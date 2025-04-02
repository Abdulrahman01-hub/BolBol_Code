from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Advertisement, Contact, Favorite, Comment, Like, Rating, Notification, UserProfile
from .forms import AdvertisementForm, CommentForm
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import AdvertisementSerializer, UserProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

def send_comment_email(ad_user, ad_title, comment_user):
    subject = f"New Comment: {ad_title}"
    message = f"The user {comment_user.username} commented on your advertisement."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [ad_user.email]
    send_mail(subject, message, from_email, recipient_list)

def home(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'my_template.html', {'advertisements': advertisements})

def advertisement_detail(request, id):
    ad = get_object_or_404(Advertisement, id=id)
    ad.increment_views()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ad = ad
            comment.user = request.user
            comment.save()

            create_notification(ad.user, f"{request.user.username} commented on your advertisement.")
            send_comment_email(ad.user, ad.title, request.user)

            return redirect('ad_detail', id=ad.id)
    else:
        comment_form = CommentForm()

    comments = Comment.objects.filter(ad=ad).order_by('-created_at')
    return render(request, 'advertisement_detail.html', {'ad': ad, 'comments': comments, 'comment_form': comment_form})

def advertisement_list(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'my_template.html', {'advertisements': advertisements})

def about(request):
    about_info = "Bolbol is a platform where users can share their advertisements and search for the product or service of their dreams."
    return render(request, 'about.html', {'about_info': about_info})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        Contact.objects.create(name=name, email=email, message=message)
        return redirect('home')
    return render(request, 'contact.html')

def search_results(request):
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)

    advertisements = Advertisement.objects.filter(title__icontains=query)
    if category:
        advertisements = advertisements.filter(category__icontains=category)

    if min_price:
        advertisements = advertisements.filter(price__gte=min_price)
    if max_price:
        advertisements = advertisements.filter(price__lte=max_price)

    return render(request, 'advertisement_list.html', {
        'advertisements': advertisements,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price
    })

@login_required
def add_advertisement(request):
    years = list(range(2005, 2025))
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.user = request.user
            advertisement.save()
            return redirect('ads')
    else:
        form = AdvertisementForm()

    return render(request, 'add_advertisement.html', {'form': form, 'years': years})

@login_required
def favorites_view(request):
    user = request.user
    favorites = Advertisement.objects.filter(favorites=user)
    return render(request, 'favorites.html', {'favorites': favorites})

def category_ads(request, category):
    advertisements = Advertisement.objects.filter(category=category)
    return render(request, 'my_template.html', {'advertisements': advertisements})

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('profile')

    def get_success_url(self):
        return self.request.GET.get('next') or self.success_url

@login_required
def toggle_favorite(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, advertisement=ad)

    if created:
        create_notification(ad.user, f"{request.user.username} added your advertisement to favorites.")
    
    if not created:
        favorite.delete()
        status = "unfavorited"
    else:
        status = "favorited"

    if request.is_ajax():
        return JsonResponse({'status': status, 'ad_id': ad_id})
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def add_comment(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ad = ad
            comment.user = request.user
            comment.save()

            create_notification(ad.user, f"{request.user.username} commented on your advertisement.")
            send_comment_email(ad.user, ad.title, request.user)

            return redirect('ad_detail', id=ad.id)
    else:
        comment_form = CommentForm()

    comments = Comment.objects.filter(ad=ad).order_by('-created_at')
    return render(request, 'advertisement_detail.html', {'ad': ad, 'comments': comments, 'comment_form': comment_form})

@login_required
def delete_advertisement(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.user == ad.user:
        ad.delete()
        return redirect('ads')
    else:
        return redirect('ad_detail', id=ad.id)

@login_required
def toggle_like(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    like, created = Like.objects.get_or_create(user=request.user, advertisement=ad)

    if not created:
        like.delete()
        status = "unliked"
    else:
        status = "liked"

    if request.is_ajax():
        return JsonResponse({'status': status, 'ad_id': ad_id})
    return redirect('home')

@login_required
def add_rating(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        rating = Rating.objects.create(ad=ad, user=request.user, rating=rating_value, comment=comment)
        return redirect('ad_detail', id=ad.id)

    return render(request, 'advertisement_detail.html', {'ad': ad})

def share_advertisement(request, ad_id):
    advertisement = get_object_or_404(Advertisement, id=ad_id)
    return HttpResponse(f"{advertisement.title} has been shared!")

class AdvertisementListAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get(self, request):
        ads = Advertisement.objects.all()

        category = request.query_params.get('category', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        search_query = request.query_params.get('search', None)
        ordering = request.query_params.get('ordering', None)

        if category:
            ads = ads.filter(category__icontains=category)
        if min_price:
            ads = ads.filter(price__gte=min_price)
        if max_price:
            ads = ads.filter(price__lte=max_price)
        if search_query:
            ads = ads.filter(title__icontains=search_query) | ads.filter(description__icontains=search_query)
        if ordering:
            ads = ads.order_by(ordering)

        serializer = AdvertisementSerializer(ads, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdvertisementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdvertisementDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, ad_id):
        try:
            ad = Advertisement.objects.get(id=ad_id)
        except Advertisement.DoesNotExist:
            return Response({"error": "Advertisement not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdvertisementSerializer(ad)
        return Response(serializer.data)

    def put(self, request, ad_id):
        try:
            ad = Advertisement.objects.get(id=ad_id, user=request.user)
        except Advertisement.DoesNotExist:
            return Response({"error": "Advertisement not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdvertisementSerializer(ad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ad_id):
        try:
            ad = Advertisement.objects.get(id=ad_id, user=request.user)
        except Advertisement.DoesNotExist:
            return Response({"error": "Advertisement not found or not authorized"}, status=status.HTTP_404_NOT_FOUND)

        ad.delete()
        return Response({"message": "Advertisement deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class UserProfileView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user.profile