from django.contrib import admin
from .models import Problem

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'platform', 'topics_list')
    list_filter = ('difficulty', 'platform')
    search_fields = ('title',)
    
    def topics_list(self, obj):
        return ", ".join([t.name for t in obj.topics.all()])
    topics_list.short_description = 'Topics'

admin.site.register(Problem, ProblemAdmin)