from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .forms import CreateNewPost, UpdatePost, CommentSection, CreateWebinar, WebinarRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(response):
    posts = Blog.objects.filter(is_verified=True).order_by('-created_at')[:3]
    webinars=Webinar.objects.all().order_by('-created_at')[:3]

    context = {
        'posts':posts,
        'webinars':webinars
    }

    return render(response, 'core/index.html', context)

class blog(ListView):
    model = Blog
    template_name = 'blog/index.html'
    ordering = ['-created_at']
    paginate_by = 10

class webinar(ListView):
    model = Webinar
    template_name = 'webinar/index.html'
    ordering = ['-created_at']
    paginate_by = 10
    
class create(CreateView):
    model = Blog
    template_name = 'blog/create.html'
    form_class = CreateNewPost

class webinar_create(CreateView):
    model = Webinar
    template_name = 'webinar/create.html'
    form_class = CreateWebinar

class update(UpdateView):
    model = Blog
    template_name = 'blog/update.html'
    form_class = UpdatePost

class webinar_update(UpdateView):
    model = Webinar
    template_name = 'webinar/create.html'
    form_class = CreateWebinar

class delete(DeleteView):
    model = Blog
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('index')

class webinar_delete(DeleteView):
    model = Blog
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('webinar')

@login_required(login_url='login')
def blogpost(response, pk):
    blog = Blog.objects.get(id=pk)
    if response.method == "POST":
        form = CommentSection(response.POST)
        if form.is_valid():
            n = f"{response.user.first_name} {response.user.last_name}"
            c = form.cleaned_data["body"]
            Comment.objects.create(
                blog=blog,
                name=n,
                body=c
            )
            return redirect('blogpost', pk=pk)

        else:
            print("invalid code")

    else:
        form = CommentSection()
        return render(response, 'blog/post.html', {'blog':blog, 'form':form})
    
def about(response):
    return render(response, 'core/about.html')

@login_required(login_url='login')
def webinar_detail(request, pk):
    webinar = get_object_or_404(Webinar, pk=pk)
    
    # Check if user is already registered
    is_registered = False
    if request.user.is_authenticated:
        is_registered = WebinarRegistration.objects.filter(
            webinar=webinar, 
            email=request.user.email
        ).exists()
    
    # Handle registration form submission
    if request.method == 'POST':
        form = WebinarRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.webinar = webinar
            
            # If user is authenticated, prefill name and email
            if request.user.is_authenticated:
                registration.full_name = f"{request.user.first_name} {request.user.last_name}"
                registration.email = request.user.email
            
            registration.save()
            messages.success(request, 'Your registration was successful!')
            return redirect('webinar_detail', pk=webinar.pk)
    else:
        # Prefill form for authenticated users
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email
            }
        form = WebinarRegistrationForm(initial=initial_data)
    
    context = {
        'webinar': webinar,
        'form': form,
        'is_registered': is_registered,
        'now': timezone.now(),
    }
    return render(request, 'webinar/details.html', context)