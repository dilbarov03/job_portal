from functools import reduce
import operator
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from common.models import Feedback
from vacancy.models import LANGUAGE_CHOICES, REGION_CHOICES, WORKER_STATUS, Category, Vacancy, Company, Worker, WorkerDesiredJob, WorkerLanguages, JobApplication, InterviewSchedule
from django.db.models import Q
from .serializers import *
from rest_framework import status
from django.http import Http404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CategoryView(generics.ListAPIView):
   queryset = Category.objects.filter(parent=None).all()
   serializer_class = ParentCategorySerializer

class GeneralInfoView(APIView):
   def get(self, request, format=None):
      vacancy_count = Vacancy.objects.all()
      companies_count = Company.objects.all()
      resume_count = Worker.objects.exclude(status__isnull=True).all()

      data = {
         "Vacancies": len(vacancy_count),
         "Companies": len(companies_count),
         "Resumies": len(resume_count)
      }

      return Response(data)

class RegionView(APIView):
   def get(self, request, *args, **kwargs):
      region = self.kwargs.get("region").capitalize()
      companies = Company.objects.filter(company_vacancy__region=region).all()
      comp_serializer = CompanyRegionSerializer(companies, many=True)

      vacancies = Vacancy.objects.filter(region=region).all()
      vac_serializer = VacancyRegionSerializer(vacancies, many=True)

      categories = Category.objects.filter(job_vacancy__region=region).all()
      cat = []
      for category in categories:
         res = {
            "name": category.parent.name if category.parent else category.name
         }
         if res not in cat:
            cat.append(res)

      output = {
         f"companies": comp_serializer.data,
         f"vacancies": vac_serializer.data,
         f"categories": cat
      }

      return Response(output)

"""     WORKER
TODO
   - /home/worker
   Отклики
   Избранные вакансии
   Рекомендуем лично вам

   - /vacancy/all
   - /vacancy/id/apply
   - /upload/resume
   - /profile/
   - /desired_job/
   - /languages/
   - /experience/
   - /portfoilo/
"""

class WorkerHomeView(APIView):
   permission_classes = [IsAuthenticated]
   def get(self, request, *args, **kwargs):
      worker = Worker.objects.filter(user=request.user).first()
      recommended_jobs = Vacancy.objects.filter(reduce(operator.or_, (Q(title__contains=word.title) for word in worker.desired_job.all())))
      recJobs_serializer = VacancyRegionSerializer(recommended_jobs, many=True)
      savedJobs_Serializer = VacancyRegionSerializer(worker.saved_jobs, many=True)
      
      appliedJobs_Serializer = VacancyRegionSerializer(worker.applied_jobs, many=True)

      result = {
         "saved_jobs" : savedJobs_Serializer.data, 
         "recommended_jobs": recJobs_serializer.data
      }

      return Response(result)

class WorkerGetCreateView(generics.CreateAPIView):
   queryset = Worker.objects.all()
   serializer_class = WorkerCreateSerializer
   permission_classes = (IsAuthenticated, )
   
   def perform_create(self, serializer):
      return serializer.save(user=self.request.user)
   

class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class VacancyFilter(filters.FilterSet):
   job_title = filters.CharFilter(field_name="job__name", lookup_expr="icontains")
   company = filters.CharFilter(field_name="company__title")
   min_salary = filters.NumberFilter(field_name="min_salary", lookup_expr="gte")
   max_salary = filters.NumberFilter(field_name="max_salary", lookup_expr="lte")
   created_at = filters.DateRangeFilter(field_name="created_at")
   is_remote = filters.BooleanFilter(field_name="is_remote")
   region = filters.ChoiceFilter(field_name="region", choices=REGION_CHOICES)

   class Meta:
      model = Vacancy
      fields = ['job_title', 'company', 'min_salary', 'max_salary', 'created_at','is_remote', 'region']

class VacancyFilterView(generics.ListAPIView):
   queryset = Vacancy.objects.all()
   serializer_class = VacancySerializer
   filter_backends = (DjangoFilterBackend, )
   filterset_class = VacancyFilter


class VacancyApplyView(APIView):
   permission_classes = [IsAuthenticated]

   def post(self, request, *args, **kwargs):
      vacancy = Vacancy.objects.filter(pk=self.kwargs.get("pk")).first()
      worker = Worker.objects.filter(user=request.user).first()
      if vacancy and worker:
         if JobApplication.objects.filter(worker=worker, vacancy=vacancy).exists():
            return Response({"msg": "You have already applied to this job"})
         JobApplication.objects.create(worker=worker, vacancy=vacancy, status="pending")
         return Response({"msg": "Successfully applied"})
      return Response({"msg": "Vacancy not found"})
   

class VacancySaveView(APIView):
   permission_classes = [IsAuthenticated]

   def post(self, request, *args, **kwargs):
      vacancy = Vacancy.objects.filter(pk=self.kwargs.get("pk")).first()
      worker = Worker.objects.filter(user=request.user).first()
      if vacancy and worker:
         if worker.saved_jobs.filter(pk=vacancy.pk).exists():
            worker.saved_jobs.remove(vacancy)
            return Response({"msg": "Successfully removed"})
         worker.saved_jobs.add(vacancy)
         return Response({"msg": "Successfully saved"})
      return Response({"msg": "Vacancy not found"})


class AppliedJobsView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      worker = Worker.objects.filter(user=request.user).first()
      applied_jobs = JobApplication.objects.filter(worker=worker).all()
      
      appliedJobs_Serializer = JobApplicationSerializer(applied_jobs, many=True)
      return Response(appliedJobs_Serializer.data)

class UpdateResumeView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      worker = Worker.objects.filter(user=self.request.user).first()
      resume_serializer = WorkerResumeSerializer(worker)
      return Response(resume_serializer.data)

   def put(self, request):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer = WorkerResumeSerializer(worker, data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUpdateProfileView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      worker = Worker.objects.filter(user=self.request.user).first()
      worker_serializer = WorkerSerializer(worker)
      return Response(worker_serializer.data)

   def put(self, request):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer = WorkerCreateSerializer(worker, data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkerJobCRUDView(APIView):
   permission_classes = [IsAuthenticated]


   def get(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.filter(user=self.request.user).first())
      serializer = WorkerJobSerializer(worker_job, many=True)
      return Response(serializer.data)

   @swagger_auto_schema(request_body=WorkerJobSerializer)
   def post(self, request, format=None):
      serializer = WorkerJobSerializer(data=request.data, context={'request': request})
      if serializer.is_valid(raise_exception=True):
         serializer.save()
         return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   @swagger_auto_schema(request_body=WorkerJobSerializer)
   def put(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.filter(user=self.request.user).first())
      serializer = WorkerJobSerializer(worker_job, data=request.data, context={'request': request})
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

   def delete(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.filter(user=self.request.user).first())
      if worker_job:
         worker_job.delete()
      else:
         raise Http404
      return Response({"msg": "Successfully deleted"})


class WorkerLanguageView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerLanguageSerializer

   def get_queryset(self):
      return WorkerLanguages.objects.filter(worker=Worker.objects.filter(user=self.request.user).first()).all()   

   def perform_create(self, serializer):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer.save(worker=worker)
   

class WorkerLanguageUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
 
   serializer_class = WorkerLanguageSerializer
   def get_queryset(self):
      return WorkerLanguages.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.filter(user=self.request.user).first())

class WorkerExperienceView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerExperienceSerializer
   
   def get_queryset(self):
      return WorkerExperience.objects.filter(worker=Worker.objects.filter(user=self.request.user).first()).all()

   def perform_create(self, serializer):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer.save(worker=worker)


class WorkerExperienceUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerExperienceSerializer
   
   def get_queryset(self):
      return WorkerExperience.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.filter(user=self.request.user).first())  


class WorkerPortfoiloView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerPortfoiloSerializer
   parser_classes = [MultiPartParser, FormParser]
   
   def get_queryset(self):
      return WorkerPortfoilo.objects.filter(worker=Worker.objects.filter(user=self.request.user).first()).all()

   def perform_create(self, serializer):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer.save(worker=worker)


class WorkerPortfoiloUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerPortfoiloSerializer
   
   def get_queryset(self):
      return WorkerPortfoilo.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.filter(user=self.request.user).first())  


"""
TODO
   - /company/vacancies - get vacancies or post a new vacancy
   - /vacancy/<id>/applied_users - see who applied to your vacancy
"""

class CompanyListCreateView(generics.ListAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanySerializer
   

class CompanyProfileView(generics.RetrieveAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanySerializer
   
   def get_object(self):
      return Company.objects.filter(user=self.request.user).first()


class CompanyCreateView(generics.CreateAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanyCreateSerializer
   permission_classes = (IsAuthenticated, )
   
   def perform_create(self, serializer):
      return serializer.save(user=self.request.user)
   


class CompanyVacancyView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]

   def get_queryset(self):
      user = self.request.user
      company = Company.objects.filter(user=user).first()
      return Vacancy.objects.filter(company=company).all()
   
   def get_serializer_class(self):
      if self.request.method == "GET":
         return VacancySerializer
      return VacancyCreateSerializer
   
   def perform_create(self, serializer):
      user = self.request.user
      company = Company.objects.filter(user=user).first()
      serializer.save(company=company)
      company.vacancy_count += 1
      company.save()


class CompanyVacancyUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = VacancyCreateSerializer
   queryset = Vacancy.objects.all()
      
   def perform_destroy(self, instance):
      company = Company.objects.filter(user=self.request.user).first()
      company.vacancy_count -= 1
      company.save()
      instance.delete()


class AppliedUsersView(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = JobApplicationSerializer
   
   def get_queryset(self):
      user = self.request.user
      company = Company.objects.filter(user=user).first()
      vacancy = Vacancy.objects.filter(pk=self.kwargs.get("pk")).first()
      
      job_applications = JobApplication.objects.filter(vacancy__company=company, vacancy=vacancy).all()
      return job_applications
      
       
class CompanyGetUpdateView(generics.UpdateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = CompanyCreateSerializer
   
   def get_object(self):
      return Company.objects.filter(user=self.request.user).first()

class JobApplicationView(APIView):
   permission_classes = [IsAuthenticated]
   
   state_param = openapi.Schema(
      type=openapi.TYPE_OBJECT,
      properties={
         'status': openapi.Schema(type=openapi.TYPE_STRING, description='Status'),
      }
   )
    
   @swagger_auto_schema(request_body=state_param)
   def post(self, request, *args, **kwargs):
      job_application = JobApplication.objects.filter(id=self.kwargs.get("pk")).first()
      company = Company.objects.filter(user=self.request.user).first()
      if job_application.vacancy.company != company:
         return Response({"msg": "This is not your vacancy"})
      if job_application:
         job_application.status = request.data.get("status")
         job_application.save()
         return Response({"msg": "Successfully updated"})
      return Response({"msg": "Job application not found"})



class WorkerFilter(filters.FilterSet):
   region = filters.ChoiceFilter(field_name="region", choices=REGION_CHOICES)   
   status = filters.ChoiceFilter(field_name="status", choices=WORKER_STATUS)
   has_experience = filters.BooleanFilter(field_name="has_experience")
   has_portfoilo = filters.BooleanFilter(field_name="has_portfoilo")
   worker_title = filters.CharFilter(field_name="desired_job__title", lookup_expr="icontains")
   worker_salary = filters.RangeFilter(field_name="desired_job__salary")

   native_language = filters.ChoiceFilter(field_name="native_language", choices=LANGUAGE_CHOICES)
   languages = filters.ChoiceFilter(field_name="languages", choices=LANGUAGE_CHOICES)

   class Meta:
      model = Worker
      fields = ['region', "status", "has_experience", "has_portfoilo",
      "worker_title", "worker_salary", "native_language", "languages"]


class WorkersFilterView(generics.ListAPIView):
   queryset = Worker.objects.all()
   serializer_class = WorkerAllSerializer
   filter_backends = (DjangoFilterBackend, )
   filterset_class = WorkerFilter


"""
SEARCH VIEWS
"""

class SearchCompanyView(generics.ListAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanySerializer
   filter_backends = [SearchFilter]
   search_fields = ['title', 'description']

class SearchVacancyView(generics.ListAPIView):
   queryset = Vacancy.objects.all()
   serializer_class = VacancySerializer
   filter_backends = [SearchFilter]
   search_fields = ['title', 'description']

class SearchWorkerView(generics.ListAPIView):
   queryset = Worker.objects.all()
   serializer_class = WorkerAllSerializer
   filter_backends = [SearchFilter]
   search_fields = ['user__full_name', 'description', "desired_job__title"]
   
   
class InterviewScheduleView(generics.CreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = InterviewScheduleSerializer
   
   def perform_create(self, serializer):
      company = Company.objects.filter(user=self.request.user).first()
      serializer.save(company=company)


class InterviewScheduleUpdateView(generics.UpdateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = InterviewScheduleSerializer
   queryset = InterviewSchedule.objects.all()
   
            
class CompanyInterviewListView(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = InterviewGetSerializer
   
   def get_queryset(self):
      company = Company.objects.filter(user=self.request.user).first()
      return InterviewSchedule.objects.filter(company=company).all()
   
   
class WorkerInterviewListView(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = InterviewGetSerializer
   
   def get_queryset(self):
      worker = Worker.objects.filter(user=self.request.user).first()
      return InterviewSchedule.objects.filter(worker=worker).all()   


class WorkerFeedbackList(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = FeedbackSerializer
   
   def get_queryset(self):
      worker = Worker.objects.filter(user=self.request.user).first()
      return ApplicationFeedback.objects.filter(worker=worker, provider="company").all()


class WorkerFeedbackCreateView(generics.CreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerFeedbackCreateSerializer
   
   def perform_create(self, serializer):
      worker = Worker.objects.filter(user=self.request.user).first()
      serializer.save(worker=worker, provider="worker")


class CompanyFeedbackList(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = FeedbackSerializer
   
   def get_queryset(self):
      company = Company.objects.filter(user=self.request.user).first()
      return ApplicationFeedback.objects.filter(company=company, provider="worker").all()


class CompanyFeedbackCreateView(generics.CreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = CompanyFeedbackCreateSerializer
   
   def perform_create(self, serializer):
      company = Company.objects.filter(user=self.request.user).first()
      serializer.save(company=company, provider="company")


class FAQListView(generics.ListAPIView):
    """Handles creating and listing Users."""
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class FeedbackCreateView(generics.CreateAPIView):
    """Handles creating and listing Users."""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackGeneralSerializer
    
    def perform_create(self, serializer):
      serializer.save(user=self.request.user)



class WorkerDetailView(generics.RetrieveAPIView):
   queryset = Worker.objects.all()
   serializer_class = WorkerDetailSerializer


class CompanyDetailView(generics.RetrieveAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanyDetailSerializer
