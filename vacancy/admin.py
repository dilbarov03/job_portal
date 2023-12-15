from django.contrib import admin
from .models import Category, Vacancy, Company, Worker, WorkerDesiredJob, WorkerLanguages, WorkerExperience, WorkerPortfoilo

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
   list_display = ['title', 'short_description', 'vacancy_count', 'location']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
   list_display = ['name', 'vacancy_count', 'parent']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
   list_display = ['title', 'short_description', 'company', 'job', 'region']


class WorkerLanguageInline(admin.TabularInline):
   model = WorkerLanguages
   extra = 1
   
class WorkerExperienceInline(admin.StackedInline):
   model = WorkerExperience
   extra = 1


class WorkerPortfoiloInline(admin.StackedInline):
   model = WorkerPortfoilo
   extra = 1


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
   list_display = ['short_description']
   inlines = [WorkerLanguageInline, WorkerExperienceInline, WorkerPortfoiloInline]


@admin.register(WorkerDesiredJob)
class WorkerDJAdmin(admin.ModelAdmin):
   list_display = ["worker"]   