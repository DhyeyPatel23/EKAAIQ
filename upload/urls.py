from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('process/<int:file_id>/', views.process_file, name='process_file'),
]
