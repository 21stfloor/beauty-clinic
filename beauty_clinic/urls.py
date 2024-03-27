"""beauty_clinic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from app import views
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.urls import re_path as url
from rest_framework import routers
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView




router = routers.DefaultRouter(trailing_slash=False)
router.register(r'customer', views.CustomerViewSet)
router.register(r'upload_customer_image', views.UploadCustomerImageViewSet)
# router.register(r'chart-data', views.ChartDataView, basename='chartdata')

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, 'app_name'), namespace='instance_name')),
    # path('chat/', views.chat_all, name='chat'),
    path('appointment/', views.CreateAppointmentView.as_view(), name='appointment'),
    path('appointment/list', views.AppointmentListView.as_view(), name='appointment_list'),
    path('accounts/login/',
        views.MyLoginView.as_view(),
        name='login',
    ),

    path(
        'accounts/logout/',
        LogoutView.as_view(),
        name='logout',
    ),
    # path('products', views.ProductsAndOrderView.as_view(), name='products'),

    path('products/', views.ProductsAndOrderView.as_view(), name='products'),
    path('checkout-history/', views.checkout_page, name='checkout_history'),
    path('checkout/', views.checkout, name='checkout'),
    path('resend-verification/', views.resend_verification_code, name='resend_verification'),
    path('predict_sales/', views.predict_sales, name='predict_sales'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('visualizeDataset/', views.visualizeDataset , name='visualizeDataset'),

    # URL pattern for creating an order
    path('create-order/', views.CreateOrderAPIView.as_view(), name='create_order'),

    path('services', views.services, name='services'),
    path('orders', views.OrdertListView.as_view(), name='orders'),
    path('about', views.about, name='about'),
    path("accounts/register", views.register_request, name="register"),
    path('verify/', views.verification_page, name='verification_page'),
    path('video_call/<str:message_gc_id>/',
         views.video_call, name='video-call'),
    # path('chat/<str:message_gc_id>/', views.chat),
    url(r'^api/customerlist', views.customer_list),
    url(r'^api/veterinarylist', views.veterinary_list),
    url(r'^chaining/', include('smart_selects.urls')),

    path('chart-data/', views.ServiceAppointmentCount.as_view(), name='chart-data'),
    path('gender-data/', views.GenderDistributionView.as_view(), name='gender-data'),
    path('service/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('get-order-data/', views.orders_by_product_month_ajax, name='get_order_data'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
