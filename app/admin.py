from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
# Register your models here.
from django.apps import apps
from app.forms import UserChangeForm, UserCreationForm
from django import forms
from app.models import (Appointment, CustomUser, Customer, Order, Product, Purpose, Service, Status,)
from django.contrib.auth.models import Group, User
from admin_interface.admin import Theme
from django.utils.html import format_html
# admin.site.unregister((Theme, Group))

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'category', 'price', 'thumb')

    def thumb(self, obj):
        return format_html("<img src='{}'  width='48' height='48' />".format(obj.thumbnail.url))
    thumb.allow_tags = True
    thumb.__name__ = 'Thumbnail'
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'thumb')

    def thumb(self, obj):
        return format_html("<img src='{}'  width='48' height='48' />".format(obj.thumbnail.url))
    thumb.allow_tags = True
    thumb.__name__ = 'Thumbnail'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display =('customer', 'product', 'date', 'price', 'quantity', 'discount')

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    readonly_fields = ('last_login', 'date_joined')
    form = UserChangeForm
    add_form = UserCreationForm

       # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'firstname', 'lastname', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'picture')}),
        ('Personal info', {'fields': ('firstname', 'middlename', 'lastname')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'middlename', 'lastname', 'picture', 'is_staff', 'is_superuser', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'service', 'status')


# @admin.register(DeviceToken)
# class DeviceTokenAdmin(admin.ModelAdmin):
#     pass

# Replace your_app_name it is just a placeholder
app_config = apps.get_app_config('app')
models = app_config.get_models()


# for model in models:
#     try:
#         admin.site.register(model)
#     except admin.sites.AlreadyRegistered: 
#         pass 

admin.site.unregister((         Group ))


admin.site.site_header = "Web based Beauty Clinic Appointment"
admin.site.site_title = "Web based Beauty Clinic"
admin.site.index_title = ""
