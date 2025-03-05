from django.db import models
import uuid
import random
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from login.models import *
# from django.utils import timezone

static_storage = FileSystemStorage(location=settings.BASE_DIR / 'static/questions')

# class Quiz(models.Model):
#     title = models.CharField(max_length=255)
#     # code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     code = models.IntegerField(unique=True, editable=False, null=True, blank=True)
#     host = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         if not self.code:
#             self.code = self.generate_unique_code()
#         super().save(*args, **kwargs)

#     def generate_unique_code(self):
#         while True:
#             code = random.randint(100000, 999999)
#             if not Quiz.objects.filter(code=code).exists():
#                 return code

#     def __str__(self):
#         return self.title

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)
    code = models.IntegerField(unique=True, editable=False, null=True, blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    show_results_to_student = models.BooleanField(default=True)  # Show results or not
    duration = models.IntegerField(default=2)  # Duration in minutes
    is_active = models.BooleanField(default=True)  # Whether the quiz is active or not

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = random.randint(100000, 999999)
            if not Quiz.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice (Single Answer)'),
        ('MCA', 'Multiple Choice (Multiple Answers)'),
        ('TF', 'True/False'),
    )

    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    option1 = models.CharField(max_length=255, blank=True, null=True)
    option2 = models.CharField(max_length=255, blank=True, null=True)
    option3 = models.CharField(max_length=255, blank=True, null=True)
    option4 = models.CharField(max_length=255, blank=True, null=True)
    correct_option = models.CharField(max_length=255)
    image_loc = models.CharField(max_length=255, blank=True, null=True)
    images = models.ImageField(upload_to='questions/', null=True, blank=True)
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text
    
class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='results', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_points = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.score}/{self.total_points} ({self.percentage}%)"

    class Meta:
        ordering = ['-submitted_at']  # Most recent results first

# class StudentAnswer(models.Model):
#     quiz_result = models.ForeignKey(QuizResult, related_name='answers', on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     user_answer = models.CharField(max_length=255)
#     correct_answer = models.CharField(max_length=255)

#     def __str__(self):
#         return f"Answer by {self.quiz_result.user.username} for {self.question}"

class StudentAnswer(models.Model):
    quiz_result = models.ForeignKey(QuizResult, related_name='student_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=255)

    def _str_(self):
        # return f"{self.quiz_result.user.email}'s answer for {self.question.question_text}"
        return f"{self.quiz_result.user.first_name} {self.quiz_result.user.last_name} - {self.quiz_result.quiz.title} - {self.quiz_result.score}"