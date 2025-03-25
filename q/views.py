from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse , HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render
import re
import os
# import fitz  # PyMuPDF
import PyPDF2
import ollama
import json
from django.utils import timezone
from datetime import datetime
from .utils import check_quiz_status
from .ai import get_generated_quiz , generate_question
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, F, Sum  # Add this import at the top of the file

# def extract_text_from_pdf(pdf_path):
#     """Extract text from a PDF file"""
#     document = fitz.open(pdf_path)
#     text = ""
#     for page_num in range(document.page_count):
#         page = document.load_page(page_num)
#         text += page.get_text()
def extract_text_from_pdf(pdf_path):
    """Extract text from the uploaded PDF file."""
    text = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# def generate_mcqs_with_ollama(text):
    """Generate MCQs using Ollama and return JSON"""
    prompt = f"""
    Generate 10 multiple-choice questions in JSON format from the following text:
    
    {text}
    
    Ensure each question has:
    - 4 options
    - The correct answer should be mentioned as (option1, option2, option3, or option4)
    - JSON format strictly as shown below:
    
    {{
        "mcqs": [
            {{
                "question": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Rome"],
                "correct_answer": "option1"
            }},
            {{
                "question": "What is the capital of India?",
                "options": ["Gujarat", "Mumbai", "Dehli", "Kashmir"],
                "correct_answer": "option3"
            }},
            {{
                "question": "What is the capital of Australia?",
                "options": ["Paris", "London", "Berlin", "Canberra"],
                "correct_answer": "option4"
            }},
            ...
        ]
    }}

    generate 10 mcq in such way .
    """
    
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response["message"]["content"])["mcqs"]
    except json.JSONDecodeError:
        return []  # Return empty list if parsing fails

def generate_mcqs_with_ollama(text):
    """Generate MCQs using Ollama and return JSON"""

    # prompt = f"""
    # Generate a JSON object containing exactly 10 multiple-choice questions about Python programming. Format:

    # {
    # "mcqs": [
    #     {
    #     "question": "QUESTION_TEXT",
    #     "options": ["OPTION1", "OPTION2", "OPTION3", "OPTION4"],
    #     "correct_answer": "optionX"
    #     }
    # ]
    # }

    # Requirements:
    # - Exactly 10 questions
    # - Each question must have exactly 4 options
    # - Correct answer format must be "option1", "option2", "option3", or "option4"
    # - Output only the JSON object with no additional text"""
    prompt = f"""
    Generate 10 multiple-choice questions in JSON format from the following text:
    
    {text}
    
    Ensure each question has:
    - 4 options
    - The correct answer should be mentioned as (option1, option2, option3, or option4)
    - make sure to open and close the brackets properly.
    - JSON format strictly as shown below:
    
    {{
        "mcqs": [
            {{
                "question": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Rome"],
                "correct_answer": "option1"
            }},
            {{
                "question": "What is the capital of India?",
                "options": ["Gujarat", "Mumbai", "Delhi", "Kashmir"],
                "correct_answer": "option3"
            }},
            {{
                "question": "What is the capital of Australia?",
                "options": ["Paris", "London", "Berlin", "Canberra"],
                "correct_answer": "option4"
            }}
        ]
    }}

    Generate 10 MCQs in this exact format.
    make sure to open and close the brackets properly.
    """

    # don't add anything like "Here are 10 MCQs in JSON format:" in the starting of the prompt directly start with "mcqs" json .
    # Call Ollama API
    # response = ollama.chat(
    #     # model="mistral",
    #     model="llama3.2",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system", 
                "content": "You are a JSON generator. Respond only with valid JSON following the specified schema. Do not include any explanatory text, markdown formatting, or additional content."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )
    # Debugging: Print the raw response
    print("Raw Response:", response)

    try:
        # Extract the message content
        response_content = response.get("message", {}).get("content", "")
        # response_content = response_content.split("\n", 1)[1]  
        # response_content = "\n".join(response_content.split("\n")[1:])
        # print("Extracted Content:", response_content)

        json_start = response_content.find("{")
        json_end = response_content.rfind("}") + 1
        cleaned_json = response_content[json_start:json_end]

        print("Extracted Content:", cleaned_json)

        # Try parsing the response as JSON
        parsed_json = json.loads(cleaned_json)

        # Ensure "mcqs" exists in the parsed data
        return parsed_json.get("mcqs", [])
    
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return []



@login_required
def upload_pdf(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Quiz')
        start_time_str = request.POST.get('start_time' , None)
        end_time_str = request.POST.get('end_time', None)
        show_results_to_student = request.POST.get('show_results_to_student') == 'on'
        duration = int(request.POST.get('duration', 2))  # Ensure it's an integer
        count = int(request.POST.get('count'))  # Ensure it's an integer
        request.session['offset'] = count
        is_active = request.POST.get('is_active') == 'on'
        pdf_file = request.FILES.get('pdf')

        if pdf_file:
            pdf_path = f"media/pdfs/{pdf_file.name}"
            with open(pdf_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Extract text and generate MCQs
            pdf_text = extract_text_from_pdf(pdf_path)
            request.session['pdf_text'] = pdf_text
            ai_mcqs = get_generated_quiz(pdf_text , count)

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

            return redirect('edit_questions')  # Redirect to the question edit page

    return render(request, "upload.html")

@login_required
def edit_questions(request):
    quiz_data = request.session.get('quiz_data', {})

    if not quiz_data:
        return redirect('upload_pdf')  # Redirect if no quiz data found

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

        return redirect('finalize_quiz')  # Redirect to finalize and save in DB

    return render(request, "pdf_edit_page.html", {"questions": quiz_data.get('questions', [])})

@login_required
def finalize_quiz(request):
    quiz_data = request.session.get('quiz_data', {})

    if not quiz_data:
        return redirect('upload_pdf')
    
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
            option1=mcq["options"][0],
            option2=mcq["options"][1],
            option3=mcq["options"][2],
            option4=mcq["options"][3],
            correct_option=mcq["correct_answer"]
        )

    # Clear session data
    del request.session['quiz_data']

    return redirect('quiz_detail', quiz_id=quiz.id)  # Redirect to quiz details page

@require_http_methods(["POST"])
def generate_ai_questions(request):
    try:
        text = request.session.get('pdf_text', '')
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


@login_required
def create_quiz(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == 'POST':
        title = request.POST.get('title')
        show_results_to_student = request.POST.get('show_results_to_student') == 'on'  # Checkbox for showing results
        duration = request.POST.get('duration')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox for active status
        pdf_file = request.FILES.get('pdf')  # Get uploaded PDF

        # questions = request.POST.getlist('questions')
        # options = request.POST.getlist('options')
        # correct_options = request.POST.getlist('correct_options')
        # images = request.FILES.getlist('images')

        quiz = Quiz.objects.create(
            title=title, 
            host=request.user,
            show_results_to_student=show_results_to_student,
            duration=duration,
            is_active=is_active
        )
        
        if pdf_file:
            # Save the PDF
            pdf_path = f"media/pdfs/{pdf_file.name}"
            with open(pdf_path, "wb") as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)

            # Extract text and generate MCQs
            pdf_text = extract_text_from_pdf(pdf_path)
            ai_mcqs = generate_mcqs_with_ollama(pdf_text)

            # Store AI-generated MCQs in the database
            for mcq in ai_mcqs:
                question_text = mcq.get("question")
                options = mcq.get("options", ["", "", "", ""])
                correct_answer = mcq.get("correct_answer")

                if len(options) == 4:
                    correct_option_index = options.index(correct_answer) + 1  # Convert to 1-based index
                    Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        option1=options[0],
                        option2=options[1],
                        option3=options[2],
                        option4=options[3],
                        correct_option=correct_option_index
                    )

            return redirect('quiz_detail', quiz_id=quiz.id)

        else:
            # Manual question entry
            questions = request.POST.getlist('questions')
            options = request.POST.getlist('options')
            correct_options = request.POST.getlist('correct_options')
            images = request.FILES.getlist('images')

            for i in range(len(questions)):
                image_file = images[i] if i < len(images) else None

                Question.objects.create(
                    quiz=quiz,
                    question_text=questions[i],
                    option1=options[i * 4],
                    option2=options[i * 4 + 1],
                    option3=options[i * 4 + 2],
                    option4=options[i * 4 + 3],
                    correct_option=correct_options[i],
                    images=image_file
                )

        return redirect('quiz_detail', quiz_id=quiz.id)

    return render(request, 'quiz-v2.html')



@login_required
def join_quiz(request, code):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, code=code)
    
    # Check if the student has already submitted the quiz
    if QuizResult.objects.filter(quiz=quiz, user=request.user).exists():
        return render(request, 'error.html', {'message': 'You have already submitted this quiz.'})
    
    if request.method == 'POST':
        score = 0
        total_points = 0
        user_answers = {}
        questions = quiz.questions.all()
        
        for question in questions:
            total_points += question.points
            
            if question.question_type == 'MCQ':
                user_answer = request.POST.get(f'answers_{question.id}')
                user_answers[question.id] = user_answer
                if user_answer and user_answer == question.correct_option:
                    score += question.points
                    
            elif question.question_type == 'MCA':
                user_answer = request.POST.getlist(f'answers_{question.id}[]')
                user_answers[question.id] = user_answer
                correct_options = question.correct_option.split(',')
                if set(user_answer) == set(correct_options):
                    score += question.points
                    
            elif question.question_type == 'TF':
                user_answer = request.POST.get(f'answers_{question.id}')
                user_answers[question.id] = user_answer
                if user_answer and user_answer == question.correct_option:
                    score += question.points

        # Calculate percentage
        percentage = (score / total_points * 100) if total_points > 0 else 0

        # Store the quiz result
        quiz_result = QuizResult.objects.create(
            quiz=quiz,
            user=request.user,
            score=score,
            total_points=total_points,
            percentage=percentage
        )

        # Store individual answers
        for question in questions:
            user_answer = user_answers.get(question.id, '')
            if isinstance(user_answer, list):
                user_answer = ','.join(user_answer)
                
            StudentAnswer.objects.create(
                quiz_result=quiz_result,
                question=question,
                user_answer=user_answer,
                correct_answer=question.correct_option
            )
        
        return redirect('quiz_result', quiz_id=quiz.id)
    
    return render(request, 'join_quiz.html', {'quiz': quiz})

@login_required
def quiz_result(request, quiz_id):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    quiz_result = QuizResult.objects.filter(
        quiz=quiz,
        user=request.user
    ).order_by('-submitted_at').first()

    if not quiz_result:
        return redirect('join_quiz', code=quiz.code)

    student_answers = StudentAnswer.objects.filter(quiz_result=quiz_result)
    
    questions_data = []
    total_score = 0
    max_possible_score = 0
    
    for question in quiz.questions.all():
        student_answer = student_answers.filter(question=question).first()
        
        # Create a mapping of option values to actual option text
        option_mapping = {
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4
        }
        
        # Convert option values to actual text for user answers
        user_answer_list = []
        if student_answer and student_answer.user_answer:
            if question.question_type == 'MCA':
                user_answer_values = student_answer.user_answer.split(',')
                user_answer_list = [option_mapping.get(value, value) for value in user_answer_values]
            else:
                user_answer_list = [option_mapping.get(student_answer.user_answer, student_answer.user_answer)]

        # Convert option values to actual text for correct answers
        correct_answer_list = []
        if question.correct_option:
            if question.question_type == 'MCA':
                correct_values = question.correct_option.split(',')
                correct_answer_list = [option_mapping.get(value, value) for value in correct_values]
            else:
                correct_answer_list = [option_mapping.get(question.correct_option, question.correct_option)]

        question_data = {
            'text': question.question_text,
            'type': question.question_type,
            'points': question.points,
            'image': question.images.url if question.images else None,
            'options': [
                question.option1,
                question.option2,
                question.option3,
                question.option4
            ],
            'user_answer_list': user_answer_list,
            'correct_answer_list': correct_answer_list,
            'is_correct': False
        }

        # Calculate if answer is correct based on question type
        if student_answer:
            if question.question_type == 'MCQ' or question.question_type == 'TF':
                question_data['is_correct'] = student_answer.user_answer == question.correct_option
            elif question.question_type == 'MCA':
                user_answers = set(student_answer.user_answer.split(','))
                correct_answers = set(question.correct_option.split(','))
                question_data['is_correct'] = user_answers == correct_answers

            if question_data['is_correct']:
                total_score += question.points

        max_possible_score += question.points
        questions_data.append(question_data)

    percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0

    context = {
        'quiz': quiz,
        'questions': questions_data,
        'total_score': total_score,
        'max_score': max_possible_score,
        'percentage': round(percentage, 2),
        'show_results': quiz.show_results_to_student,
        'quiz_result': quiz_result
    }

    return render(request, 'quiz_result.html', context)



@login_required
def view_questions(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_questions = questions.count()

    return render(request, 'view_questions.html', {
        'quiz': quiz,
        'total_questions': total_questions,
    })



@login_required
def quiz_detail(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    results = QuizResult.objects.filter(quiz=quiz).select_related('user').order_by('-submitted_at')
    
    # Calculate quiz statistics
    total_attempts = results.count()
    avg_score = results.aggregate(Avg('percentage'))['percentage__avg'] or 0
    
    context = {
        'quiz': quiz,
        'results': results,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 2),
    }
    return render(request, 'quiz_detail_v2.html', context)

@login_required
def view_quiz_results(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Ensure that only the quiz creator can view the results
    if request.user != quiz.host:
        return HttpResponseForbidden("You are not allowed to view these results.")
    
    results = quiz.results.all().order_by('-score', 'submitted_at')
    
    return render(request, 'view_quiz_results.html', {'quiz': quiz, 'results': results})




# @login_required
# def join_room(request):
#     if not request.user.is_student:
#         return HttpResponseForbidden("You are not allowed to access this page.")
#     if request.method == 'POST':
#         room_code = request.POST.get('room_code')
#         if room_code:
#             # Validate that the room code contains only digits
#             if not re.match(r'^\d+$', room_code):
#                 return render(request, 'room.html', {'error': 'Invalid room code. Only numbers are allowed.'})

#             # Check if the room code exists in the Quiz model
#             try:
#                 quiz = Quiz.objects.get(code=room_code)

#                 # Check if the quiz is active
#                 if not quiz.is_active:
#                     return render(request, 'room.html', {'error': 'Room is not active.'})

#                 # Generate a 6-digit OTP
#                 otp = random.randint(100000, 999999)

#                 # Save the OTP and room code in the session for later verification
#                 request.session['otp'] = otp
#                 request.session['room_code'] = room_code

#                 # Send OTP via email
#                 user_email = request.user.email
#                 send_mail(
#                     'Your OTP for Quiz Room',
#                     f'Your OTP is {otp}. Please use this to join the quiz.',
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_email],
#                     fail_silently=False,
#                 )

#                 # Redirect to OTP verification page
#                 return redirect('verify_otp_room')

#             except Quiz.DoesNotExist:
#                 # If the room code does not exist, show an error
#                 return render(request, 'room.html', {'error': 'Room not found.'})

#     return render(request, 'room.html')

@login_required
def join_room(request):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == 'POST':
        room_code = request.POST.get('room_code')
        if room_code:
            # Validate that the room code contains only digits
            if not re.match(r'^\d+$', room_code):
                return render(request, 'room.html', {'error': 'Invalid room code. Only numbers are allowed.'})

            # Check if the room code exists in the Quiz model
            try:
                quiz = Quiz.objects.get(code=room_code)
                quiz_status = check_quiz_status(quiz.start_time, quiz.end_time)

                # print("start time : " , quiz.start_time)

                local_time = timezone.localtime(quiz.start_time)

                # print("start time : " , local_time)

                time_12hr = local_time.strftime("%I:%M %p")

                # Check if the quiz is active
                if not quiz.is_active:
                    return render(request, 'room.html', {'error': 'Room is not currently active.'})

                if quiz_status == "upcoming":
                    return render(request, 'room.html', {'error': f'Room will start at {time_12hr} .'})
                elif quiz_status == "expired":
                    return render(request, 'room.html', {'error': 'Room is already expired.'})


                # Generate a 6-digit OTP
                otp = random.randint(100000, 999999)

                # Save the OTP and room code in the session for later verification
                request.session['otp'] = otp
                request.session['room_code'] = room_code

                # Send OTP via email
                user_email = request.user.email
                send_mail(
                    'Your OTP for Quiz Room',
                    f'Your OTP is {otp}. Please use this to join the quiz.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user_email],
                    fail_silently=False,
                )

                # Redirect to OTP verification page
                return redirect('verify_otp_room')

            except Quiz.DoesNotExist:
                # If the room code does not exist, show an error
                return render(request, 'room.html', {'error': 'Room not found.'})

    return render(request, 'room.html')


@login_required
def verify_otp_room(request):
    if not request.user.is_student:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        stored_otp = request.session.get('otp')
        room_code = request.session.get('room_code')
        
        if str(entered_otp) == str(stored_otp):
            # Check if the OTP has already been used
            if 'used_otps' not in request.session:
                request.session['used_otps'] = []
            
            if entered_otp in request.session['used_otps']:
                return render(request, 'verify_otp.html', {'error': 'OTP has already been used. Please request a new one.'})
            
            # Mark the OTP as used
            request.session['used_otps'].append(entered_otp)
            return redirect('join_quiz', code=room_code)
        else:
            return render(request, 'verify_otp.html', {'error': 'Invalid OTP. Please try again.'})
    
    return render(request, 'verify_otp.html')
# @login_required
# def verify_otp_room(request):
#     if not request.user.is_student:
#         return HttpResponseForbidden("You are not allowed to access this page.")
#     if request.method == 'POST':
#         entered_otp = request.POST.get('otp')
        
#         stored_otp = request.session.get('otp')
#         room_code = request.session.get('room_code')
        
#         if str(entered_otp) == str(stored_otp):
#             return redirect('join_quiz', code=room_code)
#         else:
#             return render(request, 'verify_otp.html', {'error': 'Invalid OTP. Please try again.'})
    
#     return render(request, 'verify_otp.html')

@login_required
def delete_quiz(request, pk):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.method == "POST":
        quiz.delete()
        return redirect('teacher_home') 
    return render(request, 'delete_confirm.html', {'object': quiz, 'type': 'quiz'})

@login_required
def quiz_view(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_questions = questions.count()
    results = quiz.results.all()

    # Calculate correct attempts for each result
    for result in results:
        correct_attempts = StudentAnswer.objects.filter(
            quiz_result=result,
            user_answer=F('correct_answer')
        ).count()
        result.correct_attempts = correct_attempts

    return render(request, 'view.html', {
        'quiz': quiz ,
        'results': results,
        'total_questions': total_questions,
        })


def edit_question(request, question_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    # Fetch the question object using the provided question_id
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        # Manually update each field of the question from the POST data
        question.question_text = request.POST.get('question_text', question.question_text)
        question.option1 = request.POST.get('option1', question.option1)
        question.option2 = request.POST.get('option2', question.option2)
        question.option3 = request.POST.get('option3', question.option3)
        question.option4 = request.POST.get('option4', question.option4)
        question.correct_option = request.POST.get('correct_option', question.correct_option)

        # Handle image deletion if checkbox is checked
        if 'delete_image' in request.POST and request.POST['delete_image'] == 'on':
            if question.images:
                question.images.delete()  # Deletes the current image file
            question.images = None  # Set the field to None

        # Handle the image file upload
        if 'image' in request.FILES:
            if question.images:  # Delete the old image if a new one is being uploaded
                question.images.delete()
            question.images = request.FILES['image']

        question.save()

        # Redirect to the quiz detail page or wherever you want after editing
        return redirect('view_questions' , quiz_id=question.quiz.id)  # Adjust the redirect as needed

    # Render the edit question page with the question details for GET request
    return render(request, 'edit_question.html', {'question': question})

def delete_question(request, question_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    # Fetch the question object using the provided question_id
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id  # Store the quiz id for redirection after deletion

    # Delete the question and its associated image if any
    if question.images:
        question.images.delete()
    question.delete()

    # Redirect back to the view_questions page for the quiz
    return redirect('view_questions', quiz_id=quiz_id)

def add_question(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        correct_option = request.POST.get('correct_option')
        
        # Handle file upload
        image = request.FILES.get('image')
        
        # Create a new question
        Question.objects.create(
            quiz=quiz,
            question_text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option,
            images=image
        )
        
        messages.success(request, 'Question added successfully!')
        return redirect('view_questions', quiz_id=quiz_id)
    
    return render(request, 'add_question.html', {'quiz': quiz})







@login_required
def view_student_answers(request, result_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz_result = get_object_or_404(QuizResult, id=result_id)
    quiz = quiz_result.quiz
    student = quiz_result.user
    total_points = quiz.questions.aggregate(total_points=Sum('points'))['total_points'] or 0

    # Get all the answers related to this quiz result
    student_answers = StudentAnswer.objects.filter(quiz_result=quiz_result)
    detailed_results = []
    total_score = 0

    for answer in student_answers:
        # Create option mapping
        option_mapping = {
            'option1': answer.question.option1,
            'option2': answer.question.option2,
            'option3': answer.question.option3,
            'option4': answer.question.option4
        }

        # Convert option values to actual text
        user_answer = answer.user_answer
        correct_answer = answer.correct_answer

        # For MCA questions, convert to list
        if answer.question.question_type == 'MCA':
            user_answer = answer.user_answer.split(',') if answer.user_answer else []
            correct_answer = answer.correct_answer.split(',')

        # Convert option values to actual text
        if answer.question.question_type in ['MCQ', 'MCA']:
            if isinstance(user_answer, list):
                user_answer = [option_mapping.get(opt, opt) for opt in user_answer]
            else:
                user_answer = option_mapping.get(user_answer, user_answer)
            
            if isinstance(correct_answer, list):
                correct_answer = [option_mapping.get(opt, opt) for opt in correct_answer]
            else:
                correct_answer = option_mapping.get(correct_answer, correct_answer)

        is_correct = user_answer == correct_answer
        if is_correct:
            total_score += answer.question.points

        detailed_results.append({
            'question': answer.question.question_text,
            'question_type': answer.question.question_type,
            'img': answer.question.images,
            'img_loc': answer.question.image_loc,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'options': option_mapping,
            'is_correct': is_correct,
            'points': answer.question.points
        })

    # Calculate percentage
    percentage = round((total_score / total_points * 100), 1) if total_points > 0 else 0

    return render(request, 'view_answers.html', {
        'quiz': quiz,
        'student': student,
        'result': quiz_result,
        'total': total_points,
        'percentage': percentage,
        'detailed_results': detailed_results
    })






@login_required
def update_quiz_settings(request, quiz_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    total_questions = questions.count()

    if request.method == 'POST':
        # Get the data from the POST request
        duration = request.POST.get('duration')
        show_results = request.POST.get('show_results_to_student') == 'True'
        is_active = request.POST.get('is_active') == 'True'
        start = request.POST.get('start_time', "").strip()
        end = request.POST.get('end_time' , "").strip()

        # Print the data to check if it's being received
        print(f"Received Duration: {duration}")
        print(f"Show Results: {show_results}")
        print(f"Is Active: {is_active}")

        # Update the quiz settings
        quiz.duration = duration
        quiz.show_results_to_student = show_results
        quiz.is_active = is_active

        if start :
            quiz.start_time = start
        else : 
            quiz.start_time = None

        if end :
            quiz.end_time = end
        else : 
            quiz.end_time = None


        # Print the current quiz object before saving
        print(f"Quiz before save: {quiz}")

        quiz.save()  # Save changes to the database

        # Print confirmation after saving
        print("Quiz settings updated and saved.")

        return redirect('view_questions', quiz_id=quiz.id)  # Redirect back to the questions page

    return render(request, 'view_questions.html', {'quiz': quiz , 'total_questions': total_questions,})


@login_required
def create_quiz_enhanced(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == 'POST':
        try:
            # Debug print
            print("Form data:", request.POST)
            print("Files:", request.FILES)

            title = request.POST.get('title')
            show_results_to_student = request.POST.get('show_results_to_student') == 'on'
            duration = request.POST.get('duration')
            is_active = request.POST.get('is_active') == 'on'

            # Create the quiz
            quiz = Quiz.objects.create(
                title=title,
                host=request.user,
                show_results_to_student=show_results_to_student,
                duration=duration,
                is_active=is_active
            )

            # Process questions
            question_texts = request.POST.getlist('questions[]')
            question_types = request.POST.getlist('question_types[]')
            
            print(f"Found {len(question_texts)} questions")  # Debug print
            
            for i in range(len(question_texts)):
                question_type = question_types[i]
                image = request.FILES.get(f'images_{i}')
                points = request.POST.get(f'points_{i}', 1)

                print(f"Processing question {i + 1}, type: {question_type}")  # Debug print

                if question_type == 'MCQ':
                    # Get individual options
                    option1 = request.POST.get(f'option1_{i}')
                    option2 = request.POST.get(f'option2_{i}')
                    option3 = request.POST.get(f'option3_{i}')
                    option4 = request.POST.get(f'option4_{i}')
                    correct_option = request.POST.get(f'correct_option_{i}')
                    
                    print(f"MCQ Options: {option1}, {option2}, {option3}, {option4}")  # Debug print
                    
                    Question.objects.create(
                        quiz=quiz,
                        question_text=question_texts[i],
                        question_type='MCQ',
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        correct_option=correct_option,
                        images=image,
                        points=points
                    )
                
                elif question_type == 'MCA':
                    # Get individual options
                    option1 = request.POST.get(f'option1_{i}')
                    option2 = request.POST.get(f'option2_{i}')
                    option3 = request.POST.get(f'option3_{i}')
                    option4 = request.POST.get(f'option4_{i}')
                    correct_options = request.POST.getlist(f'correct_options_{i}[]')
                    
                    print(f"MCA Options: {option1}, {option2}, {option3}, {option4}")  # Debug print
                    print(f"Correct options: {correct_options}")  # Debug print
                    
                    Question.objects.create(
                        quiz=quiz,
                        question_text=question_texts[i],
                        question_type='MCA',
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        correct_option=','.join(correct_options),
                        images=image,
                        points=points
                    )
                
                elif question_type == 'TF':
                    correct_answer = request.POST.get(f'correct_tf_{i}')
                    
                    print(f"TF Correct answer: {correct_answer}")  # Debug print
                    
                    Question.objects.create(
                        quiz=quiz,
                        question_text=question_texts[i],
                        question_type='TF',
                        option1='True',
                        option2='False',
                        correct_option=correct_answer,
                        images=image,
                        points=points
                    )

            return redirect('quiz_detail', quiz_id=quiz.id)
        
        except Exception as e:
            print(f"Error creating quiz: {str(e)}")
            import traceback
            traceback.print_exc()  # This will print the full traceback
            return render(request, 'quiz_enhanced.html', {'error': str(e)})

    return render(request, 'quiz_enhanced.html')

@login_required
def view_answers(request, result_id):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    quiz_result = get_object_or_404(QuizResult, id=result_id)
    student_answers = StudentAnswer.objects.filter(quiz_result=quiz_result)
    
    detailed_results = []
    total_points = 0
    
    for answer in student_answers:
        # Create option mapping
        option_mapping = {
            'option1': answer.question.option1,
            'option2': answer.question.option2,
            'option3': answer.question.option3,
            'option4': answer.question.option4
        }

        # Convert option values to actual text
        user_answer = answer.user_answer
        correct_answer = answer.correct_answer

        # For MCA questions, convert to list
        if answer.question.question_type == 'MCA':
            user_answer = answer.user_answer.split(',') if answer.user_answer else []
            correct_answer = answer.correct_answer.split(',')
        
        # Convert option values to actual text
        if answer.question.question_type in ['MCQ', 'MCA']:
            if isinstance(user_answer, list):
                user_answer = [option_mapping.get(opt, opt) for opt in user_answer]
            else:
                user_answer = option_mapping.get(user_answer, user_answer)
            
            if isinstance(correct_answer, list):
                correct_answer = [option_mapping.get(opt, opt) for opt in correct_answer]
            else:
                correct_answer = option_mapping.get(correct_answer, correct_answer)

        detailed_results.append({
            'question': answer.question.question_text,
            'question_type': answer.question.question_type,
            'img': answer.question.images,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'options': option_mapping,
            'is_correct': user_answer == correct_answer,
            'points': answer.question.points
        })

    context = {
        'quiz': quiz_result.quiz,
        'student': quiz_result.user,
        'result': quiz_result,
        'detailed_results': detailed_results,
        'total': sum(q.points for q in quiz_result.quiz.questions.all())
    }
    
    return render(request, 'view_answers.html', context)

###########################################################################################################

# @login_required
# def view_student_answers(request, result_id):
#     quiz_result = get_object_or_404(QuizResult, id=result_id)
#     student_answers = quiz_result.answers.all()

#     return render(request, 'view_answers.html', {
#         'quiz_result': quiz_result,
#         'student_answers': student_answers,
#     })

############################################################################################################

# @login_required
# def create_quiz(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         questions = request.POST.getlist('questions')
#         options = request.POST.getlist('options')
#         correct_options = request.POST.getlist('correct_options')
#         quiz = Quiz.objects.create(title=title, host=request.user)
        
#         for i in range(len(questions)):
#             Question.objects.create(
#                 quiz=quiz,
#                 question_text=questions[i],
#                 option1=options[i*4],
#                 option2=options[i*4 + 1],
#                 option3=options[i*4 + 2],
#                 option4=options[i*4 + 3],
#                 correct_option=correct_options[i]
#             )
        
#         return redirect('quiz_detail', quiz_id=quiz.id)

#     return render(request, 'quiz-v2.html')

#################################################################################################################try


# @login_required
# def create_quiz(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         questions = request.POST.getlist('questions')
#         options = request.POST.getlist('options')
#         correct_options = request.POST.getlist('correct_options')
#         images = request.FILES.getlist('images')  # Get list of uploaded image files

#         print("Images received:", images)

#         quiz = Quiz.objects.create(title=title, host=request.user)
        
#         for i in range(len(questions)):
#             # Handle image file saving
#             # image_file = images[i] if len(images) > i else None
#             # image_path = None
            
#             # if image_file:
#             #     # fs = FileSystemStorage(location=os.path.join('static', 'questions'))  # Define storage location
#             #     # image_path = fs.save(image_file.name, image_file)  # Save image file
#             #     fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'questions'))  # Save images in MEDIA_ROOT
#             #     image_path = fs.save(image_file.name, image_file)

#             image_file = images[i] if i < len(images) else None

#             # Create Question object
#             Question.objects.create(
#                 quiz=quiz,
#                 question_text=questions[i],
#                 option1=options[i * 4],
#                 option2=options[i * 4 + 1],
#                 option3=options[i * 4 + 2],
#                 option4=options[i * 4 + 3],
#                 correct_option=correct_options[i],
#                 images=image_file  # Save the path to the image field
#             )

        
#         return redirect('quiz_detail', quiz_id=quiz.id)

#     return render(request, 'quiz-v2.html')






#################################################################################################################

# def join_quiz(request, code):
#     quiz = get_object_or_404(Quiz, code=code)
    
#     if request.method == 'POST':
#         user_answers = request.POST.getlist('answers')
#         score = 0
#         for i, question in enumerate(quiz.questions.all()):
#             if question.correct_option == user_answers[i]:
#                 score += 1
        
#         QuizResult.objects.create(quiz=quiz, user=request.user, score=score)
        
#         return redirect('quiz_result', quiz_id=quiz.id)
    
#     return render(request, 'join_quiz.html', {'quiz': quiz})

# @login_required
# def join_quiz(request, code):
#     quiz = get_object_or_404(Quiz, code=code)
#     questions = quiz.questions.all()

#     if request.method == 'POST':
#         score = 0
#         for question in questions:
#             selected_option = request.POST.get(str(question.id))  # Get selected option for this question
#             if selected_option and selected_option == question.correct_option:
#                 score += 1

#         # Save the score to the database, or pass it to the template
#         # For simplicity, we're just returning the score here
#         return render(request, 'quiz_result.html', {'quiz': quiz.id, 'score': score})

#     return render(request, 'join_quiz.html', {'quiz': quiz, 'questions': questions})


# @login_required
# def join_quiz(request, code):
    # quiz = get_object_or_404(Quiz, code=code)
    
    # if request.method == 'POST':
    #     # user_answers = request.POST.getlist('answers')
    #     user_answer = request.POST.get(f'answers_{question.id}')
    #     score = 0
        
    #     # Make sure the length of user answers matches the number of questions
    #     questions = quiz.questions.all()
        
    #     for i, question in enumerate(questions):
    #         try:
    #             if question.correct_option == user_answers[i]:
    #                 score += 1
    #         except IndexError:
    #             # Handle the case where there are fewer answers than questions
    #             continue
        
    #     # Store the quiz result for the user
    #     QuizResult.objects.create(quiz=quiz, user=request.user, score=score)
        
    #     return redirect('quiz_result', quiz_id=quiz.id)
    
    # return render(request, 'join_quiz.html', {'quiz': quiz})







    ########################################################################################################


# dev
# def edit_question(request, question_id):
#     # Fetch the question object using the provided question_id
#     question = get_object_or_404(Question, id=question_id)
    
#     if request.method == 'POST':
#         # Manually update each field of the question from the POST data
#         question.question_text = request.POST.get('question_text', question.question_text)
#         question.option1 = request.POST.get('option1', question.option1)
#         question.option2 = request.POST.get('option2', question.option2)
#         question.option3 = request.POST.get('option3', question.option3)
#         question.option4 = request.POST.get('option4', question.option4)
#         question.correct_option = request.POST.get('correct_option', question.correct_option)
#         question.save()

#         # Redirect to the quiz detail page or wherever you want after editing
#         return redirect('view_questions' , quiz_id=question.quiz.id)  # Adjust the redirect as needed

#     # Render the edit question page with the question details for GET request
#     return render(request, 'edit_question.html', {'question': question})

##############################################################################################









############################################################################################################

# @login_required
# def quiz_result(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     score = request.session.get('score')
#     total = request.session.get('total_questions')
#     user_answers = request.session.get('user_answers', {})
    
#     questions = quiz.questions.all()
#     detailed_results = []

#     for question in questions:
#         correct_answer = question.correct_option
#         user_answer = user_answers.get(str(question.id))
        
#         detailed_results.append({
#             'question': question.question_text,
#             'img' : question.images,
#             'img_loc' : question.image_loc,
#             'user_answer': user_answer,
#             'correct_answer': correct_answer,
#             'options': {
#                 'option1': question.option1,
#                 'option2': question.option2,
#                 'option3': question.option3,
#                 'option4': question.option4,
#             },
#             # 'image_url': question.images.url if question.images else None,
#         })

#     html_content = render_to_string('result.html', context={
#         'quiz': quiz,
#         'score': score,
#         'total': total,
#         'detailed_results': detailed_results , 
#         'email' : True
#     }, request=request)

#     recipient_email = request.user.email
#     subject = 'Your Quiz Result for ' + quiz.title
    
#     send_mail(
#         subject=subject,
#         message='Something went wrong',  # Fallback plain-text message
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[recipient_email],
#         html_message=html_content,  # The HTML content of the page
#         fail_silently=False,
#     )

#     return render(request, 'result.html', {
#         'quiz': quiz,
#         'score': score,
#         'total': total,
#         'detailed_results': detailed_results , 
#     })

############################################################################################################
# @login_required
# def quiz_result(request, quiz_id):
#     quiz = get_object_or_404(Quiz, id=quiz_id)
#     # results = quiz.results.all()

#     # score = request.session.pop('score', None)
#     score = request.session.get('score')
#     total = request.session.get('total_questions')

#     return render(request, 'result.html', {'quiz': quiz, 'score': score, 'total': total})



########################################################################################################


# @login_required
# def join_room(request):
#     return render(request, 'room.html')


# def join_room(request):
#     if request.method == 'POST':
#         room_code = request.POST.get('room_code')
#         if room_code:
#             # Check if the room code exists in the QuizRoom model
#             if Quiz.objects.filter(code=room_code).exists():
#                 return redirect('join_quiz', code=room_code)
#             else:
#                 # If the room code does not exist, show an error
#                 return render(request, 'room.html', {'error': 'Room not found.'})
#     return render(request, 'room.html')

# @login_required
# def join_room(request):
#     if request.method == 'POST':
#         room_code = request.POST.get('room_code')
#         if room_code:
#             # Validate that the room code contains only digits
#             if not re.match(r'^\d+$', room_code):
#                 return render(request, 'room.html', {'error': 'Invalid room code. Only numbers are allowed.'})

#             # Check if the room code exists in the Quiz model
#             if Quiz.objects.filter(code=room_code).exists():
#                 return redirect('join_quiz', code=room_code)
#             else:
#                 # If the room code does not exist, show an error
#                 return render(request, 'room.html', {'error': 'Room not found.'})
#     return render(request, 'room.html')

# def join_room(request):
#     if request.method == 'POST':
#         room_code = request.POST.get('room_code')
#         if room_code:
#             # Validate that the room code contains only digits
#             if not re.match(r'^\d+$', room_code):
#                 return render(request, 'room.html', {'error': 'Invalid room code. Only numbers are allowed.'})

#             # Check if the room code exists in the Quiz model
#             if Quiz.objects.filter(code=room_code).exists():
#                 # Generate a 6-digit OTP
#                 otp = random.randint(100000, 999999)
                
#                 # Save the OTP and room code in the session for later verification
#                 request.session['otp'] = otp
#                 request.session['room_code'] = room_code
                
#                 # Send OTP via email (you can modify this to use SMS if needed)
#                 user_email = request.user.email
#                 send_mail(
#                     'Your OTP for Quiz Room',
#                     f'Your OTP is {otp}. Please use this to join the quiz.',
#                     settings.DEFAULT_FROM_EMAIL,
#                     [user_email],
#                     fail_silently=False,
#                 )
                
#                 # Redirect to OTP verification page
#                 return redirect('verify_otp_room')
#             else:
#                 # If the room code does not exist, show an error
#                 return render(request, 'room.html', {'error': 'Room not found.'})
#     return render(request, 'room.html')
