from django.contrib import admin
from django.utils.html import format_html
from .models import Donor, BloodRequest, CustomUser, Donation
from django.contrib.auth.admin import UserAdmin


# Register your models here.

admin.site.register(Donor)


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'blood_group', 'urgency', 'hospital_name', 'created_at', 'status', 'action_buttons']
    list_filter = ['status', 'urgency', 'blood_group', 'created_at']
    search_fields = ['contact_name', 'hospital_name', 'contact_number']
    readonly_fields = ['created_at']
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<button onclick="location.href=\'{}?action=approve&id={}\'" '
                'class="button" style="background-color: #28a745; color: white; '
                'border: none; padding: 5px 10px; margin-right: 5px; border-radius: 3px;">'
                '<i class="fas fa-check"></i> Approve</button>'
                '<button onclick="location.href=\'{}?action=reject&id={}\'" '
                'class="button" style="background-color: #dc3545; color: white; '
                'border: none; padding: 5px 10px; border-radius: 3px;">'
                '<i class="fas fa-times"></i> Reject</button>',
                obj.id, obj.id, obj.id, obj.id
            )
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.status == 'approved' else 'red',
            obj.get_status_display()
        )
    
    action_buttons.short_description = 'Actions'

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.GET and 'id' in request.GET:
            request_id = request.GET['id']
            try:
                blood_request = self.model.objects.get(id=request_id)
                if request.GET['action'] == 'approve':
                    blood_request.status = 'approved'
                    blood_request.save()
                    self.message_user(request, f'Blood request from {blood_request.contact_name} has been approved.')
                elif request.GET['action'] == 'reject':
                    blood_request.status = 'rejected'
                    blood_request.save()
                    self.message_user(request, f'Blood request from {blood_request.contact_name} has been rejected.')
            except self.model.DoesNotExist:
                pass
        return super().changelist_view(request, extra_context)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['approved', 'rejected']:
            return self.readonly_fields + ['status']
        return self.readonly_fields


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'blood_group', 'city', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone', 'city', 'blood_group')
    list_filter = ('blood_group', 'city', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "blood_group", "city", "security_question", "security_answer")
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {
            "fields": ("phone", "blood_group", "city", "security_question", "security_answer")
        }),
    )


class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'blood_group', 'amount_ml', 'date')
    list_filter = ('blood_group', 'date')
    search_fields = ('donor__username', 'blood_group')

admin.site.register(Donation, DonationAdmin)
