from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('create/' , create_quiz , name="ai_create")
    # path('quiz/' , quiz_view , name="ai_quiz"),
    # path('ai_select/' , ai_select , name="ai_select") ,
    # path('ai_create/' , ai_create_quiz , name="ai_create" ),
    # path('add_quiz/' , quiz_add , name="add_quiz"),
    path('upload_text/' , upload_text , name="upload_text"),
    path('edit_questions_text/' , edit_questions_text , name="edit_questions_text"),
    path('finalize_quiz/' , finalize_quiz_text, name="finalize_quiz_text"),
    path('add_question_text/' , generate_ai_questions_text , name="add_question_text"),
]

