from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('create/' , create_quiz , name="ai_create")
    path('quiz/' , quiz_view , name="ai_quiz"),
    path('ai_select/' , ai_select , name="ai_select") ,
    path('ai_create/' , ai_create_quiz , name="ai_create" ),
    path('add_quiz/' , quiz_add , name="add_quiz"),
]

