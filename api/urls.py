from django.urls import include, path
from .views import *

urlpatterns = [
   #general 
   path("feedback/", FeedbackCreateView.as_view()),
   path("faq/", FAQListView.as_view()),
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
   path("vacancy/<int:pk>/save", VacancySaveView.as_view()),
   path("worker/<int:pk>/detail", WorkerDetailView.as_view()),
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
   path("worker/interviews", WorkerInterviewListView.as_view()),
   path("worker/feedbacks", WorkerFeedbackList.as_view()),
   path("worker/feedback/create", WorkerFeedbackCreateView.as_view()),



   #for company
   path("company/", CompanyListCreateView.as_view()),
   path("company/<int:pk>/detail", CompanyDetailView.as_view()),
   path("company/create", CompanyCreateView.as_view()),
   path("company/vacancy", CompanyVacancyView.as_view()),
   path("company/vacancy/<int:pk>/applied_users", AppliedUsersView.as_view()),
   path("company/update", CompanyGetUpdateView.as_view()),
   path("company/job_application/<int:pk>", JobApplicationView.as_view()),
   path("company/schedule_interview", InterviewScheduleView.as_view()),
   path("company/interview/<int:pk>/update", InterviewScheduleUpdateView.as_view()),
   path("company/interviews", CompanyInterviewListView.as_view()),
   path("company/feedbacks", CompanyFeedbackList.as_view()),
   path("company/feedback/create", CompanyFeedbackCreateView.as_view()),
   path("workers/all", WorkersFilterView.as_view()), #with filter
]