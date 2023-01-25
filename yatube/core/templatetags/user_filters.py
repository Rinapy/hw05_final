from django import template
from django.contrib.auth import get_user_model


register = template.Library()

User = get_user_model()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})
