from django.shortcuts import render, redirect
from .models import *
from .utils import *
import random
from django.http import HttpResponseBadRequest, JsonResponse

def quiz_view(request):
    if 'quiz_questions' in request.session:
        quiz_questions = request.session['quiz_questions']
    else:
        level = request.session.get('level')
        subject = request.session.get('subject')
        num_questions = request.session.get('num_questions')

        if subject == "python":
            if level == "beginner":
                all_questions = python_easy()
            elif level == "intermediate":
                all_questions = python_inter()
            elif level == "advance":
                all_questions = python_adv()
        elif subject == "java":
            if level == "beginner":
                all_questions = java_easy()
            elif level == "intermediate":
                all_questions = java_inter()
            elif level == "advance":
                all_questions = java_adv()
        elif subject == "c":
            if level == "beginner":
                all_questions = c_easy()
            elif level == "intermediate":
                all_questions = c_inter()
            elif level == "advance":
                all_questions = c_adv()

        request.session['all_questions'] = all_questions
        quiz_questions = random.sample(all_questions, num_questions)
        request.session['quiz_questions'] = quiz_questions

    context = {
        'questions': quiz_questions
    }
    return render(request, 'ai-show.html', context)

def ai_select(request):
    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']

    if request.method == 'POST':
        subject = request.POST.get('subject')
        request.session['subject'] = str(subject)
        level = request.POST.get('level')
        request.session['level'] = str(level)
        num_questions = request.POST.get('num')
        if num_questions:
            try:
                num_questions = int(num_questions)
                request.session['num_questions'] = num_questions
                return redirect('ai_quiz')
            except ValueError:
                return HttpResponseBadRequest("Invalid number of questions")
        else:
            return HttpResponseBadRequest("Number of questions not provided")

    return render(request, 'ai-generated.html')

def ai_create_quiz(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        show_results_to_student = request.POST.get('show_results_to_student') == 'on'
        duration = request.POST.get('duration')
        is_active = request.POST.get('is_active') == 'on'
        
        questions = request.POST.getlist('questions')
        options = request.POST.getlist('options')
        correct_options = request.POST.getlist('correct_options')
        image_loc = request.POST.getlist('img')

        filtered_questions = []
        filtered_options = []
        filtered_correct_options = []
        filtered_image_loc = []

        for i in range(len(questions)):
            if questions[i].strip():
                filtered_questions.append(questions[i])
                filtered_correct_options.append(correct_options[i])
                filtered_options.extend(options[i * 4:(i + 1) * 4])
                if image_loc:
                    filtered_image_loc.append(image_loc[i] if i < len(image_loc) else None)

        num_questions = len(filtered_questions)
        expected_options_length = num_questions * 4

        if len(filtered_options) != expected_options_length:
            return HttpResponseBadRequest("Mismatch in the number of options after filtering.")

        if len(filtered_correct_options) != num_questions:
            return HttpResponseBadRequest("Mismatch in the number of correct options after filtering.")

        if len(filtered_image_loc) != num_questions:
            return HttpResponseBadRequest("Mismatch in the number of images after filtering.")

        quiz = Quiz.objects.create(
            title=title, 
            host=request.user,
            show_results_to_student=show_results_to_student,
            duration=duration,
            is_active=is_active
        )

        for i in range(num_questions):
            Question.objects.create(
                quiz=quiz,
                question_text=filtered_questions[i],
                option1=filtered_options[i * 4],
                option2=filtered_options[i * 4 + 1],
                option3=filtered_options[i * 4 + 2],
                option4=filtered_options[i * 4 + 3],
                correct_option=filtered_correct_options[i],
                images=filtered_image_loc[i] if filtered_image_loc else None
            )

        return redirect('quiz_detail', quiz_id=quiz.id)

    return HttpResponseBadRequest("Invalid request method.")

def quiz_add(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        level = request.session.get('level')
        subject = request.session.get('subject')
        num_questions = 1 

        all_questions = request.session.get('all_questions')

        add_questions = random.sample(all_questions, num_questions)
        request.session['add_questions'] = add_questions

        data = {
            'questions': add_questions
        }
        return JsonResponse(data)

    return HttpResponseBadRequest('Invalid request')

def remove_quiz_question(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        question_text = request.POST.get('question')
        quiz_questions = request.session.get('quiz_questions', [])
        
        updated_questions = [q for q in quiz_questions if q['question'] != question_text]
        request.session['quiz_questions'] = updated_questions
        
        return JsonResponse({'status': 'success'})
    return HttpResponseBadRequest('Invalid request')
