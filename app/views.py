from datetime import date
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
import random
from rest_framework.generics import ListAPIView
from django.db.models import Count
from django.db.models import F, Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.functions import ExtractMonth, TruncMonth
from itertools import product
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.utils.timezone import get_current_timezone
from datetime import datetime
from django.utils.timezone import make_aware
from app import models
from app.context_processors import SCHEDULE_DATEFORMAT
from django_tables2 import SingleTableView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.shortcuts import render, redirect
from app.context_processors import CONTEXT
from app.forms import AppointmentForm, NewUserForm, OrderForm
from app.models import Appointment, CustomUser, Customer, Gender, Order, Product, Service
from app.tables import AppointmentTable, OrderTable
from .serializers import GenderDistributionSerializer, OrderSerializer, ProductSerializer, ServiceAppointmentCountSerializer, CustomUserSerializer, CustomerImageSerializer, CustomerSerializer, ServiceSerializer
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
from calendar import month_name

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
        # user = CustomUser.objects.filter(email=self.request.user.email).first()
        form.instance.customer = self.request.user
        return super(CreateAppointmentView, self).form_valid(form)


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

# def products(request):
#     products = Product.objects.order_by('-id')
    
#     return render(request, 'pages/products.html', {"products": products})


def services(request):
    services = Service.objects.order_by('-id')
    
    return render(request, 'pages/services.html', {"services": services})

def about(request):
    return render(request, 'pages/about.html')

class OrdertListView(LoginRequiredMixin, SingleTableView):
    model = Order
    table_class = OrderTable
    template_name = 'pages/orders.html'
    per_page = 8


    def get_table_data(self):

        return Order.objects.filter(customer__email=self.request.user.email)
    
    def get_context_data(self, **kwargs):
        context = super(OrdertListView, self).get_context_data(**kwargs)
        
        context['form'] = OrderForm()
            
        return context

# def generate_random_color():
#     return f"rgba({random.randrange(0, 255)}, {random.randrange(0, 255)}, {random.randrange(0, 255)}, 1)"

   
    
class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductsAndOrderView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'pages/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.order_by('-id')

class CreateOrderAPIView(CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        product = Product.objects.filter(id=product_id).first()

        if product is None:
            return Response({'message': 'Product not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the price based on the product's price and the quantity
        price = product.price * int(quantity)

        # Create the Order object
        order_data = {
            'customer': request.user.id,
            'product': product_id,
            'quantity': quantity,
            'price': price,
            'discount': product.discount
        }

        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        success_url = reverse('orders')

        return Response({'message': 'Order created successfully'}, status=status.HTTP_302_FOUND, headers={'Location': success_url})
    

# def generate_random_hex_color(used_colors):
#     while True:
#         color = "#{:02X}{:02X}{:02X}".format(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
#         if color not in used_colors:
#             return color
        
# def generate_unique_hex_colors(num_colors):
#     used_colors = set()
#     unique_colors = []

#     while len(unique_colors) < num_colors:
#         color = generate_random_hex_color(used_colors)
#         used_colors.add(color)
#         unique_colors.append(color)

#     return unique_colors

unique_colors = [
    "#FF5733",
    "#33FF57",
    "#5733FF",
    "#33FF33",
    "#FF3357",
    "#57FF33",
    "#3357FF",
    "#FF33FF",
    "#57FF57",
    "#335733",
    "#AA5733",
    "#33AA57",
    "#5733AA",
    "#33AA33",
    "#AA3357",
    "#57AA33",
    "#3357AA",
    "#AA33AA",
    "#57AA57",
    "#3357AA"
]

class ServiceAppointmentCount(APIView):
    def get(self, request):
        queryset = (
            Appointment.objects
            .values('date', 'service__name')
            .annotate(count=Count('service'))
        )
        background_colors = list(unique_colors)

        # Group the data by service__name and create a dictionary with label, data, and random backgroundColor
        service_data = {}
        for item in queryset:
            service_name = item['service__name']
            # month = item['date__month']
            date = item['date']
            month = date.month
            count = item['count']

            if service_name not in service_data:
                # Get a random background color for the service
                random_color = random.choice(background_colors)

                service_data[service_name] = {
                    "label": service_name,
                    "data": [0] * 12,  # Initialize data array for 12 months
                    "backgroundColor": random_color,
                }
            
            if month is not None and 1 <= month <= 12:
                service_data[service_name]["data"][month - 1] = count  # Subtract 1 to align with array index

        # Convert the dictionary values to a list
        result = list(service_data.values())

        return Response(result, status=status.HTTP_200_OK)
    

class GenderDistributionView(APIView):
    def get(self, request):
        gender_data = CustomUser.objects.values('gender').annotate(count=Count('gender'))

        gender_counts = [0] * (len(Gender) + 1)  # Initialize with 0 values for all gender choices

        for entry in gender_data:
            gender = entry['gender']
            gender_counts[gender] = entry['count']

        # # Convert the list to exclude the first index (0 value)
        # gender_counts = gender_counts[1:]

        return Response(gender_counts)
    

def orders_by_product_month_ajax(request):
    current_year = date.today().year
    orders = Order.objects.filter(date__year=current_year)

    data = orders.values('product__name', 'date').annotate(quantity_sum=Sum('quantity'))

    # Initialize chart_data with default zero values for all months and products
    chart_data = {}
    for month in range(1, 13):
        for product in data.values_list('product__name', flat=True).distinct():
            if product not in chart_data:
                chart_data[product] = [0] * 12

    for entry in data:
        product_name = entry['product__name']
        d = entry['date']
        month = d.month
        current_count = chart_data[product_name][month - 1]
        quantity_sum = entry['quantity_sum']

        # Update the chart_data with the quantity_sum
        if month is not None:
            chart_data[product_name][month - 1] = quantity_sum + current_count

    labels = [datetime(current_year, month, 1).strftime('%B') if month is not None else '' for month in range(1, 13)]

    return JsonResponse({'data': chart_data, 'labels': labels})