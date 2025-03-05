from django.urls import path
from . import views
# from django.conf import settings
# from django.conf.urls.static import static


urlpatterns = [
    path('create_enhanced/', views.create_quiz_enhanced, name='create_quiz'),
    # path('create/', views.create_quiz, name='create_quiz'),
    path('join/<str:code>/', views.join_quiz, name='join_quiz'),
    path('result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('view/<int:quiz_id>/', views.quiz_view, name='quiz_view'),
    # path('quiz/<int:quiz_id>/results/', views.view_quiz_results, name='view_quiz_results'),
    path('join_room/' , views.join_room , name="join_room") ,
    path('quiz/delete/<int:pk>/', views.delete_quiz, name='delete_quiz'),
    path('q/view_questions/<int:quiz_id>/', views.view_questions, name='view_questions'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('verify-otp/', views.verify_otp_room , name='verify_otp_room'),
    path('result/<int:result_id>/view_answers/', views.view_student_answers, name='view_student_answers'),
    path('quiz/<int:quiz_id>/update-settings/', views.update_quiz_settings, name='update_quiz_settings'),
    
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('edit_questions/', views.edit_questions, name='edit_questions'),  # Edit AI-generated questions
    path('finalize_quiz/', views.finalize_quiz, name='finalize_quiz'), 
    path('generate_ai_questions/', views.generate_ai_questions, name='generate_ai_questions'),
] 