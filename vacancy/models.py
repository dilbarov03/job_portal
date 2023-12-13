from distutils.command.upload import upload
from django.db import models
from django.template.defaultfilters import truncatechars
from django.db.models.signals import post_save, pre_delete, pre_save, post_delete
from django.dispatch import receiver

from common.models import User
from helpers.models import BaseModel, generate_unique_slug

REGION_CHOICES = (
   ('Toshkent', 'Toshkent'),
   ("Farg'ona", "Farg'ona"), 
   ('Andijon', 'Andijon'),
   ('Samarqand', 'Samarqand'),
   ("Buxoro", "Buxoro"),
   ("Navoiy", "Navoiy"),
   ("Qarshi", "Qarshi"),
   ("Nukus", "Nukus"),
   ("Xorazm", "Xorazm"), 
)

LANGUAGE_CHOICES = (
   ("Uzbek", "Uzbek"),
   ("Russian", "Russian"),
   ("English", "English")
)

WORKER_STATUS = (
   ('active', 'active'), #Is actively looking for a job
   ('open', 'open'), #Is open for offers
   ('closed', 'closed') #Is not looking for a job
)

class Company(BaseModel):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   title = models.CharField(max_length=128)
   slug = models.CharField(max_length=256, blank=True, null=True)
   description = models.TextField(null=True, blank=True)
   vacancy_count = models.IntegerField(default=0)
   location = models.CharField(max_length=128, null=True, blank=True)

   def __str__(self):
      return self.title

   def save(self, *args, **kwargs):
      if hasattr(self, "slug") and hasattr(self, "title"):
         if not self.slug:
               self.slug = generate_unique_slug(self.__class__, self.title)

      if self._state.adding:
         self.user.is_company = True
         self.user.save()

      super().save(*args, **kwargs)

   @property
   def short_description(self):
      return truncatechars(self.description, 35)

class Category(BaseModel):
   name = models.CharField(max_length=128)
   slug = models.CharField(max_length=256, blank=True, null=True)
   vacancy_count = models.IntegerField(default=0)
   min_salary = models.IntegerField(default=0)
   max_salary = models.IntegerField(default=0)
   parent = models.ForeignKey("self", null=True, blank=True, 
               related_name="child_category", on_delete=models.CASCADE)
   
   def __str__(self):
      return self.name

   def save(self, *args, **kwargs):
      if hasattr(self, "slug") and hasattr(self, "name"):
         if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.name)
      super().save(*args, **kwargs)


class Vacancy(BaseModel):
   title = models.CharField(max_length=128)
   slug = models.CharField(max_length=256, blank=True, null=True)
   description = models.TextField()
   company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_vacancy")
   job = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="job_vacancy")
   min_salary = models.BigIntegerField(null=True, blank=True)
   max_salary = models.BigIntegerField(null=True, blank=True)
   is_active = models.BooleanField(default=True)
   is_remote = models.BooleanField(default=False)
   region = models.CharField(max_length=128, null=True, blank=True, choices=REGION_CHOICES)

   def __str__(self):
      return self.title


   @property
   def short_description(self):
      return truncatechars(self.description, 35)

   def save(self, *args, **kwargs):
      if hasattr(self, "slug") and hasattr(self, "title"):
         if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.title)
      company = self.company
      category = self.job
      parent = category.parent
      
      company.vacancy_count=Vacancy.objects.filter(company=company).count()
      company.save()
      category.vacancy_count=Vacancy.objects.filter(job=category).count()
      if parent and self._state.adding:
         parent.vacancy_count+=1
      
      if self.min_salary<category.min_salary:
         category.min_salary = self.min_salary
      if self.max_salary>category.max_salary:
         category.max_salary = self.max_salary
      
      if parent:
         if self.min_salary<parent.min_salary:
            parent.min_salary = self.min_salary
         if self.max_salary>parent.max_salary:
            parent.min_salary = self.min_salary

         parent.save()
      category.save()
      
      

      super().save(*args, **kwargs)

@receiver(pre_delete, sender=Vacancy)
def my_handler(sender, instance, **kwargs):
   company = instance.company
   company.vacancy_count=Vacancy.objects.filter(company=company).count()
   parent = company.parent
   if parent:
      parent.vacancy_count-=1
      parent.save()
   company.save()

class Worker(BaseModel):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   description = models.TextField(null=True, blank=True)
   birthdate = models.DateField(null=True, blank=True)
   phone_number = models.CharField(max_length=128, null=True, blank=True)
   telegram = models.CharField(max_length=128, null=True, blank=True)
   region = models.CharField(max_length=128, choices=REGION_CHOICES)
   native_language = models.CharField(max_length=128, choices=LANGUAGE_CHOICES)

   resume = models.FileField(upload_to="files/", blank=True, null=True)
   status = models.CharField(max_length=128, choices=WORKER_STATUS)
   saved_jobs = models.ManyToManyField(Vacancy, blank=True)
   has_experience = models.BooleanField(default=False)
   has_portfoilo = models.BooleanField(default=False)

   def __str__(self):
      return self.user.full_name

   @property
   def short_description(self):
      return truncatechars(self.description, 35)

   def save(self, *args, **kwargs):
      if hasattr(self, "slug") and hasattr(self, self.user.full_name):
         if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.user.full_name)

      if hasattr(self, "slug") and hasattr(self, self.user.username):
         if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.user.username)
            
      if self._state.adding:
         self.user.is_worker = True
         self.user.save()
               

      super().save(*args, **kwargs)


class JobApplication(BaseModel):
   class ApllicationStatus(models.TextChoices):
      PENDING = 'pending'
      ACCEPTED = 'accepted'
      REJECTED = 'rejected'
   
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="applied_jobs")
   vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applied_workers")
   status = models.CharField(max_length=128, choices=ApllicationStatus.choices, default=ApllicationStatus.PENDING)
   
   class Meta:
      unique_together = ('worker', 'vacancy')


class WorkerDesiredJob(BaseModel):
   WORK_STATUS = (
      ('full work day', 'full work day'),
      ('partly work', 'partly work'),
      ('project work', 'project work'),
      ("voluntary work", 'voluntary work'),
      ("internship", "internship") 
   )

   WORK_SCHEDULE = (
      ('full-time', 'full-time'),
      ('part-time', 'part-time'),
      ('flexible', 'flexible'),
      ("remote", 'remote'),
      ("shift method", "shift method") 
   )

   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="desired_job")
   title = models.CharField(max_length=128)
   category = models.ForeignKey(Category, on_delete=models.CASCADE)
   salary = models.IntegerField()
   employment_type = models.CharField(max_length=28, choices=WORK_STATUS)
   schedule = models.CharField(max_length=28, choices=WORK_SCHEDULE)


class InterviewSchedule(BaseModel):
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="interview_schedule")
   company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="interview_schedule")
   vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="interview_schedule")
   date = models.DateTimeField()
   link = models.URLField()
   
   class Meta:
      unique_together = ("worker", "vacancy")


class WorkerLanguages(BaseModel):
   LEVEL_CHOICES = (
      ("A1 (Beginner)", "A1 (Beginner)"),
      ("A2 (Elementary)", "A2 (Elementary)"),
      ("B1 (Intermediate)", "B1 (Intermediate)"),
      ("B2 (Upper-Intermediate)", "B2 (Upper-Intermediate)"),
      ("C1 (Advanced)", "C1 (Advanced)"),
      ("C2 (Proficiency)", "C2 (Proficiency)")
   )
   
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="languages")
   language = models.CharField(max_length=56, choices=LANGUAGE_CHOICES)
   level = models.CharField(max_length=128, choices=LEVEL_CHOICES)


class WorkerExperience(BaseModel):
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="work_experience")
   position = models.CharField(max_length=128)
   organization = models.CharField(max_length=128)
   organization_category = models.ForeignKey(Category, on_delete=models.CASCADE)
   start_date = models.DateField()
   end_date = models.DateField(null=True, blank=True)
   is_active = models.BooleanField(default=False) #hozirgacha shu kompaniyada ishlaydimi


@receiver(post_save, sender=WorkerExperience)
def my_handler(sender, created, instance, **kwargs):
   if created:
      worker = instance.worker
      worker.has_experience = True
      worker.save()

@receiver(pre_delete, sender=WorkerExperience)
def my_handler(sender, instance, **kwargs):
   worker = instance.worker
   if worker.work_experience:
      worker.has_experience = True
   else:
      worker.has_experience = False
   worker.save()


class WorkerPortfoilo(BaseModel):
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="portfoilo")
   image = models.ImageField(upload_to="images/")
   description = models.TextField()

@receiver(post_save, sender=WorkerPortfoilo)
def my_handler(sender, created, instance, **kwargs):
   if created:
      worker = instance.worker
      worker.has_portfoilo = True
      worker.save()

@receiver(pre_delete, sender=WorkerPortfoilo)
def my_handler(sender, instance, **kwargs):
   worker = instance.worker
   if worker.portfoilo:
      worker.has_portfoilo = True
   else:
      worker.has_portfoilo = False
   worker.save()
   
   
class ApplicationFeedback(BaseModel):
   class FeedbackProvider(models.TextChoices):
      WORKER = 'worker'
      COMPANY = 'company'
   
   worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="feedback")
   company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="feedback")
   provider = models.CharField(max_length=128, choices=FeedbackProvider.choices)
   text = models.TextField()
   rating = models.IntegerField()
   
   class Meta:
      unique_together = ("worker", "company", "provider")
   


   