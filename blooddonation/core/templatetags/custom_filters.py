from django import template

register = template.Library()

@register.filter
def status_color(status):
    colors = {
        'available': 'success',
        'pending': 'warning',
        'used': 'danger',
        'expired': 'secondary'
    }
    return colors.get(status.lower(), 'primary')

@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0