from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/data/', views.appointment_events, name='calendar_events'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]
