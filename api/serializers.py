from common.models import User
from rest_framework import serializers
from vacancy.models import Category, Vacancy, Company, Worker, WorkerDesiredJob, WorkerExperience, WorkerLanguages, WorkerPortfoilo


class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ["username", "full_name"]

class ChildCategorySerializer(serializers.ModelSerializer):
   class Meta:
      model = Category
      fields = ['name', 'vacancy_count', 'parent', "min_salary", "max_salary"]

class ParentCategorySerializer(serializers.ModelSerializer):
   child_category = ChildCategorySerializer(many=True)
   class Meta:
      model = Category
      fields = ['name', 'vacancy_count', 'parent', 'min_salary', 'max_salary', "child_category"]

class CompanyRegionSerializer(serializers.ModelSerializer):
   class Meta:
      model = Company
      fields = ['title', 'vacancy_count']   

class CompanyNameSerializer(serializers.ModelSerializer):
   class Meta:
      model = Company
      fields = ['title']

class VacancyRegionSerializer(serializers.ModelSerializer):
   company = CompanyNameSerializer(read_only=True)
   class Meta:
      model = Vacancy
      fields = ['title', 'company', 'min_salary', 'max_salary']

class RegionSerializer(serializers.ModelSerializer):
   class Meta:
      model = Category
      fields = ['name']

class WorkerResumeSerializer(serializers.ModelSerializer):
   class Meta:
      model = Worker
      fields = ['resume']

class WorkerSerializer(serializers.ModelSerializer):
   saved_jobs = VacancyRegionSerializer(many=True)
   applied_jobs = VacancyRegionSerializer(many=True)
   class Meta:
      model = Worker
      fields = "__all__"

class WorkerJobSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerDesiredJob
      fields = "__all__"

class WorkerLanguageSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerLanguages
      fields = "__all__"

class WorkerExperienceSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerExperience
      fields = "__all__"

class WorkerPortfoiloSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerPortfoilo
      fields = "__all__"

class VacancySerializer(serializers.ModelSerializer):
   class Meta:
      model = Vacancy
      fields = "__all__"

class VacancyForCompanySerializer(serializers.ModelSerializer):
   class Meta:
      model = Vacancy
      fields = ['title']

class AppliedUserSerializer(serializers.ModelSerializer):
   applied_jobs = VacancyForCompanySerializer(many=True)
   user = UserSerializer(read_only=True)
   class Meta:
      model = Worker
      fields = ["user","resume", "applied_jobs"]

class CompanySerializer(serializers.ModelSerializer):
   class Meta:
      model = Company
      fields = "__all__"

class WorkerAllSerializer(serializers.ModelSerializer):
   user = UserSerializer(read_only=True)
   desired_job = WorkerJobSerializer(many=True)
   languages = WorkerLanguageSerializer(many=True)
   work_experience = WorkerExperienceSerializer(many=True)
   portfoilo = WorkerPortfoiloSerializer(many=True)
   
   class Meta:
      model = Worker
      fields = ["user", "description", "birthdate", "phone_number", "telegram",
      "region", "resume", "status", "has_experience", "has_portfoilo", 
      "native_language", "languages", "desired_job", "work_experience", 
      "portfoilo"]