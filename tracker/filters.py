import django_filters
from .models import Problem
from django import forms

class ProblemFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    difficulty = django_filters.ChoiceFilter(choices=Problem.DIFFICULTY_CHOICES)
    platform = django_filters.ChoiceFilter(choices=Problem.PLATFORM_CHOICES)
    topics = django_filters.ModelMultipleChoiceFilter(
        field_name='topics',
        queryset=Problem.topics.field.related_model.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Problem
        fields = ['title', 'difficulty', 'platform', 'topics']