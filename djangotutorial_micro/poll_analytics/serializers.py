from rest_framework import serializers
from django.db.models import Sum
from polls.models import Question, Choice

class ChoiceAnalyticsSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes', 'percentage']

    def get_percentage(self, obj):
        total_votes = obj.question.choice_set.aggregate(total=Sum('votes'))['total'] or 0
        if total_votes > 0:
            return (obj.votes / total_votes) * 100
        return 0.0

class QuestionAnalyticsSerializer(serializers.ModelSerializer):
    choices = ChoiceAnalyticsSerializer(many=True, source='choice_set')
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'pub_date', 'total_votes', 'choices']

    def get_total_votes(self, obj):
        total = obj.choice_set.aggregate(total=Sum('votes'))['total'] or 0
        return total