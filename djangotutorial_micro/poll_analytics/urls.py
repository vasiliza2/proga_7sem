from django.urls import path
from . import views

urlpatterns = [
    path('questions/<int:pk>/stats/', views.QuestionAnalyticsView.as_view(), name='question_stats'),
    path('questions/<int:pk>/chart/svg/', views.QuestionChartSVGView.as_view(), name='question_chart_svg'),
    path('questions/<int:pk>/chart/png/', views.QuestionChartPNGView.as_view(), name='question_chart_png'),
    path('questions/search/', views.QuestionSearchView.as_view(), name='question_search'),
]