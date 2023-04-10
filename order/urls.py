from django.urls import path

from .views import start_order , stripe_webhook

urlpatterns = [
    path('start_order/', start_order, name='start_order'),
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),
]