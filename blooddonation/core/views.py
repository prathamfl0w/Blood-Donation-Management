from django.shortcuts import render, redirect
from .models import Donor, BloodRequest, CustomUser, Donation, DonorDonation
from appointment.models import Appointment 
from .forms import CustomUserRegistrationForm, CustomLoginForm, PasswordResetSecurityForm, BloodRequestForm, DonationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from datetime import datetime
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings

FLASK_API_URL = 'http://127.0.0.1:5000/api'

def home(request):
    return render(request, 'home.html')

def show_donors(request):
    donors = Donor.objects.all()
    return render(request, 'donors.html', {'donors': donors})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            # Ensure email is provided
            if not form.cleaned_data.get('email'):
                messages.error(request, 'Email is required')
                return render(request, 'register.html', {'form': form})

            # First register in Django
            user = form.save()
            
            # Then register in Flask API
            try:
                flask_data = {
                    'name': user.get_full_name() or user.username,
                    'email': user.email,  # This should now always have a value
                    'password': 'django_user_password',  # Use consistent password
                    'blood_group': user.blood_group,
                    'phone': user.phone,
                    'city': user.city,
                    'role': 'admin' if user.is_superuser else 'user'
                }
                
                response = requests.post(f'{FLASK_API_URL}/register', json=flask_data)
                
                if response.status_code == 201:
                    messages.success(request, 'Registration successful! Please login.')
                    return redirect('login')
                else:
                    # If Flask registration fails, delete Django user
                    user.delete()
                    messages.error(request, 'Registration failed. Please try again.')
            except Exception as e:
                user.delete()
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'login.html', {'form': form})

def register_flask_user(user):
    """Helper function to register user in Flask API for donations only"""
    try:
        response = requests.post(f'{FLASK_API_URL}/register', json={
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'password': 'django_user_password',
            'blood_group': getattr(user, 'blood_group', 'O+'),
            'phone': getattr(user, 'phone', '1234567890'),
            'city': getattr(user, 'city', 'Default City')
        })
        return response.status_code == 201
    except:
        return False

def get_flask_token(user):
    """Get JWT token from Flask API"""
    try:
        # Ensure user has an email
        if not user.email:
            print(f"Debug - No email for user: {user.username}")
            return None

        # First try to login with the user's credentials
        login_data = {
            'email': user.email,
            'password': 'admin123' if user.is_superuser else 'django_user_password'
        }
        
        print(f"Debug - Attempting login for: {user.email}")
        
        login_response = requests.post(
            f'{FLASK_API_URL}/login',
            json=login_data
        )
        
        print(f"Debug - Login response: {login_response.text}")

        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            if token:
                return token

        # If login fails, try to register
        if login_response.status_code == 401:
            register_data = {
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'password': 'admin123' if user.is_superuser else 'django_user_password',
                'blood_group': getattr(user, 'blood_group', 'O+'),
                'phone': getattr(user, 'phone', '1234567890'),
                'city': getattr(user, 'city', 'Default City'),
                'role': 'admin' if user.is_superuser else 'user'
            }
            
            register_response = requests.post(
                f'{FLASK_API_URL}/register',
                json=register_data
            )
            
            print(f"Debug - Register response: {register_response.text}")

            if register_response.status_code == 201:
                # Try login again after registration
                login_response = requests.post(
                    f'{FLASK_API_URL}/login',
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    return login_response.json().get('access_token')

        print(f"Debug - Authentication failed for user: {user.email}")
        return None

    except requests.RequestException as e:
        print(f"Error getting token: {str(e)}")
        return None

@login_required
def dashboard(request):
    context = {
        'blood_stats': {},
        'blood_data': [0] * 8,
        'data_source': 'Combined (Django + Flask)',
        'total_donations': 0,
        'available_units': 0,
        'available_units_ml': 0,
        'total_appointments': 0,
        'appointments_stats': {
            'pending': 0,
            'confirmed': 0,
            'cancelled': 0
        },
        'pending_requests': 0
    }

    try:
        # Get Django donations
        if request.user.is_superuser:
            django_donations = Donation.objects.all()
        else:
            django_donations = Donation.objects.filter(donor=request.user)

        # Get Flask data
        token = get_flask_token(request.user)
        if token:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            stats_response = requests.get(
                f'{FLASK_API_URL}/blood-stats',
                headers=headers,
                timeout=5
            )
            
            if stats_response.status_code == 200:
                api_data = stats_response.json()
                if api_data.get('success'):
                    flask_stats = api_data['stats']
                    
                    # Combine Django and Flask donations
                    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
                    combined_stats = {group: flask_stats.get(group, 0) for group in blood_groups}
                    
                    # Add Django donations to stats
                    for donation in django_donations:
                        if donation.blood_group in combined_stats:
                            combined_stats[donation.blood_group] += 1

                    # Calculate combined totals
                    total_donations = len(django_donations) + api_data['total_donations']
                    available_units = django_donations.filter(status='completed').count() + api_data['available_units']
                    total_ml = (django_donations.filter(status='completed').aggregate(Sum('amount_ml'))['amount_ml__sum'] or 0) + api_data['available_units_ml']

                    # Format all donations for display
                    all_donations = []
                    
                    # Add Django donations
                    for d in django_donations:
                        all_donations.append({
                            'donor_name': d.donor.username,
                            'blood_group': d.blood_group,
                            'amount_ml': d.amount_ml,
                            'donation_date': d.date.isoformat(),
                            'status': d.status,
                            'city': getattr(d.donor, 'city', 'N/A')
                        })
                    
                    # Add Flask donations
                    all_donations.extend(api_data.get('donations', []))

                    context.update({
                        'blood_stats': combined_stats,
                        'blood_data': [combined_stats[group] for group in blood_groups],
                        'total_donations': total_donations,
                        'available_units': available_units,
                        'available_units_ml': total_ml,
                        'donations': sorted(all_donations, key=lambda x: x['donation_date'], reverse=True),
                        'total_system_donations': total_donations if request.user.is_superuser else None
                    })

        # Get appointments data
        appointments = Appointment.objects.filter(user=request.user)
        context.update({
            'total_appointments': appointments.count(),
            'appointments_stats': {
                'pending': appointments.filter(status='pending').count(),
                'confirmed': appointments.filter(status='confirmed').count(),
                'cancelled': appointments.filter(status='cancelled').count()
            }
        })

        # Get blood requests data
        if request.user.is_superuser:
            pending_requests = BloodRequest.objects.filter(status='pending')
        else:
            pending_requests = BloodRequest.objects.filter(
                user=request.user,
                status='pending'
            )
        
        context.update({
            'pending_requests': pending_requests.count()
        })

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        messages.error(request, f"Could not fetch blood donation statistics: {str(e)}")

    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    return redirect('login')

def reset_password(request):
    if request.method == 'POST':
        form = PasswordResetSecurityForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            security_answer = form.cleaned_data['security_answer']
            password1 = form.cleaned_data['new_password1']
            password2 = form.cleaned_data['new_password2']

            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect('reset_password')

            if user.security_answer.strip().lower() != security_answer.strip().lower():
                messages.error(request, "Security answer is incorrect.")
                return redirect('reset_password')

            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                return redirect('reset_password')

            user.password = make_password(password1)
            user.save()
            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')
    else:
        form = PasswordResetSecurityForm()

    return render(request, 'reset_password.html', {'form': form})


@login_required
def donate_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.status = 'pending'
            donation.save()

            # Sync with Flask API
            try:
                token = get_flask_token(request.user)
                if token:
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                    
                    flask_donation_data = {
                        'donor_name': request.user.username,
                        'blood_group': donation.blood_group,
                        'amount_ml': donation.amount_ml,
                        'phone': request.user.phone,
                        'city': request.user.city,
                        'status': 'available'
                    }
                    
                    response = requests.post(
                        f'{FLASK_API_URL}/donations',
                        headers=headers,
                        json=flask_donation_data,
                        timeout=5
                    )
                    
                    if response.status_code == 201:
                        messages.success(request, 'Blood donation recorded successfully!')
                    else:
                        messages.warning(request, 'Donation recorded locally but sync with central system failed')
                
            except Exception as e:
                print(f"Error syncing donation: {str(e)}")
                messages.warning(request, 'Donation recorded but sync failed')
            
            return redirect('dashboard')
    else:
        form = DonationForm()
    
    return render(request, 'donate.html', {'form': form})

@login_required
def request_blood(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.user = request.user  # Changed from requester to user
            blood_request.save()
            messages.success(request, "Blood request submitted successfully")
            return redirect('dashboard')
    else:
        form = BloodRequestForm()
    
    # Update the filter to use user instead of requester
    user_requests = BloodRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'request_blood.html', {
        'form': form,
        'user_requests': user_requests
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        try:
            # Update basic information
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.phone = request.POST.get('phone', '')
            user.blood_group = request.POST.get('blood_group', '')
            user.city = request.POST.get('city', '')
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
        return redirect('profile')

    # Get user's donation history
    donations = Donation.objects.filter(donor=request.user).order_by('-date')
    return render(request, 'profile.html', {
        'donations': donations,
        'user': request.user
    })

@login_required
def request_history(request):
    token = get_flask_token(request.user)
    if not token:
        messages.error(request, "Authentication failed")
        return redirect('home')

    headers = {'Authorization': f'Bearer {token}'}
    context = {}

    try:
        response = requests.get(
            f'{FLASK_API_URL}/donations',
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            donations = response.json()
            context['donations'] = donations
            context['total_donations'] = len(donations)
            context['available_donations'] = len([d for d in donations if d['status'] == 'available'])
        else:
            messages.error(request, "Could not fetch donation history")
            
    except requests.RequestException as e:
        messages.error(request, f"Connection error: {str(e)}")
        
    return render(request, 'request_history.html', context)

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_donations(request):
    donations = DonorDonation.objects.all().order_by('-donation_date')  # Changed from date to donation_date
    context = {
        'donations': donations,
        'total_donations': donations.count(),
        'pending_donations': donations.filter(status='pending').count(),
        'approved_donations': donations.filter(status='approved').count()
    }
    return render(request, 'admin_donations.html', context)

@user_passes_test(is_superuser)
def admin_requests(request):
    requests = BloodRequest.objects.all().order_by('-created_at')
    context = {
        'requests': requests,
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='pending').count(),
        'urgent_requests': requests.filter(urgency__in=['high', 'critical']).count()
    }
    return render(request, 'admin_requests.html', context)

@user_passes_test(is_superuser)
def update_donation_status(request, donation_id, status):
    if request.method == 'POST':
        donation = get_object_or_404(DonorDonation, id=donation_id)
        if status in ['approved', 'rejected']:
            donation.status = status
            donation.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@user_passes_test(is_superuser)
def update_request_status(request, request_id, status):
    if request.method == 'POST':
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        if status in ['approved', 'rejected']:
            blood_request.status = status
            blood_request.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})



@api_view(['GET'])
def flask_data(request):
    try:
        res = requests.get("http://127.0.0.1:5000/api/")  # your Flask route
        return Response(res.json())
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)
