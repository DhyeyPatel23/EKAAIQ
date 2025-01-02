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
from django.db.models import Avg, F  # Add this import at the top of the file


@login_required
def create_quiz(request):
    if not request.user.is_teacher:
        return HttpResponseForbidden("You are not allowed to access this page.")
    if request.method == 'POST':
        title = request.POST.get('title')
        show_results_to_student = request.POST.get('show_results_to_student') == 'on'  # Checkbox for showing results
        duration = request.POST.get('duration')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox for active status

        questions = request.POST.getlist('questions')
        options = request.POST.getlist('options')
        correct_options = request.POST.getlist('correct_options')
        images = request.FILES.getlist('images')

        quiz = Quiz.objects.create(
            title=title, 
            host=request.user,
            show_results_to_student=show_results_to_student,
            duration=duration,
            is_active=is_active
        )
        
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

                # Check if the quiz is active
                if not quiz.is_active:
                    return render(request, 'room.html', {'error': 'Room is not active.'})

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
    total = quiz.questions.count()

    # Calculate percentage
    percentage = round((quiz_result.score / total * 100), 1) if total > 0 else 0

    # Get all the answers related to this quiz result
    student_answers = StudentAnswer.objects.filter(quiz_result=quiz_result)
    detailed_results = []

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

    return render(request, 'view_answers.html', {
        'quiz': quiz,
        'student': student,
        'result': quiz_result,
        'total': total,
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

        # Print the data to check if it's being received
        print(f"Received Duration: {duration}")
        print(f"Show Results: {show_results}")
        print(f"Is Active: {is_active}")

        # Update the quiz settings
        quiz.duration = duration
        quiz.show_results_to_student = show_results
        quiz.is_active = is_active

        # Print the current quiz object before saving
        print(f"Quiz before save: {quiz}")

        quiz.save()  # Save changes to the database

        # Print confirmation after saving
        print("Quiz settings updated and saved.")

        return redirect('view_questions', quiz_id=quiz.id)  # Redirect back to the questions page

    return render(request, 'view_questions.html', {'quiz': quiz , 'total_questions': total_questions,})


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