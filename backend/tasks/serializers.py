from rest_framework import serializers

class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_null=True)
    title = serializers.CharField()
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, default=5)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False, default=list)

class AnalyzeRequestSerializer(serializers.Serializer):
    tasks = TaskInputSerializer(many=True)
    weights = serializers.DictField(child=serializers.FloatField(), required=False)
    strategy = serializers.ChoiceField(choices=["fastest", "impact", "deadline", "smart"], required=False, default="smart")
