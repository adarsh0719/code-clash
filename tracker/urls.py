from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('problems/', views.problem_list, name='problem_list'),
    path('roadmap/', views.topic_roadmap, name='topic_roadmap'),
    path('daily-challenge/', views.daily_challenge, name='daily_challenge'),
    path('achievements/', views.achievements, name='achievements'),
    path('set-goal/', views.set_goal, name='set_goal'),
    path('suggest-problem/', views.suggest_problem, name='suggest_problem'),
    path('', views.public_dashboard, name='public_dashboard'),
]