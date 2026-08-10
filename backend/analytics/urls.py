from django.urls import path
from .views import KPIsView

app_name = 'analytics'

urlpatterns = [
    path('kpis/', KPIsView.as_view(), name='kpis'),
]