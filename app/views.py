from datetime import date
from django.conf import settings
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
from app.models import Appointment, CheckoutHistory, CustomUser, Customer, Gender, Order, Product, Service
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
import random
from django.shortcuts import render, redirect
from .forms import SalesPredictionForm, VerificationForm
from django.core.mail import send_mail
from django.contrib.sessions.models import Session
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
import pickle
import pandas as pd
from datetime import timedelta
from .models import SalesData
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import mysql.connector

query_watch = None
from django.contrib.auth.decorators import login_required
@api_view(['GET', ])
def customer_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()

        customers_serializer = CustomerSerializer(customers, many=True)
        return JsonResponse(customers_serializer.data, safe=False)


class CheckoutHistoryView(ListView):
    model = Order
    template_name = 'pages/checkOut.html'
    context_object_name = 'checkout-history'

    def get_queryset(self):
        return Order.objects.filter(customer__email=self.request.user.email)


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
    redirect_authenticated_user = True
    template_name = 'registration/login.html'

    def form_valid(self, form):
        # Proceed with regular login
        response = super().form_valid(form)

        # Check if the user is authenticated and store email in the session if not verified
        if self.request.user.is_authenticated and not self.request.user.is_verified:
            user_email = self.request.user.email
            self.request.session['user_email'] = user_email  # Store user email in the session

        return response

    def get_success_url(self):
        if self.request.user.is_authenticated and self.request.user.is_verified:
            return reverse('index')  # Redirect to index page after successful login and verification
        else:
            # Redirect to some other page if needed for unverified users
            return reverse('verification_page')


def register_request(request):
    context = {}
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True # Activate the user by default
            user.is_verified = False
            user.save()

            # Generate a random 4-digit code
            verification_code = f"{random.randint(1000, 9999)}"
            print(f"Verification Code for {user.email}: {verification_code}")
            request.session['verification_code'] = verification_code

            # Store the user email in the session
            request.session['user_email'] = user.email  # Store the user email in the session

            # Send the verification code to the user's email
            send_mail(
                'Verification Code',
                f'Your verification code is: {verification_code}',
                'beautyskincarec@gmail.com',  # Replace with your sender email address
                [user.email],  # Send to the newly created user's email
                fail_silently=False,
            )

            # Redirect to the verification page where the user will input the code
            return redirect("verification_page")
        context['form_errors'] = form.errors
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    context["register_form"] = form
    return render(request=request, template_name="registration/register.html", context=context)


def verification_page(request):
    user_email = request.session.get('user_email')  # Retrieve user email from the session
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['verification_code']

            # Retrieve the stored verification code from the session
            stored_code = request.session.get('verification_code')

            # Compare entered_code with the stored verification code
            if entered_code == stored_code:
                # Verification successful
                # Update user verification status to True
                try:
                    user = CustomUser.objects.get(email=user_email)
                    user.is_verified = True
                    user.save()
                    return redirect("index")
                except CustomUser.DoesNotExist:
                    # Handle case where user with provided email does not exist
                    pass
            else:
                # Invalid verification code
                # Display error message and redirect back to verification page
                messages.error(request, "Invalid verification code. Please try again.")
                return redirect("verification_page")
    else:
        form = VerificationForm()
    return render(request, 'registration/verification.html', {'verification_form': form, 'user_email': user_email})

def resend_verification_code(request):
    user_email = request.session.get('user_email')  # Retrieve user email from the session
    verification_code = f"{random.randint(1000, 9999)}"
    print(f"New Verification Code for {user_email}: {verification_code}")
    request.session['verification_code'] = verification_code

    # Send the new verification code to the user's email
    send_mail(
                'New Verification Code',
                f'Your new verification code is: {verification_code}',
                'beautyskincarec@gmail.com',  # Replace with your sender email address
                [user_email],  # Send to the newly created user's email
                fail_silently=False,
            )

    return JsonResponse({'message': 'Verification code resent successfully'})


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


class OrdertListView(ListView):
    model = Order
    template_name = 'pages/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer__email=self.request.user.email, ordered=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orders = self.get_queryset()
        total_price = orders.aggregate(total_price=Sum('price'))['total_price'] or 0
        total_discount = orders.aggregate(total_discount=Sum('discount'))['total_discount'] or 0
        total_quantity = orders.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

        context['total_price'] = total_price
        context['total_discount'] = total_discount
        context['total_quantity'] = total_quantity

        return context


def checkout(request):
    # Get products in the cart for the current user
    customer = request.user
    cart_items = Order.objects.filter(customer=customer, ordered=False)

    total_price = 0
    total_discount = 0  # Calculate discount logic
    total_quantity = 0

    # Calculate total price and quantity for the items in the cart
    for item in cart_items:
        total_price += item.product.price * item.quantity
        total_quantity += item.quantity

        # Update the product stock after checkout
        product = item.product
        product.stock -= item.quantity
        item.ordered = True
        item.save()
        product.save()

    # Create a record in CheckoutHistory for the current checkout
    new_checkout = CheckoutHistory.objects.create(
        user=request.user,
        total_price=total_price,
        date_of_checkout=timezone.now(),
        discount=total_discount,
        total_quantity=total_quantity,
        # Add other fields as needed
    )


    # cart_items.delete()  # Remove the products from the cart after checkout
    checkout_history_data = CheckoutHistory.objects.filter(id=new_checkout.id)

    if checkout_history_data.exists():
        # Pass checkout history data to the template
        return render(request, 'pages/checkOut.html', {'checkout_history_data': checkout_history_data})
    else:
        # Redirect to a success page if there's no checkout history data
        return redirect('success_page')

def delete_order(request, order_id):
    # Assuming 'order_id' is passed in the URL or as a parameter

    try:
        order_to_delete = Order.objects.get(id=order_id)
        order_to_delete.delete()
        # Optionally, perform additional actions after deletion if needed

        return redirect('orders')  # Redirect to a success page after deletion

    except Order.DoesNotExist:
        # Handle the case where the order with the provided ID does not exist
        return HttpResponse("Order does not exist", status=404)


def checkout_page(request):
    # Fetch all CheckoutHistory data for the logged-in user
    checkout_history_data = CheckoutHistory.objects.filter(user=request.user)
    # Pass checkout_history to the template
    return render(request, 'pages/checkOut.html', {'checkout_history_data': checkout_history_data})

# class OrdertListView(ListView):
#     model = Order
#     template_name = 'pages/orders.html'
#     context_object_name = 'orders'

#     def get_queryset(self):
#         return Order.objects.filter(customer__email=self.request.user.email)

# # def generate_random_color():
# #     return f"rgba({random.randrange(0, 255)}, {random.randrange(0, 255)}, {random.randrange(0, 255)}, 1)"

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductsAndOrderView(LoginRequiredMixin, ListView):
    model = Product  # Specifies the model for this view
    template_name = 'pages/products.html'  # Specifies the template to be used
    context_object_name = 'products'  # Specifies the context variable name in the template

    def get_queryset(self):
        # Returns a queryset of Product objects ordered by their IDs in descending order
        return Product.objects.order_by('-id')

class CreateOrderAPIView(CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 0))
        product = Product.objects.filter(id=product_id).first()

        # Calculate the price based on the product's price and the quantity
        price = product.price * int(quantity)

        # Create the Order object
        order_data = {
            'customer': request.user.id,
            'product': product_id,
            'quantity': quantity,
            'stock': product.stock,
            'price': price,
            'discount': product.discount,
            'ordered': False
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


def predict_sales_new(request):
    # Fetch data from the Order model
    orders = Order.objects.filter(ordered=True)

    # Check if there are any orders
    if not orders:
        return render(request, 'admin/prediction_page.html', {'annual_sales_data': '[]', 'future_sales': '[]'})

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(list(orders.values('date', 'price')))

    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Extract year from 'date' and group by year
    df['Year'] = df['date'].dt.year

    # Drop rows with missing values
    df = df.dropna()

    yearly_data = df.groupby('Year').agg({'price': 'mean'}).reset_index()
    yearly_data.rename(columns={'price': 'Total_Revenue'}, inplace=True)

    # Convert data and future_sales to JSON
    yearly_data_json = yearly_data.to_json(orient='records', date_format='iso')  # Include date_format parameter

    # Extract features and target variable
    X = np.array([(year - df['Year'].min()) for year in yearly_data['Year']])
    y = np.array(yearly_data['Total_Revenue'], dtype=float)

    # Perform manual linear regression
    X_mean = np.mean(X)
    y_mean = np.mean(y)

    m = np.sum((X - X_mean) * (y - y_mean)) / np.sum((X - X_mean)**2)
    b = y_mean - m * X_mean

    # Predict future sales
    future_years = range(int(df['Year'].max()) + 1, int(df['Year'].max()) + 6)
    future_sales = []

    for year in future_years:
        days_since_min_year = year - df['Year'].min()
        prediction = m * days_since_min_year + b
        future_sales.append({'year': year, 'sales': prediction})

    future_sales_json = json.dumps(future_sales)

    return render(request, 'admin/prediction_page.html', {'annual_sales_data': yearly_data_json, 'future_sales': future_sales_json})

def predict_sales(request):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='beauty-clinic'
    )

    cursor = connection.cursor()

    # Fetch data from the 'dataset' table
    cursor.execute('SELECT Order_Date, Total_Revenue FROM `dataset`')

    data = cursor.fetchall()

    # Close the connection
    connection.close()

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=['Order_Date', 'Total_Revenue'])

    # Convert 'Order_Date' to datetime
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce', format='%m/%d/%Y')  # Adjust the format as needed

    # Extract year from 'Order_Date' and group by year
    df['Year'] = df['Order_Date'].dt.year

    # Convert 'Total_Revenue' to numeric
    df['Total_Revenue'] = pd.to_numeric(df['Total_Revenue'], errors='coerce')

    # Drop rows with missing values
    df = df.dropna()

    yearly_data = df.groupby('Year').agg({'Total_Revenue': 'mean'}).reset_index()

    # Convert data and future_sales to JSON
    yearly_data_json = yearly_data.to_json(orient='records', date_format='iso')  # Include date_format parameter

    # Extract features and target variable
    X = np.array([(year - df['Year'].min()) for year in yearly_data['Year']])
    y = np.array(yearly_data['Total_Revenue'], dtype=float)

    # Perform manual linear regression
    X_mean = np.mean(X)
    y_mean = np.mean(y)

    m = np.sum((X - X_mean) * (y - y_mean)) / np.sum((X - X_mean)**2)
    b = y_mean - m * X_mean

    # Predict future sales
    future_years = range(int(df['Year'].max()) + 1, int(df['Year'].max()) + 6)
    future_sales = []

    for year in future_years:
        days_since_min_year = year - df['Year'].min()
        prediction = m * days_since_min_year + b
        future_sales.append({'year': year, 'sales': prediction})

    future_sales_json = json.dumps(future_sales)

    return render(request, 'admin/prediction_page.html', {'annual_sales_data': yearly_data_json, 'future_sales': future_sales_json})


from django.http import JsonResponse


def visualizeDataset(request):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='beauty-clinic'
    )

        # Create a cursor
        cursor = connection.cursor()

        # Fetch data from the 'dataset' table
        cursor.execute('SELECT CAST(YEAR(STR_TO_DATE(`Order_Date`, "%m/%d/%Y")) AS UNSIGNED) as Order_Year, Product, SUM(CAST(`Units_Sold` AS DECIMAL(10,2))) as Total_Units_Sold FROM `dataset` GROUP BY Order_Year, `Product`')

        data = cursor.fetchall()

        # Close the connection
        connection.close()

        # Prepare data for visualization
        data_per_year = {}
        for row in data:
            order_year = row[0]
            product_name = row[1]  # Renamed to avoid conflict
            units_sold = row[2]

            if order_year not in data_per_year:
                data_per_year[order_year] = []

            data_per_year[order_year].append({'units_sold': units_sold, 'product': product_name})

        # Check if the result set is empty before responding
        if not data_per_year:
            return JsonResponse({'detail': 'No data available'}, status=204)

        return JsonResponse({'data': data_per_year}, status=200)

    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)
