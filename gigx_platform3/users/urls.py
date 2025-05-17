from django.urls import path
from . import views
from .views import RegisterView, LoginView, LogoutView, DeleteAccountView, GigView

urlpatterns = [
    path('', views.home, name='home'),
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
    path('dashboard/seeker/', views.seeker_dashboard, name='seeker_dashboard'),
    path('gigs/<int:gig_id>/favorite/', views.favorite_gig, name='favorite_gig'),
    path('gigs/<int:gig_id>/apply/', views.apply_gig, name='apply_gig'),
    path('gigs/create/', views.create_gig, name='create_gig'),
]
