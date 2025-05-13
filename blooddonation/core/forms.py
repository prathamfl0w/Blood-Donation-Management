# core/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import BloodRequest, CustomUser, Donation


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'blood_group', 'urgency', 'hospital_name', 'hospital_address',
            'contact_name', 'contact_number', 'additional_notes'
        ]
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'blood_group', 'city', 'password1', 'password2', 'security_question', 'security_answer']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })


class PasswordResetSecurityForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    security_question = forms.ChoiceField(
        choices=[
            ('', 'Select your security question'),
            ('What was your first pet name?', 'What was your first pet name?'),
            ('What is your mother maiden name?', 'What is your mother maiden name?'),
            ('What city were you born in?', 'What city were you born in?'),
            ('What is your favorite book?', 'What is your favorite book?'),
            ('What was your first school name?', 'What was your first school name?')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_security_question'
        })
    )
    security_answer = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['blood_group', 'amount_ml']
        widgets = {
            'blood_group': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'amount_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 450,
                'min': 350,
                'max': 550,
                'required': True
            })
        }




