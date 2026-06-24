from django.urls import path
from .views import WiderrufCreateView

urlpatterns = [
    path('widerruf/', WiderrufCreateView.as_view(), name='widerruf-create'),
]