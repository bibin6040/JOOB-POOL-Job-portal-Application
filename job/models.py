from django.db import models
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)  # In real apps, hash this

    def __str__(self):
        return self.username
class Employer(models.Model):
    company_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=100)  # Optional: Use hash in real apps
    is_active = models.BooleanField(default=True)  # In case admin wants to deactivate them

    def __str__(self):
        return self.company_name
class AdminUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=100)  # You can hash this if needed

    def __str__(self):
        return self.username
class JobPost(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)  # Link to employer
    company_name = models.CharField(max_length=255) 
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    job_description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.employer.company_name}"
class JobApplication(models.Model):
    job = models.ForeignKey('JobPost', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # ✅ This is important
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    education = models.TextField(default='Not Provided')
    experience = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)

    why_interested = models.TextField(default='Not Provided')
    strength = models.TextField(default='Not Provided')
    agree_terms = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
        ('Accepted', 'Accepted'),
    ], default='Pending')

    def __str__(self):
        return f"{self.name} - {self.job.job_title}"
# Create your models here.
