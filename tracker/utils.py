from django.db.models import Sum, DurationField
from django.db.models.functions import TruncDate
from datetime import timedelta
from .models import UserProblem


def get_user_stats(user):
    # Solved problems
    solved_problems = UserProblem.objects.filter(user=user, status='Solved')
    solved_count = solved_problems.count()
    
    # Difficulty distribution
    difficulty_stats = {
        'Easy': solved_problems.filter(problem__difficulty='Easy').count(),
        'Medium': solved_problems.filter(problem__difficulty='Medium').count(),
        'Hard': solved_problems.filter(problem__difficulty='Hard').count(),
    }

    # Total time spent
    time_aggregation = solved_problems.aggregate(
        total_time=Sum('time_taken', output_field=DurationField())
    )
    total_time = time_aggregation['total_time'] or timedelta(0)

    # Format total time to HH:MM:SS
    total_seconds = int(total_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    time_spent_str = f"{hours}:{minutes:02d}:{seconds:02d}"

    # Daily time spent (last 7 days)
    daily_time_data = (
        solved_problems
        .annotate(solve_day=TruncDate('solve_date'))
        .values('solve_day')
        .annotate(total_time=Sum('time_taken', output_field=DurationField()))
        .order_by('-solve_day')[:7]
    )

    daily_time_spent = []
    for entry in daily_time_data:
        total_time = entry['total_time'] or timedelta(0)
        total_seconds = int(total_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        daily_time_spent.append({
            'date': entry['solve_day'],
            'time_spent': time_str
        })

    # Recent activity
    recent_activity = solved_problems.order_by('-solve_date')[:5]

    return {
        'solved_count': solved_count,
        'difficulty_stats': difficulty_stats,
        'time_spent': time_spent_str,
        'daily_time_spent': daily_time_spent,
        'recent_activity': recent_activity,
    }
