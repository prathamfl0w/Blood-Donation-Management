from django.shortcuts import render, redirect
from .forms import AppointmentForm
from .models import Appointment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


# Create your views here.

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.status = 'pending'
            try:
                appointment.save()
                messages.success(request, 'Appointment booked successfully!')
                return redirect('my_appointments')
            except Exception as e:
                messages.error(request, f'Error booking appointment: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()
    
    return render(request, 'appointment/book_appointment.html', {'form': form})

@login_required
def my_appointments(request):
    user_appointments = Appointment.objects.filter(user=request.user)
    
    context = {
        'appointments': user_appointments,
        'stats': {
            'confirmed': user_appointments.filter(status='Confirmed').count(),
            'pending': user_appointments.filter(status='pending').count(),
        }
    }
    return render(request, 'appointment/my_appointments.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id, user=request.user)
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
    return redirect('my_appointments')

@login_required
def calendar_view(request):
    return render(request, 'appointment/calendar.html')

@login_required
@csrf_exempt
def appointment_events(request):
    appointments = Appointment.objects.filter(user=request.user)
    events = []
    
    for appointment in appointments:
        event = {
            'title': f'{appointment.full_name} - {appointment.type} ({appointment.status.title()})',
            'start': appointment.date.strftime('%Y-%m-%d'),
            'end': appointment.date.strftime('%Y-%m-%d'),
            'color': {
                'pending': '#FFA500',
                'confirmed': '#28a745',
                'rejected': '#dc3545'
            }.get(appointment.status, '#dc3545'),
            'allDay': True,
            'extendedProps': {
                'status': appointment.status,
                'fullName': appointment.full_name,
                'type': appointment.type,
                'time': appointment.time.strftime('%I:%M %p')
            }
        }
        events.append(event)
    
    return JsonResponse(events, safe=False)