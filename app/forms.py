from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from app.models import Appointment, CustomUser, Purpose
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


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'firstname', 'middlename', 'lastname', 'picture', 'is_active', 'is_superuser')


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class AppointmentForm(forms.ModelForm):
    # purpose = forms.ChoiceField(choices=Purpose.choices)
    
    class Meta:
        model = Appointment
        fields = ('date', 'service', 'payment_method', )
        exclude = ('date', 'status')
        # widgets = {
        #     'godparents': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        #     'date_of_death': forms.DateInput(format='%d/%m/%Y')
        # }

    # def __init__(self, *args, **kwargs):
    #     super(AppointmentForm, self).__init__(*args, **kwargs)
    #     wedding_fields = ('name_of_husband', 'name_of_wife', 'name_of_officer', 'name_of_first_witness', 'name_of_second_witness', 'husband_birth_certificate', 'wife_birth_certificate')
        
    #     self.fields['number_of_attendees'].label = "Estimated number of attendees"

    #     for field in wedding_fields:
    #         self.fields[field].widget.attrs.update({
    #             'data-purpose_type': 'Wedding'
    #         })

    #     baptism_fields = ('fathers_full_name', 'mothers_full_name', 'address', 'godparents')
    #     for field in baptism_fields:
    #         self.fields[field].widget.attrs.update({
    #             'data-purpose_type': 'Baptism'
    #         })

    #     funeral_fields = ('deceased_full_name', 'age', 'date_of_death', 'place_of_burial_cemetery', 'death_certificate', 'gift_bearers_for_the_offering', 'prelude_music', 'placement_of_the_pall',
    #                       'entrance_hymn', 'opening_collect', 'first_reading', 'responsorial_psalm', 'text_of_response', 'second_reading', )
    #     for field in funeral_fields:
    #         self.fields[field].widget.attrs.update({
    #             'data-purpose_type': 'Funeral'
    #         })
        
    
    # def __init__(self, owner=None, **kwargs):
    #     super(AppointmentForm, self).__init__(**kwargs)
    #     if owner:
    #         self.fields['pet'].queryset = Pet.objects.filter(owner__email=owner.email)