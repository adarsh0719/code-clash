from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, date
from .forms import UserProblemForm, GoalForm  # Use the restored forms
from .forms import ProblemSuggestionForm
from django.contrib.auth import authenticate, login, logout  # Add authenticate import
from django.contrib.auth.forms import AuthenticationForm 
from .models import (
    Problem, UserProblem, Topic, DailyChallenge, 
    UserDailyChallenge, Goal, Achievement, UserAchievement, Streak
)
from .forms import UserProblemForm, GoalForm
from django_filters.views import FilterView
from .filters import ProblemFilter
from .utils import get_user_stats


@login_required
def dashboard(request):
    
    stats = get_user_stats(request.user)
    
    # Streak information
    streak, created = Streak.objects.get_or_create(user=request.user)
    today = timezone.now().date()
    last_solved = UserProblem.objects.filter(
        user=request.user, 
        status='Solved'
    ).order_by('-solve_date').first()
    
    if last_solved and last_solved.solve_date.date() == today:
        streak, created = Streak.objects.get_or_create(user=request.user)
        if streak.last_activity != today:
            if streak.last_activity and (today - streak.last_activity).days == 1:
                streak.current_streak += 1
            else:
                streak.current_streak = 1
            streak.last_activity = today
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            streak.save()
    
    # Topic progress
    topics = Topic.objects.all().order_by('order')
    topic_progress = []
    for topic in topics:
        total_problems = Problem.objects.filter(topics=topic).count()
        solved_problems = UserProblem.objects.filter(
            user=request.user,
            problem__topics=topic,
            status='Solved'
        ).count()
        if total_problems > 0:
            percentage = (solved_problems / total_problems) * 100
        else:
            percentage = 0
        topic_progress.append({
            'topic': topic,
            'solved': solved_problems,
            'total': total_problems,
            'percentage': round(percentage, 1)
        })
    
    # Goals
    active_goals = Goal.objects.filter(user=request.user, is_active=True)
    
    # Achievements
    achievements = UserAchievement.objects.filter(user=request.user)
    
    context = {
        'solved_problems': stats['solved_count'],
        'difficulty_data': stats['difficulty_stats'],
        'time_spent': stats['time_spent'],
        'streak': streak,
        'recent_activity': stats['recent_activity'],
        'topic_progress': topic_progress,
        'active_goals': active_goals,
        'achievements': achievements,
    }
    
    return render(request, 'tracker/dashboard.html', context)

@login_required
def suggest_problem(request):
    if request.method == 'POST':
        form = ProblemSuggestionForm(request.POST)
        if form.is_valid():
            # In a real app, you'd save this to a model
            messages.success(request, 'Problem suggestion submitted! Admin will review it soon.')
            return redirect('problem_list')
    else:
        form = ProblemSuggestionForm()
    
    return render(request, 'tracker/suggest_problem.html', {'form': form})
@login_required
def problem_list(request):
    problems = Problem.objects.all()
    user_problems = UserProblem.objects.filter(user=request.user)
    user_problem_dict = {up.problem_id: up for up in user_problems}
    
    # Filtering
    problem_filter = ProblemFilter(request.GET, queryset=problems)
    filtered_problems = problem_filter.qs
    
    if request.method == 'POST':
        problem_id = request.POST.get('problem_id')
        status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        problem = get_object_or_404(Problem, id=problem_id)
        user_problem, created = UserProblem.objects.get_or_create(
            user=request.user,
            problem=problem,
            defaults={'status': 'Not Started'}
        )
        
        if status:
            user_problem.status = status
            if status == 'Solved':
                user_problem.solve_date = timezone.now()
        user_problem.notes = notes
        user_problem.save()
        
        messages.success(request, 'Problem status updated successfully!')
        return redirect('problem_list')
    
    context = {
        'problems': filtered_problems,
        'user_problem_dict': user_problem_dict,
        'filter': problem_filter,
    }
    return render(request, 'tracker/problem_list.html', context)

def safe_convert_order(order):
    """Safely convert order to integer or return infinity for non-convertible values"""
    if isinstance(order, int):
        return order
    try:
        return int(order)
    except (TypeError, ValueError):
        return float('inf')

@login_required
def topic_roadmap(request):
    topics = Topic.objects.order_by('order')
    
    if not topics.exists():
        return render(request, 'tracker/topic_roadmap.html', {'topic_data': None})
    
    topic_ids = topics.values_list('id', flat=True)
    
    total_counts = Problem.objects.filter(topics__in=topic_ids) \
        .values('topics') \
        .annotate(total=Count('id'))
    total_dict = {item['topics']: item['total'] for item in total_counts}
    
    solved_counts = UserProblem.objects.filter(
        user=request.user,
        status='Solved',
        problem__topics__in=topic_ids
    ).values('problem__topics') \
     .annotate(solved=Count('id'))
    solved_dict = {item['problem__topics']: item['solved'] for item in solved_counts}
    
    topic_data = []
    for index, topic in enumerate(topics):
        total = total_dict.get(topic.id, 0)
        solved = solved_dict.get(topic.id, 0)
        percentage = (solved / total * 100) if total > 0 else 0

        # 🔐 Safe unlock threshold parsing with fallback
        try:
            unlock_threshold = float(topic.unlock_threshold)
        except (ValueError, TypeError):
            unlock_threshold = 70.0  # default value if blank or invalid

        is_unlocked = True
        if index > 0:
            prev_topic = topic_data[index - 1]
            if prev_topic['percentage'] < unlock_threshold:
                is_unlocked = False

        topic_data.append({
            'topic': topic,
            'solved': solved,
            'total': total,
            'percentage': round(percentage, 1),
            'is_unlocked': is_unlocked
        })

    return render(request, 'tracker/topic_roadmap.html', {'topic_data': topic_data})

@login_required
def achievements(request):
    all_achievements = Achievement.objects.all()
    user_achievements = UserAchievement.objects.filter(user=request.user)
    achieved_ids = [ua.achievement.id for ua in user_achievements]

    # Count solved problems
    solved_count = UserProblem.objects.filter(
        user=request.user,
        status='Solved'
    ).count()

    # Define achievement milestones
    milestones = [
        {"name": "Bronze - 5 Problems", "count": 5, "desc": "Solved 5 problems", "cond": "problems_solved >= 5"},
        {"name": "Silver - 10 Problems", "count": 10, "desc": "Solved 10 problems", "cond": "problems_solved >= 10"},
        {"name": "Gold - 50 Problems", "count": 50, "desc": "Solved 50 problems", "cond": "problems_solved >= 50"},
        {"name": "Platinum - 100 Problems", "count": 100, "desc": "Solved 100 problems", "cond": "problems_solved >= 100"},
    ]

    for milestone in milestones:
        if solved_count >= milestone["count"]:
            achievement, created = Achievement.objects.get_or_create(
                name=milestone["name"],
                defaults={
                    'description': milestone["desc"],
                    'condition': milestone["cond"]
                }
            )
            if achievement.id not in achieved_ids:
                UserAchievement.objects.create(user=request.user, achievement=achievement)
                messages.success(request, f'New achievement unlocked: {milestone["name"]}!')
                return redirect('achievements')

    context = {
        'all_achievements': all_achievements,
        'user_achievements': user_achievements,
        'achieved_ids': achieved_ids,
    }
    return render(request, 'tracker/achievements.html', context)


@login_required
def set_goal(request):
    if request.method == 'POST':
        target = request.POST.get('target')
        period = request.POST.get('period')
        
        if target and period:
            # Create or update the goal
            goal, created = Goal.objects.update_or_create(
                user=request.user,
                is_active=True,
                defaults={
                    'target': target,
                    'period': period,
                    'start_date': timezone.now().date()
                }
            )
            messages.success(request, 'Goal set successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fill in all fields')
    
    return render(request, 'tracker/set_goal.html')

def public_dashboard(request):
    # Public stats (simplified version)
    total_users = User.objects.count()
    total_problems = Problem.objects.count()
    total_solved = UserProblem.objects.filter(status='Solved').count()
    
    context = {
        'total_users': total_users,
        'total_problems': total_problems,
        'total_solved': total_solved,
    }
    return render(request, 'tracker/public_dashboard.html', context)


@login_required
def suggest_problem(request):
    if request.method == 'POST':
        form = ProblemSuggestionForm(request.POST)
        if form.is_valid():
            # Create problem suggestion (not published yet)
            # In a real app, you'd save this to a model for admin review
            messages.success(request, 'Problem suggestion submitted! Admin will review it soon.')
            return redirect('problem_list')
    else:
        form = ProblemSuggestionForm()
    
    return render(request, 'tracker/suggest_problem.html', {'form': form})

def daily_challenge(request):
    today = timezone.now().date()
    
    # Get or create today's daily challenge (admin-created)
    daily_challenge_obj, created = DailyChallenge.objects.get_or_create(
        date=today,
        defaults={
            'problem': Problem.objects.order_by('?').first()  # Random problem as default
        }
    )
    
    # Handle user's interaction with the challenge
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'set_custom':
            # User wants to set their own challenge
            problem_id = request.POST.get('problem_id')
            if problem_id:
                problem = get_object_or_404(Problem, id=problem_id)
                daily_challenge_obj.problem = problem
                daily_challenge_obj.save()
                messages.success(request, 'Custom daily challenge set!')
        
        elif action == 'mark_complete':
            # User marks challenge as complete
            user_challenge, created = UserDailyChallenge.objects.get_or_create(
                user=request.user,
                challenge=daily_challenge_obj,
                defaults={'completed': True, 'completed_at': timezone.now()}
            )
            if not created and not user_challenge.completed:
                user_challenge.completed = True
                user_challenge.completed_at = timezone.now()
                user_challenge.save()
            
            # Update user's solved problems
            UserProblem.objects.update_or_create(
                user=request.user,
                problem=daily_challenge_obj.problem,
                defaults={
                    'status': 'Solved',
                    'solve_date': timezone.now()
                }
            )
            
            # Update streak
            streak, created = Streak.objects.get_or_create(user=request.user)
            if streak.last_activity != today:
                if streak.last_activity and (today - streak.last_activity).days == 1:
                    streak.current_streak += 1
                else:
                    streak.current_streak = 1
                streak.last_activity = today
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
                streak.save()
            
            messages.success(request, 'Challenge marked as complete! Streak updated!')
        
        return redirect('daily_challenge')
    
    # Get user's challenge status
    try:
        user_challenge = UserDailyChallenge.objects.get(
            user=request.user,
            challenge=daily_challenge_obj
        )
    except UserDailyChallenge.DoesNotExist:
        user_challenge = None
    
    # Get available problems for custom challenge
    problems = Problem.objects.exclude(id=daily_challenge_obj.problem.id).order_by('?')[:10]
    
    # Check if user has solved this problem before
    try:
        user_problem = UserProblem.objects.get(
            user=request.user,
            problem=daily_challenge_obj.problem
        )
        already_solved = user_problem.status == 'Solved'
    except UserProblem.DoesNotExist:
        already_solved = False
    
    context = {
        'daily_challenge': daily_challenge_obj,
        'user_challenge': user_challenge,
        'problems': problems,
        'today': today,
        'already_solved': already_solved,
        
    }
    return render(request, 'tracker/daily_challenge.html', context)