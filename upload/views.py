from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UploadedFile
from q.models import Quiz, Question
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        file_instance = UploadedFile.objects.create(user=request.user, file=uploaded_file)
        return redirect('process_file', file_id=file_instance.id)
    return render(request, 'upload_file.html')

@login_required
def process_file(request, file_id):
    file_instance = UploadedFile.objects.get(id=file_id)
    file_path = file_instance.file.path

    try:
        logger.info(f"Processing file: {file_path}")

        # Read the Excel file using openpyxl engine
        df = pd.read_excel(file_path, engine='openpyxl')
        logger.info("Excel file read successfully")

        # Create a new quiz
        quiz = Quiz.objects.create(
            title="Uploaded Quiz",
            host=request.user,
            show_results_to_student=True,
            duration=10,
            is_active=True
        )
        logger.info(f"Quiz created: {quiz.id}")

        # Iterate through the DataFrame and create questions
        for index, row in df.iterrows():
            question_type = row['QuestionType']
            points = row['Points']
            image = row['Image'] if isinstance(row['Image'], str) else None

            logger.info(f"Processing row {index}: {row}")

            if question_type == 'MCQ':
                Question.objects.create(
                    quiz=quiz,
                    question_text=row['Question'],
                    question_type='MCQ',
                    option1=row['Option1'],
                    option2=row['Option2'],
                    option3=row['Option3'],
                    option4=row['Option4'],
                    correct_option=row['CorrectOption'],
                    points=points,
                    images=image
                )
                logger.info(f"MCQ question created with {points} points")
            elif question_type == 'MCA':
                correct_options = row['CorrectOption'].split(',')
                Question.objects.create(
                    quiz=quiz,
                    question_text=row['Question'],
                    question_type='MCA',
                    option1=row['Option1'],
                    option2=row['Option2'],
                    option3=row['Option3'],
                    option4=row['Option4'],
                    correct_option=','.join(correct_options),
                    points=points,
                    images=image
                )
                logger.info(f"MCA question created with {points} points")
            elif question_type == 'TF':
                Question.objects.create(
                    quiz=quiz,
                    question_text=row['Question'],
                    question_type='TF',
                    option1='True',
                    option2='False',
                    correct_option=row['CorrectOption'],
                    points=points,
                    images=image
                )
                logger.info(f"TF question created with {points} points")

        return redirect('quiz_detail', quiz_id=quiz.id)
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        return render(request, 'error.html', {'message': 'There was an error processing the file. Please ensure it is in the correct format.'})
