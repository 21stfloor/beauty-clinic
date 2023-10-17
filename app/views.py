
from itertools import product
from django.views.generic.edit import CreateView
from django.utils.timezone import get_current_timezone
from datetime import datetime
from django.utils.timezone import make_aware
from app.context_processors import SCHEDULE_DATEFORMAT
from django_tables2 import SingleTableView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import render, redirect
from app.context_processors import CONTEXT
from app.forms import AppointmentForm, NewUserForm
from app.models import Appointment, CustomUser, Customer, Product, Service
from app.tables import AppointmentTable
from .serializers import CustomUserSerializer, CustomerImageSerializer, CustomerSerializer
from rest_framework import viewsets, mixins, generics
from rest_framework.decorators import api_view, action
from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404
from rest_framework import status
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from django.http import HttpResponse
from django.template import loader
from django.urls import resolve, reverse
from django.contrib import messages
from django.contrib.auth.views import LoginView
import math
import time
import os
from agora_token_builder import RtcTokenBuilder
from django.templatetags.static import static

query_watch = None

@api_view(['GET', ])
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()

        customers_serializer = CustomerSerializer(customers, many=True)
        return JsonResponse(customers_serializer.data, safe=False)




class CustomerViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class UploadCustomerImageViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Customer.objects.all()
    serializer_class = CustomerImageSerializer
    parser_classes = [MultiPartParser]


class CreateAppointmentView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'pages/appointment_form.html'

    def get_success_url(self):
        return reverse('appointment_list')
    
    def form_valid(self, form):
        user = Customer.objects.filter(email=self.request.user.email).first()
        form.instance.user = user
        return super(CreateAppointmentView, self).form_valid(form)

    # def post(self, request, *args, **kwargs):
        
    #     user = Customer.objects.filter(email=request.user.email).first()
    #     # owner = Customer.objects.filter(email=request.user.email).first()
    #     date = make_aware(datetime.strptime(
    #                 request.POST.get('date'), SCHEDULE_DATEFORMAT), timezone=get_current_timezone())
    #     Appointment.objects.create(user=user, date=date, purpose=request.POST.get('purpose'))
    #     return self.get(request, *args, **kwargs)


class AppointmentListView(LoginRequiredMixin, SingleTableView):
    model = Appointment
    table_class = AppointmentTable
    template_name = 'pages/appointment_list.html'
    per_page = 8


    def get_table_data(self):

        return Appointment.objects.filter(customer__email=self.request.user.email)
    
    def get_context_data(self, **kwargs):
        context = super(AppointmentListView, self).get_context_data(**kwargs)
        
        context['form'] = AppointmentForm()
            
        return context


@api_view(['GET', ])
def veterinary_list(request):
    if request.method == 'GET':
        veterinaries = CustomUser.objects.all()

        veterinaries_serializer = CustomUserSerializer(veterinaries, many=True)
        return JsonResponse(veterinaries_serializer.data, safe=False)


def video_call(request, message_gc_id):
    if request.user is None or request.user.is_authenticated is False:
        return redirect('admin:index')

    template = loader.get_template('pages/video_call.html')
    
    receiver_id = ''
    receiver = "Other"
    try:
        receiver_id = message_gc_id.split('-')[1]
        receiver = Customer.objects.filter(id=receiver_id).first()
    except Exception:
        pass
    #Build token with account
    expiration_time_in_seconds = 3600
    currentTimestamp = time.time()
    privilege_expired_ts = currentTimestamp + expiration_time_in_seconds;
    token = RtcTokenBuilder.buildTokenWithAccount(CONTEXT['app_id'], CONTEXT['app_certificate'], message_gc_id, request.user.id, 1, privilege_expired_ts)

    context = {
        'message_gc_id': message_gc_id,
        'receiver': receiver
        # 'token': token
    }

    return HttpResponse(template.render(context, request))


class MyLoginView(LoginView):
    # form_class=LoginForm
    redirect_authenticated_user=True
    template_name='registration/login.html'

    def get_success_url(self):
        # write your logic here
        # if self.request.user.is_superuser:
        return reverse('index')# '/progress/'
        # return '/'


def register_request(request):
    context = {}
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(email=user.email)
            login(request, user)
            return redirect("index")
        context['form_errors'] = form.errors
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    context["register_form"] = form
    return render(request=request, template_name="registration/register.html", context=context)


def index(request):
    recent_services = Service.objects.order_by('-id')[:3]
    recent_products = Product.objects.order_by('-id')[:3]
    
    context = {
        'services': recent_services,
        'products': recent_products
    }
    return render(request, 'pages/landing.html', context)

def products(request):
    products = Product.objects.order_by('-id')[:3]
    
    return render(request, 'pages/products.html', {"products": products})

def about(request):
    return render(request, 'pages/about.html')