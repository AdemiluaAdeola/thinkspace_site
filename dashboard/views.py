from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from core.models import *
from core.forms import *
from django.db.models import Q, Count, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from decimal import Decimal
from user.models import User
import uuid
import random

# Create your views here.
def is_admin(user):
    return user.is_staff or user.is_superuser

def index(request):
    context = {
        'total_users': User.objects.count(),
        'total_webinars': Webinar.objects.count(),
        'total_blogs': Blog.objects.count(),
        'published_blogs': Blog.objects.filter(is_verified=True).count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

# In your views.py
def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    authors = User.objects.filter(blog__isnull=False).distinct()
    
    context = {
        'blogs': blogs,
        'categories': categories,
        'authors': authors,
    }
    return render(request, 'dashboard/blog.html', context)

# In your views.py
def webinar(request):
    webinars = Webinar.objects.all().order_by('-start_datetime')
    hosts = User.objects.filter(hosted_webinars__isnull=False).distinct()
    
    context = {
        'webinars': webinars,
        'hosts': hosts,
    }
    return render(request, 'dashboard/webinar_management.html', context)

# In your views.py
def user(request):
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
    }
    return render(request, 'dashboard/user_management.html', context)