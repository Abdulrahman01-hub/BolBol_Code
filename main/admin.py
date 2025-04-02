from django.contrib import admin
from .models import Advertisement, Contact, Like, Favorite, AdvertisementImage, UserProfile, Comment, Rating, Notification


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'category', 'status')
    list_filter = ('category', 'status', 'created_at')
    ordering = ('-created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'advertisement', 'created_at')
    search_fields = ('user__username', 'advertisement__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'advertisement', 'created_at')
    search_fields = ('user__username', 'advertisement__title')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(AdvertisementImage)
class AdvertisementImageAdmin(admin.ModelAdmin):
    list_display = ('advertisement', 'image')
    search_fields = ('advertisement__title',)
    list_filter = ('advertisement__category',)
    ordering = ('-advertisement__created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_image')
    search_fields = ('user__username',)
    ordering = ('user__username',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user', 'content', 'created_at')
    search_fields = ('ad__title', 'user__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user', 'rating', 'comment', 'created_at')
    search_fields = ('ad__title', 'user__username', 'comment')
    list_filter = ('created_at', 'rating')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'created_at')
    ordering = ('-created_at',)