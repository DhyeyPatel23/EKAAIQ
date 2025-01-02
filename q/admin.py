# from django.contrib import admin
# from .models import Quiz, Question, QuizResult

# admin.site.register(Quiz)

# admin.site.register(QuizResult)

from django.contrib import admin
from .models import *
admin.site.register(Question)
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of empty forms for new questions in the admin

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'host', 'created_at')
    search_fields = ('title', 'code', 'host__username')
    list_filter = ('created_at',)
    inlines = [QuestionInline]

class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'score', 'submitted_at')
    search_fields = ('quiz__title', 'user__username')
    list_filter = ('quiz', 'submitted_at')
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_result', 'question', 'user_answer', 'correct_answer')
    search_fields = ('quiz_result__user__username', 'question__question_text')
    list_filter = ('quiz_result__quiz',)
    
    # To display ForeignKey relationships properly
    def quiz_result(self, obj):
        return f"{obj.quiz_result.user.first_name} - {obj.quiz_result.quiz.title}"
    
    def question(self, obj):
        return obj.question.question_text


admin.site.register(StudentAnswer, StudentAnswerAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizResult, QuizResultAdmin)
