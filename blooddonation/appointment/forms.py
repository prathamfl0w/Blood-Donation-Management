from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }
        )
    )
    
    class Meta:
        model = Appointment
        fields = ['full_name', 'phone', 'email', 'date', 'time', 'type', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }