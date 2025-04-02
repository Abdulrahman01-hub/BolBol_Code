from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import AdvertisementListAPI, AdvertisementDetailAPI
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.home, name='home'),
    path('ads/', views.advertisement_list, name='ads'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search_results, name='search_results'),
    path('ad/<int:id>/', views.advertisement_detail, name='ad_detail'),
    path('add-ad/', views.add_advertisement, name='add_advertisement'),
    path('kategori/<str:category>/', views.category_ads, name='category_ads'),
    path(
        'login/',
        LoginView.as_view(template_name='login.html', redirect_authenticated_user=True),
        name='login'
    ),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('toggle_favorite/<int:ad_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('ad/<int:ad_id>/comment/', views.add_comment, name='add_comment'),
    path('delete-ad/<int:ad_id>/', views.delete_advertisement, name='delete_advertisement'),
    path('toggle_like/<int:ad_id>/', views.toggle_like, name='toggle_like'),
    path('share/<int:ad_id>/', views.share_advertisement, name='share_advertisement'),
    path('api/ads/', AdvertisementListAPI.as_view(), name='api_ads'),
    path('api/ads/<int:ad_id>/', AdvertisementDetailAPI.as_view(), name='api_ad_detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)