from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.generic import ListView, DetailView
from .forms import UserForm, UserProfileForm
from core.models import WebinarRegistration

# Create your views here.
def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('register')
            
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                return redirect(edit_profile)
        else:
            messages.info(request, 'Password Does Not Match')
            return redirect('register')
        
    else:
        return render(request, 'registration/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
    
    return render(request, 'registration/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request):
    user = request.user
    # Get user's registered webinars
    registered_webinars = WebinarRegistration.objects.filter(email=user.email).select_related('webinar')
    
    context = {
        'user': user,
        #'countries': countries,
        'registered_webinars': registered_webinars,
    }
    return render(request, 'user/profile.html', context)

@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)

    context = {
        'user_form': user_form,
    }
    return render(request, 'user/edit_profile.html', context)

class UserListView(ListView):
    model = User
    template_name = 'user/user_list.html'
    ordering = ['-date_joined']

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    
    context = {
        'user': user,
    }
    return render(request, 'user/profile.html', context)