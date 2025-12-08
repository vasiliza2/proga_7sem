import base64
from io import BytesIO
import matplotlib.pyplot as plt

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from polls.models import Question
from .serializers import QuestionAnalyticsSerializer

# Микросервис: Статистика по голосованиям
class QuestionAnalyticsView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionAnalyticsSerializer
    lookup_field = 'pk' # Используем 'id' вопроса

# Микросервис: Графики и диаграммы
class QuestionChartSVGView(APIView):
    def get(self, request, pk, format=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        choices = question.choice_set.all()
        labels = [choice.choice_text for choice in choices]
        votes = [choice.votes for choice in choices]

        total_votes = sum(votes)
        if total_votes == 0:
            return Response({"error": "No votes yet for this question"}, status=400)

        percentages = [(v / total_votes) * 100 for v in votes]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(labels, percentages, color='skyblue')
        ax.set_ylabel('Процент голосов')
        ax.set_title(f'Результаты голосования: "{question.question_text}"')
        ax.set_ylim(0, 100) # Проценты от 0 до 100

        # Добавляем подписи с процентами над столбцами
        for i, p in enumerate(percentages):
            ax.text(i, p + 2, f'{p:.1f}%', ha='center')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='svg')
        buffer.seek(0)
        svg_data = buffer.getvalue().decode('utf-8')
        plt.close(fig) # Закрываем фигуру, чтобы избежать утечек памяти

        # В данном случае, мы отправляем SVG как строку,
        # если бы нужно было PNG, то использовали бы base64 кодирование
        # png_buffer = BytesIO()
        # plt.savefig(png_buffer, format='png')
        # png_base64 = base64.b64encode(png_buffer.getvalue()).decode('utf-8')

        return Response({"svg_chart": svg_data})

class QuestionChartPNGView(APIView):
    def get(self, request, pk, format=None):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        choices = question.choice_set.all()
        labels = [choice.choice_text for choice in choices]
        votes = [choice.votes for choice in choices]

        total_votes = sum(votes)
        if total_votes == 0:
            return Response({"error": "No votes yet for this question"}, status=400)

        percentages = [(v / total_votes) * 100 for v in votes]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(labels, percentages, color='lightgreen')
        ax.set_ylabel('Процент голосов')
        ax.set_title(f'Результаты голосования: "{question.question_text}"')
        ax.set_ylim(0, 100)

        for i, p in enumerate(percentages):
            ax.text(i, p + 2, f'{p:.1f}%', ha='center')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        return Response({"png_chart_base64": png_base64})

# Микросервис для поиска голосований (основное приложение polls будет использовать этот API)
class QuestionSearchView(generics.ListAPIView):
    queryset = Question.objects.all().order_by('-pub_date')
    serializer_class = QuestionAnalyticsSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по дате
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(pub_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(pub_date__lte=end_date)

        # Поиск по тексту вопроса
        search_term = self.request.query_params.get('q')
        if search_term:
            queryset = queryset.filter(question_text__icontains=search_term)

        # Сортировка (популярность - количество голосов, дата проведения)
        sort_by = self.request.query_params.get('sort_by')
        if sort_by == 'popularity':
            queryset = queryset.annotate(total_votes=Sum('choice__votes')).order_by('-total_votes')
        elif sort_by == 'date_asc':
            queryset = queryset.order_by('pub_date')
        elif sort_by == 'date_desc': # по умолчанию уже идет сортировка по убыванию даты
            queryset = queryset.order_by('-pub_date')

        return queryset