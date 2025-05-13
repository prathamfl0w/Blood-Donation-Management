from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time', 'type', 'status', 'action_buttons']
    list_filter = ['status', 'date', 'type']
    search_fields = ['user__username', 'user__email', 'full_name']
    readonly_fields = ['created_at']
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}?action=approve&id={}">'
                '<img src="/static/admin/img/icon-yes.svg" alt="Approve">'
                '</a>&nbsp;'
                '<a class="button" href="{}?action=reject&id={}">'
                '<img src="/static/admin/img/icon-no.svg" alt="Reject">'
                '</a>',
                obj.id, obj.id, obj.id, obj.id
            )
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.status == 'confirmed' else 'red',
            obj.get_status_display()
        )
    
    action_buttons.short_description = 'Actions'
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'pending':
            return self.readonly_fields + ['status']
        return self.readonly_fields
    
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.GET and 'id' in request.GET:
            appointment_id = request.GET['id']
            try:
                appointment = self.model.objects.get(id=appointment_id)
                if request.GET['action'] == 'approve':
                    appointment.status = 'confirmed'
                    appointment.save()
                    self.message_user(request, f'Appointment for {appointment.user} has been approved.')
                elif request.GET['action'] == 'reject':
                    appointment.status = 'rejected'
                    appointment.save()
                    self.message_user(request, f'Appointment for {appointment.user} has been rejected.')
            except self.model.DoesNotExist:
                pass
        return super().changelist_view(request, extra_context)
