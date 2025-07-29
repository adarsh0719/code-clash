from django import forms
from .models import UserProblem, Goal, Problem, Topic

class ProblemSuggestionForm(forms.Form):
    title = forms.CharField(max_length=200)
    url = forms.URLField()
    difficulty = forms.ChoiceField(choices=Problem.DIFFICULTY_CHOICES)
    platform = forms.ChoiceField(choices=Problem.PLATFORM_CHOICES)
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

# Add these form definitions
class UserProblemForm(forms.ModelForm):
    class Meta:
        model = UserProblem
        fields = ['status', 'notes']

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['target', 'period']