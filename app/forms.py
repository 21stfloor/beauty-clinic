import datetime
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from app.models import Appointment, CustomUser, Order, Purpose, Service
from crispy_forms.layout import Div
Div.template = 'bootstrap5/floating_field.html'


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'firstname', 'middlename', 'lastname')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class VerificationForm(forms.Form):
    verification_code = forms.CharField(label='Verification Code', max_length=4)

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'firstname', 'middlename', 'lastname', 'gender', 'picture', 'is_active', 'is_superuser')


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "firstname", "lastname", "gender", "phone_number", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class AppointmentForm(forms.ModelForm):
    # purpose = forms.ChoiceField(choices=Purpose.choices)
    date = forms.DateTimeField(
        input_formats=['%Y-%m-%d, %I:%M %p'],  # Format for input
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    
    class Meta:
        model = Appointment
        fields = ('date', 'service', 'payment_method', )
        exclude = ('status', )

    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),  # Assuming 'User' is your user model
        required=True  # Set 'required' to True
    )
    
class OrderForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ('id', 'product', 'price', 'discount', 'quantity')

class SalesPredictionForm(forms.Form):
    units_sold = forms.IntegerField(label='Units Sold Today')
    unit_price = forms.DecimalField(label='Unit Price Today')
    current_year = datetime.datetime.now().year
    order_year = forms.IntegerField(label='Order Year', min_value=current_year)
    order_month = forms.IntegerField(label='Order Month', min_value=1, max_value=12)
        