from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, authenticate, login
from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from .models import Gig
from .models import Application
from .serializers import GigSerializer
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import GigForm

def home(request):
    gigs = Gig.objects.all()
    return render(request, 'home.html', {'gigs': gigs})

def gig_detail(request, gig_id):
    gig = Gig.objects.get(id=gig_id)
    return render(request, 'gig_detail.html', {'gig': gig})

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})
        user = User.objects.create_user(username=email, email=email, password=password, role=role, first_name=name)
        return render(request, 'register.html', {'success': 'Registration successful! You can now log in.'})
    return render(request, 'register.html')

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            if user.role == 'Provider':
                return redirect('provider_dashboard')
            else:
                return redirect('seeker_dashboard')
        else:
            error = 'Invalid credentials'
    return render(request, 'login.html', {'next': next_url, 'error': error})

# Register API
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Logout API
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


# Delete Account API
class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        request.user.delete()


class GigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, gig_id=None):
        if gig_id:
            gig = Gig.objects.filter(id=gig_id).first()
            if not gig:
                return Response({"error": "Gig not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(GigSerializer(gig).data)
        search_query = request.query_params.get('search', '')
        gigs = Gig.objects.filter(Q(title__icontains=search_query))
        return Response(GigSerializer(gigs, many=True).data)

    def post(self, request):
        serializer = GigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, gig_id):
        gig = Gig.objects.filter(id=gig_id, created_by=request.user).first()
        if not gig:
            return Response({"error": "Gig not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        serializer = GigSerializer(gig, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, gig_id):
        gig = Gig.objects.filter(id=gig_id, created_by=request.user).first()
        if not gig:
            return Response({"error": "Gig not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        gig.delete()
        return Response({"message": "Gig deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

@login_required
def provider_dashboard(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'provider_dashboard.html', {'gigs': gigs})

@login_required
def seeker_dashboard(request):
    favorites = request.user.favorites.all()
    applications = Application.objects.filter(seeker=request.user)
    return render(request, 'seeker_dashboard.html', {'favorites': favorites, 'applications': applications})

@login_required
def favorite_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    request.user.favorites.add(gig)
    return redirect('seeker_dashboard')

@login_required
def apply_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    Application.objects.get_or_create(gig=gig, seeker=request.user)
    return redirect('seeker_dashboard')

@login_required
def create_gig(request):
    if request.method == 'POST':
        form = GigForm(request.POST)
        if form.is_valid():
            gig = form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('home')
    else:
        form = GigForm()
    return render(request, 'create_gig.html', {'form': form})
