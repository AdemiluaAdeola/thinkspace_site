from django.urls import path
from .views import *
from user.views import user_profile

urlpatterns = [
    path('', index, name='dashboard'),
    path('blog/', blog, name='blog_management'),
    path('webinar/', webinar, name='webinar_management'),
    path('user/', user, name='user_management'),
    path('user/<int:pk>', user_profile, name='user_profile'),
]
