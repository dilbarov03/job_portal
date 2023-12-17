from common.models import FAQ, Feedback, User
from rest_framework import serializers
from vacancy.models import ApplicationFeedback, Category, InterviewSchedule, Notification, Vacancy, Company, Worker, WorkerDesiredJob, WorkerExperience, WorkerLanguages, WorkerPortfoilo, JobApplication


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
      fields = ['title', 'id']

class VacancyRegionSerializer(serializers.ModelSerializer):
   company = CompanyNameSerializer(read_only=True)
   class Meta:
      model = Vacancy
      fields = ['id', 'title', 'slug', 'company', 'min_salary', 'max_salary']

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
   user = UserSerializer(read_only=True)
   # applied_jobs = VacancyRegionSerializer(many=True)
   class Meta:
      model = Worker
      fields = "__all__"
      

class WorkerCreateSerializer(serializers.ModelSerializer):

   class Meta:
      model = Worker
      fields = ("id", "description", "birthdate", "phone_number", "telegram", "region", "native_language", "resume",
                "status")


class WorkerJobSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerDesiredJob
      fields = ("id", "title", "category", "salary", "employment_type", "schedule")
      
   def create(self, validated_data):
      worker = self.context['request'].user.worker
      desired_job = WorkerDesiredJob.objects.create(worker=worker, **validated_data)
      return desired_job

class WorkerLanguageSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerLanguages
      fields = ("id", "language", "level")

class WorkerExperienceSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerExperience
      fields = ("id", "position", "organization", "organization_category", "start_date",
                "end_date", "is_active")

class WorkerPortfoiloSerializer(serializers.ModelSerializer):
   class Meta:
      model = WorkerPortfoilo
      fields = ("id", "description", "image")
      

class VacancySerializer(serializers.ModelSerializer):
   company = CompanyNameSerializer(read_only=True)
   job = serializers.SerializerMethodField()
   
   class Meta:
      model = Vacancy
      fields = ("id", "title", "description", "company", "job", "min_salary", "max_salary", 
                "region", "is_active", "is_remote")
      
   def get_job(self, value):
      return {
         "id": value.job.id,
         "name": value.job.name
      }
   
class VacancyCreateSerializer(serializers.ModelSerializer):
   
   class Meta:
      model = Vacancy
      fields = ("id", "title", "description", "job", "min_salary", "max_salary", 
                "region", "is_active", "is_remote")
      
      
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
      
      
class CompanyCreateSerializer(serializers.ModelSerializer):
   class Meta:
      model = Company
      fields = ("id", "title", "description", "location")
      

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
      

class JobApplicationSerializer(serializers.ModelSerializer):
   vacancy = VacancyRegionSerializer(read_only=True)
   worker = serializers.SerializerMethodField()
   
   class Meta:
      model = JobApplication
      fields = ("id", "worker", "vacancy", "status")

   def get_worker(self, value):
      return {
         "id": value.worker.id,
         "full_name": value.worker.user.full_name
      }
      
      
class InterviewGetSerializer(serializers.ModelSerializer):
   vacancy = VacancyRegionSerializer()
   worker = serializers.SerializerMethodField()
      
   class Meta:
      model = InterviewSchedule
      fields = ("id", "worker", "vacancy", "date", "link")
      
   def get_worker(self, value):
      return {
         "id": value.worker.id,
         "full_name": value.worker.user.full_name
      }
      
         
class InterviewScheduleSerializer(serializers.ModelSerializer):      
   class Meta:
      model = InterviewSchedule
      fields = ("id", "worker", "vacancy", "date", "link")
      

class FeedbackSerializer(serializers.ModelSerializer):
   company = serializers.SerializerMethodField()
   worker = serializers.SerializerMethodField()
   
   class Meta:
      model = ApplicationFeedback
      fields = ("id", "company", "worker", "rating", "text")
      
   def get_company(self, value):
      return {
         "id": value.company.id,
         "name": value.company.title
      }
      
   def get_worker(self, value):
      return {
         "id": value.worker.id,
         "full_name": value.worker.user.full_name
      }


class WorkerFeedbackCreateSerializer(serializers.ModelSerializer):
   class Meta:
      model = ApplicationFeedback
      fields = ("id", "company", "text", "rating")
      
   def validate(self, data):
      if data["rating"] > 10 or data["rating"] < 1:
         raise serializers.ValidationError("Rating must be between 1 and 10")
      company = data["company"]
      worker = self.context["request"].user.worker
      if ApplicationFeedback.objects.filter(company=company, worker=worker, provider="worker").exists():
         raise serializers.ValidationError("You already have feedback for this company")
      return data


class CompanyFeedbackCreateSerializer(serializers.ModelSerializer):
   class Meta:
      model = ApplicationFeedback
      fields = ("id", "worker", "text", "rating")
      
   def validate(self, data):
      if data["rating"] > 10 or data["rating"] < 1:
         raise serializers.ValidationError("Rating must be between 1 and 10")
      worker = data["worker"]
      company = self.context["request"].user.company
      if ApplicationFeedback.objects.filter(company=company, worker=worker, provider="company").exists():
         raise serializers.ValidationError("You already have feedback for this worker")
      return data


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for creating user objects."""

    class Meta:
        model = FAQ
        fields = ('id', 'question', 'answer')
        
        

class FeedbackGeneralSerializer(serializers.ModelSerializer):
    """Serializer for creating user objects."""

    class Meta:
        model = Feedback
        fields = ('id', 'text')
        

class WorkerDetailSerializer(serializers.ModelSerializer):
   user = UserSerializer(read_only=True)
   portfoilo = WorkerPortfoiloSerializer(many=True)
   languages = WorkerLanguageSerializer(many=True)
   work_experience = WorkerExperienceSerializer(many=True)

   class Meta:
      model = Worker
      fields = ('id', 'description', 'birthdate', 'phone_number', 'telegram', 'region', 
               'native_language', 'resume', 'status', 'has_experience', 'has_portfoilo',
               'user', 'portfoilo', 'work_experience', 'languages')


class CompanyDetailSerializer(serializers.ModelSerializer):
   company_vacancy = VacancySerializer(many=True)
   
   class Meta:
      model = Company
      fields = ("id", "title", "description", "location", "vacancy_count", "company_vacancy")


class NotificationSerializer(serializers.ModelSerializer):
   
   class Meta:
      model = Notification 
      fields = ("id", "text", "created_at")
