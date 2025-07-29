import csv
from django.core.management.base import BaseCommand
from tracker.models import Problem, Topic

class Command(BaseCommand):
    help = 'Imports DSA problems from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        with open(options['file_path'], 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Create problem
                problem, created = Problem.objects.get_or_create(
                    title=row['title'],
                    defaults={
                        'url': row['url'],
                        'difficulty': row.get('difficulty', 'Medium'),
                        'platform': row.get('platform', 'LeetCode')
                    }
                )
                
                # Add topics
                if 'topics' in row:
                    for topic_name in [t.strip() for t in row['topics'].split(',')]:
                        if topic_name:
                            topic, _ = Topic.objects.get_or_create(name=topic_name)
                            problem.topics.add(topic)
                
                self.stdout.write(f"{'Created' if created else 'Updated'}: {problem.title}")