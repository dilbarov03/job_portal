from django.urls import include, path
from .views import *

urlpatterns = [
   #general 
   path("general/", GeneralInfoView.as_view()),
   path("category/", CategoryView.as_view()),
   path("region/<str:region>/", RegionView.as_view()),
   path("search/company", SearchCompanyView.as_view()),
   path("search/vacancy", SearchVacancyView.as_view()),
   path("search/worker", SearchWorkerView.as_view()),

   #for worker
   path("home/worker", WorkerHomeView.as_view()),
   path("worker/", WorkerGetCreateView.as_view()),
   path("vacancy/all", VacancyFilterView.as_view()), #with filter
   path("vacancy/<int:pk>/apply", VacancyApplyView.as_view()),
   path("worker/applied_jobs", AppliedJobsView.as_view()),
   path("worker/resume", UpdateResumeView.as_view()),
   path("worker/profile", GetUpdateProfileView.as_view()),
   path("worker/desired_job", WorkerJobCRUDView.as_view()),
   path("worker/languages", WorkerLanguageView.as_view()),
   path("worker/languages/<int:pk>", WorkerLanguageUpdateDeleteView.as_view()),
   path("worker/experience", WorkerExperienceView.as_view()),
   path("worker/experience/<int:pk>", WorkerExperienceUpdateDeleteView.as_view()),
   path("worker/portfoilo", WorkerPortfoiloView.as_view()),
   path("worker/portfoilo/<int:pk>", WorkerPortfoiloUpdateDeleteView.as_view()),


   #for company
   path("company/", CompanyListCreateView.as_view()),
   path("company/vacancy", CompanyVacancyView.as_view()),
   path("company/applied_users/", AppliedUsersView.as_view()),
   path("company/update", CompanyGetUpdateView.as_view()),
   path("workers/all", WorkersFilterView.as_view()), #with filter
]