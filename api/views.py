from cgitb import lookup
from functools import reduce
import operator
from random import choices
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from vacancy.models import LANGUAGE_CHOICES, REGION_CHOICES, WORKER_STATUS, Category, Vacancy, Company, Worker, WorkerDesiredJob, WorkerLanguages
from django.db.models import Q
from .serializers import *
from rest_framework import status
from django.http import Http404
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

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
            "name": category.parent.name
         }
         if res not in cat:
            cat.append(res)

      output = {
         f"Компании в {region}": comp_serializer.data,
         f"Вакансии дня в {region}": vac_serializer.data,
         f"Работа по профессиям в {region}": cat
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
      recommended_jobs = Vacancy.objects.filter(reduce(operator.or_, (Q(title__contains=word) for word in worker.desired_job_title.split())))
      recJobs_serializer = VacancyRegionSerializer(recommended_jobs, many=True)
      savedJobs_Serializer = VacancyRegionSerializer(worker.saved_jobs, many=True)
      appliedJobs_Serializer = VacancyRegionSerializer(worker.applied_jobs, many=True)

      result = {
         "Избранные вакансии" : savedJobs_Serializer.data, 
         "Отклики": appliedJobs_Serializer.data,
         "Рекомендуем лично вам": recJobs_serializer.data
      }

      return Response(result)

class WorkerGetCreateView(generics.ListCreateAPIView):
   queryset = Worker.objects.all()
   serializer_class = WorkerSerializer

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
      vacancy = Vacancy.objects.get(pk=self.kwargs.get("pk"))
      worker = Worker.objects.filter(user=request.user).first()
      if vacancy and worker:
         if vacancy not in worker.applied_jobs.all():
            worker.applied_jobs.add(vacancy)
            worker.save()
            appliedJobs_Serializer = VacancyRegionSerializer(worker.applied_jobs, many=True)
            return Response({"status": "You applied successfully to this job", 
            "Your applied vacancies": appliedJobs_Serializer.data})
         return Response({"msg": "You have already applied to this job"})

class AppliedJobsView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      worker = Worker.objects.filter(user=request.user).first()
      appliedJobs_Serializer = VacancyRegionSerializer(worker.applied_jobs, many=True)
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
      serializer = WorkerSerializer(worker, data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkerJobCRUDView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.get(user=self.request.user))
      serializer = WorkerJobSerializer(worker_job)
      return Response(serializer.data)

   def post(self, request, format=None):
      serializer = WorkerJobSerializer(data=request.data)
      if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   def put(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.get(user=self.request.user))
      serializer = WorkerJobSerializer(worker_job, data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

   def delete(self, request):
      worker_job = WorkerDesiredJob.objects.filter(worker=Worker.objects.get(user=self.request.user))
      if worker_job:
         worker_job.delete()
      else:
         raise Http404
      return Response({"msg": "Successfully deleted"})

class WorkerLanguageView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]

   serializer_class = WorkerLanguageSerializer

   def get_queryset(self):
      return WorkerLanguages.objects.filter(worker=Worker.objects.get(user=self.request.user)).all()   

class WorkerLanguageUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
 
   serializer_class = WorkerLanguageSerializer
   def get_queryset(self):
      return WorkerLanguages.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.get(user=self.request.user))

class WorkerExperienceView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerExperienceSerializer
   def get_queryset(self):
      return WorkerExperience.objects.filter(worker=Worker.objects.get(user=self.request.user)).all()

class WorkerExperienceUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerExperienceSerializer
   def get_queryset(self):
      return WorkerExperience.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.get(user=self.request.user))  

class WorkerPortfoiloView(generics.ListCreateAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerPortfoiloSerializer
   def get_queryset(self):
      return WorkerPortfoilo.objects.filter(worker=Worker.objects.get(user=self.request.user)).all()

class WorkerPortfoiloUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = WorkerPortfoiloSerializer
   def get_queryset(self):
      return WorkerPortfoilo.objects.filter(pk=self.kwargs.get("pk"), worker=Worker.objects.get(user=self.request.user))  


"""
TODO
   - /company/vacancies - get vacancies or post a new vacancy
   - /vacancy/<id>/applied_users - see who applied to your vacancy
"""

class CompanyListCreateView(generics.ListCreateAPIView):
   queryset = Company.objects.all()
   serializer_class = CompanySerializer

class CompanyVacancyView(generics.ListCreateAPIView):
   serializer_class = VacancySerializer

   def get_queryset(self):
      user = self.request.user
      company = Company.objects.get(user=user)
      return Vacancy.objects.filter(company=company).all()

class AppliedUsersView(generics.ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = AppliedUserSerializer
   
   def get_queryset(self):
      user = self.request.user
      company = Company.objects.get(user=user)
      return Worker.objects.filter(applied_jobs__company=company).all() 


class CompanyGetUpdateView(APIView):
   permission_classes = [IsAuthenticated]
   def get(self, request):
      company = Company.objects.filter(user=self.request.user).first()
      serializer = CompanySerializer(company)
      return Response(serializer.data)

   def put(self, request):
      company = Company.objects.filter(user=self.request.user).first()
      serializer = CompanySerializer(company, data=request.data)
      if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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