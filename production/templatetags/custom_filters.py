from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    try:
        return f"{float(value):.2f} €"
    except (ValueError, TypeError):
        return value

@register.filter(name='status_badge')
def status_badge(status):
    badges = {
        'pending': 'bg-warning text-dark',
        'in_production': 'bg-info',
        'ready': 'bg-success',
        'completed': 'bg-success',
        'cancelled': 'bg-danger',
    }
    return badges.get(status, 'bg-secondary')


@register.filter(name='format_dimensions')
def format_dimensions(width, height):
    try:
        return f"{int(width)} × {int(height)} мм"
    except (ValueError, TypeError):
        return f"{width} × {height}"


