from django.shortcuts import render,redirect,get_object_or_404
from .models import User,Employer,AdminUser,JobPost,JobApplication
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Count
import requests
def home(request):
    return render(request, 'index.html')
def register(request):
    error = ""
    success = ""
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        elif User.objects.filter(email=email).exists():
            error = "Email already registered."
        else:
            User.objects.create(username=username, email=email, password=password)
            success = "Registration successful. Please login."
    return render(request, "Register.html", {"error": error, "success": success})
def login(request):
    return render(request, 'Login.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('user_dashboard')
        except User.DoesNotExist:
            return render(request, 'Login.html', {'error': 'Invalid credentials'})

def user_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    username = request.session.get('username')
    jobs = JobPost.objects.all()

    # Filters
    post = request.GET.get('post')
    location = request.GET.get('location')
    company = request.GET.get('company')

    if post:
        jobs = jobs.filter(job_title__icontains=post)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if company:
        jobs = jobs.filter(company_name__icontains=company)

    return render(request, 'user_dashboard.html', {'username': username, 'jobs': jobs})

def apply_job(request, job_id):
    if 'user_id' not in request.session:
        return redirect('login')

    job = get_object_or_404(JobPost, id=job_id)
    user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        education = request.POST.get('education')
        experience = request.POST.get('experience')
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter')
        why_interested = request.POST.get('why_interested')
        strength = request.POST.get('strength')
        agree_terms = request.POST.get('agree_terms') == 'on'

        if not agree_terms:
            messages.error(request, 'You must agree to the terms.')
            return redirect('apply_job', job_id=job.id)

        JobApplication.objects.create(
            job=job,
            user=user,  # ✅ Save the logged-in user
            name=name,
            email=email,
            phone=phone,
            education=education,
            experience=experience,
            resume=resume,
            cover_letter=cover_letter,
            why_interested=why_interested,
            strength=strength,
            agree_terms=agree_terms
        )
        messages.success(request, 'Your application was submitted successfully!')
        return redirect('user_dashboard')

    return render(request, 'apply_job.html', {'job': job})

def my_applications(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session.get('user_id')
    applications = JobApplication.objects.filter(user_id=user_id).order_by('-submitted_at')
    return render(request, 'my_applications.html', {'applications': applications})
def logout_user(request):
    request.session.flush()
    return redirect('login')
def logout_employer(request):
    request.session.flush()
    return redirect('employerlogin')
def logout_admin(request):
    request.session.flush()
    return redirect('adminlogin')
def employer_login(request):
    error = ""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            employer = Employer.objects.get(username=username, password=password, is_active=True)
            request.session['employer_id'] = employer.id
            request.session['employer_name'] = employer.company_name
           
            return redirect('employer_dashboard')  # Your target view
        except Employer.DoesNotExist:
            error = "Invalid credentials or account inactive."
    
    return render(request, 'employers_login.html', {'error': error})
def employer_dashboard(request):
    if 'employer_id' not in request.session:
        return redirect('employerlogin')
    username = request.session.get('username')
    return render(request, 'employer_dashboard.html', {'username': username})
def employerlogin(request):
    return render(request, 'employers_login.html')
def view_applications(request):
    if 'employer_id' not in request.session:
        return redirect('employer_login')

    employer_id = request.session['employer_id']
    employer = get_object_or_404(Employer, id=employer_id)

    jobs = JobPost.objects.filter(employer=employer)
    applications = JobApplication.objects.filter(job__in=jobs).order_by('-submitted_at')

    # ✅ Pass choices to template
    status_choices = JobApplication._meta.get_field('status').choices

    return render(request, 'employer_applications.html', {
        'applications': applications,
        'status_choices': status_choices,
    })
def view_application_detail(request, app_id):
    if 'employer_id' not in request.session:
        return redirect('employer_login')

    application = get_object_or_404(JobApplication, id=app_id)
    return render(request, 'application_detail.html', {'application': application})


def update_application_status(request, app_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        application = get_object_or_404(JobApplication, id=app_id)
        application.status = status
        application.save()
        messages.success(request, f"Application status updated to '{status}'!")
    return redirect('view_applications')
def admin_login(request):
    error = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            admin = AdminUser.objects.get(username=username, password=password)
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard')
        except AdminUser.DoesNotExist:
            error = "Invalid login credentials."
    
    return render(request, 'admin_login.html', {'error': error})
def admin_dashboard(request):
    # Step 1: Check if admin is logged in
    if 'admin_id' not in request.session:
        return redirect('adminlogin')

    # Step 2: Retrieve admin details
    admin_id = request.session.get('admin_id')
    admin = AdminUser.objects.get(id=admin_id)
    username = admin.username

    # Step 3: Aggregate job count per employer
    job_data = JobPost.objects.values('employer__company_name') \
                              .annotate(job_count=Count('id')) \
                              .order_by('-job_count')

    # Step 4: Prepare data for Chart.js
    employer_names = [entry['employer__company_name'] for entry in job_data]
    job_counts = [entry['job_count'] for entry in job_data]

    # Step 5: Render the dashboard with chart data
    return render(request, 'admin_dashboard.html', {
        'username': username,
        'employer_names': employer_names,
        'job_counts': job_counts
    })

def adminlogin(request):
    return render(request, 'admin_login.html')
def post_job(request):
    if 'employer_id' not in request.session:
        return redirect('employerlogin')

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        job_description = request.POST.get('job_description')
        company_name = request.POST.get('company_name')

        if job_title and location and salary and job_description and company_name:
            try:
                employer = Employer.objects.get(id=request.session['employer_id'])
                JobPost.objects.create(
                    employer=employer,
                     company_name=company_name,
                    job_title=job_title,
                    location=location,
                    salary=salary,
                    job_description=job_description
                )
                messages.success(request, "✅ Job added successfully!")
                return redirect('employer_dashboard')
            except:
                messages.error(request, "❌ Failed to add job. Please try again.")
        else:
            messages.error(request, "❌ All fields are required.")

    return render(request, 'employer_dashboard.html')
# View for job listings

def job_list_view(request):
    if 'employer_id' not in request.session:
        return redirect('employerlogin')  # Redirect if not logged in

    employer_id = request.session['employer_id']
    jobs = JobPost.objects.filter(employer_id=employer_id).order_by('-posted_on')  # Filter by employer

    return render(request, 'joblist.html', {'jobs': jobs})


def job_view(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'job_detail.html', {'job': job})


def job_edit(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if 'employer_id' not in request.session:
        return redirect('employerlogin')
    if job.employer.id != request.session['employer_id']:
        messages.error(request, "❌ You are not authorized to edit this job.")
        return redirect('job_list_view')

    if request.method == 'POST':
        job.job_title = request.POST.get('job_title')
        job.location = request.POST.get('location')
        job.salary = request.POST.get('salary')
        job.company_name = request.POST.get('company_name')  # ✅
        job.job_description = request.POST.get('job_description')
        job.save()
        messages.success(request, "✅ Job updated successfully!")
        return redirect('job_list_view')

    return render(request, 'edit_job.html', {'job': job})

def job_delete(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    # Ensure only the owner (employer) or admin can delete
    if 'employer_id' not in request.session:
        return redirect('employerlogin')
    if job.employer.id != request.session['employer_id']:
        messages.error(request, "❌ You are not authorized to delete this job.")
        return redirect('job_list_view')

    job.delete()
    messages.success(request, "✅ Job  deleted successfully!")
    return redirect('job_list_view')
def user_list(request):
    if 'admin_id' not in request.session:
        return redirect('adminlogin')
    users = User.objects.all()
    return render(request, 'admin_user_list.html', {'users': users})

def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.password = request.POST.get('password')  # Not secure; consider hashing
        user.save()
        return redirect('user_list')  # or wherever you list users
    return render(request, 'admin_user_edit.html', {'user': user})
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect('user_list')
def employer_list(request):
    if 'admin_id' not in request.session:
        return redirect('adminlogin')
    employers = Employer.objects.all()
    return render(request, 'admin_employer_list.html', {'employers': employers})


def employer_edit(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    if request.method == 'POST':
        employer.company_name = request.POST['company_name']
        employer.email = request.POST['email']
        employer.username = request.POST['username']
        employer.password = request.POST['password']
        employer.is_active = 'is_active' in request.POST
        employer.save()
        messages.success(request, "Employer updated successfully!")
        return redirect('employer_list')
    return render(request, 'admin_employer_edit.html', {'employer': employer})


def employer_delete(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    employer.delete()
    messages.success(request, "Employer deleted successfully!")
    return redirect('employer_list')


def employer_add(request):
    if request.method == 'POST':
        Employer.objects.create(
            company_name=request.POST['company_name'],
            email=request.POST['email'],
            username=request.POST['username'],
            password=request.POST['password'],
            is_active='is_active' in request.POST
        )
        messages.success(request, "New employer added successfully!")
        return redirect('employer_list')
    return render(request, 'admin_employer_add.html')
def admin_job_list(request):
    jobs = JobPost.objects.all().order_by('-posted_on')
    return render(request, 'admin_job_list.html', {'jobs': jobs})

# View individual job
def admin_job_view(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'admin_job_view.html', {'job': job})

# Edit job
def admin_job_edit(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    if request.method == 'POST':
        job.company_name = request.POST['company_name']
        job.job_title = request.POST['job_title']
        job.location = request.POST['location']
        job.salary = request.POST['salary']
        job.job_description = request.POST['job_description']
        job.save()
        messages.success(request, "Job updated successfully.")
        return redirect('admin_job_list')
    return render(request, 'admin_job_edit.html', {'job': job})

# Delete job
def admin_job_delete(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('admin_job_list')
def admin_applications(request):
    applications = JobApplication.objects.all().order_by('-submitted_at')
    return render(request, 'admin_applications.html', {'applications': applications})


def admin_application_view(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    return render(request, 'admin_application_detail.html', {'application': application})


def admin_application_edit(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)

    if request.method == 'POST':
        application.name = request.POST.get('name')
        application.email = request.POST.get('email')
        application.phone = request.POST.get('phone')
        application.education = request.POST.get('education')
        application.experience = request.POST.get('experience')
        application.cover_letter = request.POST.get('cover_letter')
        application.why_interested = request.POST.get('why_interested')
        application.strength = request.POST.get('strength')
        application.status = request.POST.get('status')
        application.save()
        messages.success(request, 'Application updated successfully.')
        return redirect('admin_applications')

    return render(request, 'admin_application_edit.html', {'application': application})


def admin_application_delete(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    application.delete()
    messages.success(request, 'Application deleted successfully.')
    return redirect('admin_applications')

def external_jobs(request):
    query = request.GET.get('search', 'python developer')
    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": "0715debd5emshf927992dc01bc0ep157d25jsn80ca90d5dc72",  # 🔑 Replace with your key
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        jobs = data.get("data", [])
    except Exception as e:
        print("API Error:", e)
        jobs = []

    return render(request, 'external_jobs.html', {'jobs': jobs, 'query': query})
