from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    unlock_threshold = models.FloatField(default=70)
    
    def __str__(self):
        return self.name

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    
    PLATFORM_CHOICES = [
        ('LeetCode', 'LeetCode'),
        ('GFG', 'GeeksForGeeks'),
        ('Codeforces', 'Codeforces'),
        ('HackerRank', 'HackerRank'),
        ('Other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    url = models.URLField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    topics = models.ManyToManyField(Topic)
    companies = models.CharField(max_length=200, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.difficulty})"

class UserProblem(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Solved', 'Solved'),
        ('Review', 'Review'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    notes = models.TextField(blank=True, null=True)
    solve_date = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'problem')
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title}"

class DailyChallenge(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    date = models.DateField(unique=True)
    
    def __str__(self):
        return f"Daily Challenge for {self.date}"

class UserDailyChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge}"

class Goal(models.Model):
    PERIOD_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target = models.PositiveIntegerField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.target} problems {self.period.lower()}"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='trophy')
    condition = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement')
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak}"