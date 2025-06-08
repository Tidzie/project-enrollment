from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import ParentRegistrationForm, ChildForm, EnrollmentForm, ParentForm
from .models import Parent, Child, Enrollment

def home(request):
    if request.user.is_authenticated:
        return redirect('enrollment:dashboard')
    return render(request, 'enrollment/landing.html')

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('enrollment:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'enrollment/login.html')

def register(request):
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Parent.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = ParentRegistrationForm()
    return render(request, 'enrollment/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get the parent object for the current user
    parent = get_object_or_404(Parent, user=request.user)
    
    # Get all children for this parent
    children = Child.objects.filter(parent=parent)
    
    # Get all enrollments for this parent's children
    enrollments = Enrollment.objects.filter(child__parent=parent)
    
    context = {
        'parent': parent,
        'children': children,
        'enrollments': enrollments,
    }
    
    return render(request, 'enrollment/dashboard.html', context)

@login_required
def add_child(request):
    # Get or create a Parent record for the logged-in user
    parent, created = Parent.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': 'Not provided',
            'address': 'Not provided'
        }
    )
    
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent
            child.save()
            messages.success(request, 'Child added successfully!')
            return redirect('dashboard')
    else:
        form = ChildForm()
    return render(request, 'enrollment/add_child.html', {'form': form})

@login_required
def enroll_child(request, child_id):
    # Get or create a Parent record for the logged-in user
    parent, created = Parent.objects.get_or_create(
        user=request.user,
        defaults={
            'phone': 'Not provided',
            'address': 'Not provided'
        }
    )
    
    try:
        child = Child.objects.get(id=child_id, parent=parent)
    except Child.DoesNotExist:
        messages.error(request, 'Child not found or you do not have permission to enroll this child.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.child = child
            enrollment.save()
            
            # Send email notification
            send_mail(
                'Enrollment Confirmation',
                f'Your child {child.first_name} has been enrolled successfully for {enrollment.class_type} starting {enrollment.enrollment_date}',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Enrollment successful! Check your email for confirmation.')
            return redirect('dashboard')
    else:
        form = EnrollmentForm()
    return render(request, 'enrollment/enroll_child.html', {'form': form, 'child': child})

# Parent CRUD Views
@login_required
def parent_list(request):
    parents = Parent.objects.all()
    return render(request, 'enrollment/parent/list.html', {'parents': parents})

@login_required
def parent_detail(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    return render(request, 'enrollment/parent/detail.html', {'parent': parent})

@login_required
def parent_create(request):
    if request.method == 'POST':
        form = ParentForm(request.POST)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.user = request.user
            parent.save()
            messages.success(request, 'Parent profile created successfully.')
            return redirect('enrollment:dashboard')
    else:
        form = ParentForm()
    return render(request, 'enrollment/parent/form.html', {'form': form, 'action': 'Create'})

@login_required
def parent_update(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    if request.method == 'POST':
        form = ParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parent profile updated successfully.')
            return redirect('parent_detail', pk=parent.pk)
    else:
        form = ParentForm(instance=parent)
    return render(request, 'enrollment/parent/form.html', {'form': form, 'action': 'Update'})

@login_required
def parent_delete(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    if request.method == 'POST':
        parent.delete()
        messages.success(request, 'Parent profile deleted successfully.')
        return redirect('parent_list')
    return render(request, 'enrollment/parent/confirm_delete.html', {'parent': parent})

# Child CRUD Views
@login_required
def child_list(request):
    children = Child.objects.filter(parent__user=request.user)
    return render(request, 'enrollment/child/list.html', {'children': children})

@login_required
def child_detail(request, pk):
    child = get_object_or_404(Child, pk=pk)
    return render(request, 'enrollment/child/detail.html', {'child': child})

@login_required
def child_create(request):
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user.parent
            child.save()
            messages.success(request, 'Child profile created successfully.')
            return redirect('enrollment:dashboard')
    else:
        form = ChildForm()
    return render(request, 'enrollment/child/form.html', {'form': form})

@login_required
def child_update(request, pk):
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, 'Child profile updated successfully.')
            return redirect('child_detail', pk=child.pk)
    else:
        form = ChildForm(instance=child)
    return render(request, 'enrollment/child/form.html', {'form': form, 'action': 'Update'})

@login_required
def child_delete(request, pk):
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        child.delete()
        messages.success(request, 'Child profile deleted successfully.')
        return redirect('child_list')
    return render(request, 'enrollment/child/confirm_delete.html', {'child': child})

# Enrollment CRUD Views
@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.filter(child__parent__user=request.user)
    return render(request, 'enrollment/enrollment/list.html', {'enrollments': enrollments})

@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    return render(request, 'enrollment/enrollment/detail.html', {'enrollment': enrollment})

@login_required
def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.save()
            messages.success(request, 'Enrollment created successfully.')
            return redirect('enrollment_detail', pk=enrollment.pk)
    else:
        form = EnrollmentForm()
    return render(request, 'enrollment/enrollment/form.html', {'form': form, 'action': 'Create'})

@login_required
def enrollment_update(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment updated successfully.')
            return redirect('enrollment_detail', pk=enrollment.pk)
    else:
        form = EnrollmentForm(instance=enrollment)
    return render(request, 'enrollment/enrollment/form.html', {'form': form, 'action': 'Update'})

@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully.')
        return redirect('enrollment_list')
    return render(request, 'enrollment/enrollment/confirm_delete.html', {'enrollment': enrollment})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        subject = f'New Contact Form Submission from {name}'
        message_body = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """
        
        try:
            send_mail(
                subject,
                message_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
        
        return redirect('enrollment:home')
    
    return redirect('enrollment:home')
