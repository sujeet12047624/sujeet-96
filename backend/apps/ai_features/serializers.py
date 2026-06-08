"""Serializers for AI feature input validation."""

from rest_framework import serializers


class AnswerEvaluationSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)
    answer = serializers.CharField(max_length=10000)
    gs_paper = serializers.CharField(max_length=10, required=False, default="")


class RAGSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=1000)
    top_k = serializers.IntegerField(min_value=1, max_value=20, default=5)


class MCQGenerationSerializer(serializers.Serializer):
    """Pydantic-style schema for OpenAI Structured Outputs."""

    question = serializers.CharField()
    option_a = serializers.CharField()
    option_b = serializers.CharField()
    option_c = serializers.CharField()
    option_d = serializers.CharField()
    correct_option = serializers.ChoiceField(choices=["A", "B", "C", "D"])
    explanation = serializers.CharField()
    difficulty = serializers.ChoiceField(choices=["easy", "medium", "hard"])
