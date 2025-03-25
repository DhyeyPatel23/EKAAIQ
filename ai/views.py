from django.shortcuts import render, redirect
from .models import *
from .utils import *
import random
from django.http import HttpResponseBadRequest, JsonResponse
from .ai import *
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.utils import timezone


@login_required
def upload_text(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Quiz')
        start_time_str = request.POST.get('start_time' , None)
        end_time_str = request.POST.get('end_time', None)
        show_results_to_student = request.POST.get('show_results_to_student') == 'on'
        duration = int(request.POST.get('duration', 2))  # Ensure it's an integer
        count = int(request.POST.get('count'))  # Ensure it's an integer
        request.session['offset'] = count
        prompt = request.POST.get('prompt')
        is_active = request.POST.get('is_active') == 'on'
  
        request.session['ai_text'] = prompt
        ai_mcqs = get_generated_quiz(prompt , count)

        # Store questions in session before finalizing the quiz
        request.session['quiz_data'] = {
            'title': title,
            'start_time': start_time_str,
            'end_time': end_time_str,
            'show_results_to_student': show_results_to_student,
            'duration': duration,
            'is_active': is_active,
            'questions': ai_mcqs,
        }

        return redirect('edit_questions_text')  # Redirect to the question edit page

    return render(request, "upload_ai.html")

@login_required
def edit_questions_text(request):
    quiz_data = request.session.get('quiz_data', {})

    if not quiz_data:
        print("No quiz data found")
        return redirect('upload_text')  # Redirect if no quiz data found

    if request.method == 'POST':
        # Retrieve edited questions from the form
        updated_questions = []
        questions = request.POST.getlist('questions')
        options_list = request.POST.getlist('options')
        correct_answers = request.POST.getlist('correct_options')

        for i in range(len(questions)):
            updated_questions.append({
                "question": questions[i],
                "options": options_list[i * 4: (i + 1) * 4],  # Slice options into groups of 4
                "correct_answer": correct_answers[i]
            })

        # Update session with modified questions
        quiz_data['questions'] = updated_questions
        request.session['quiz_data'] = quiz_data

        return redirect('finalize_quiz_text')  # Redirect to finalize and save in DB

    return render(request, "edit_questions.html", {"questions": quiz_data.get('questions', [])})

@login_required
def finalize_quiz_text(request):
    quiz_data = request.session.get('quiz_data', {})

    if not quiz_data:
        return redirect('upload_text')
    

    try:
        start = timezone.make_aware(datetime.strptime(quiz_data['start_time'], "%Y-%m-%dT%H:%M"), timezone.get_current_timezone())
        end = timezone.make_aware(datetime.strptime(quiz_data['end_time'], "%Y-%m-%dT%H:%M"), timezone.get_current_timezone())

    except ValueError:
        start = None
        end = None
    
    # Create the Quiz
    quiz = Quiz.objects.create(
        title=quiz_data['title'],
        host=request.user,
        start_time=start,
        end_time=end,
        show_results_to_student=quiz_data['show_results_to_student'],
        duration=quiz_data['duration'],
        is_active=quiz_data['is_active']
    )

    # Save Questions
    for mcq in quiz_data['questions']:
        Question.objects.create(
            quiz=quiz,
            question_text=mcq["question"],
            question_type='MCQ',
            option1=mcq["options"][0],
            option2=mcq["options"][1],
            option3=mcq["options"][2],
            option4=mcq["options"][3],
            correct_option=mcq["correct_answer"],
            points=1
        )

    # Clear session data
    del request.session['quiz_data']

    return redirect('quiz_detail', quiz_id=quiz.id)  # Redirect to quiz details page

@require_http_methods(["POST"])
def generate_ai_questions_text(request):
    try:
        text = request.session.get('ai_text', '')
        count = 1
        offset = int(request.session.get('offset'))
        print("offset :" , offset)
        questions = generate_question(text=text, offset=offset ,  count=count)
        request.session['offset'] = offset + 1

        print("Questions:", questions)
        return JsonResponse({
            'success': True,
            'questions': questions
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)