from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField



class Advertisement(models.Model):
    CATEGORY_CHOICES = [
        ('Neqliyat', 'Neqliyat'),
        ('Daşinmaz Emlak', 'Daşinmaz Emlak'),
        ('Geyim', 'Geyim'),
        ('İş İlanlari', 'İş İlanlari'),
        ('Elektronik', 'Elektronik'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('sold', 'Satipldi'),
        ('pending', 'Beklemede'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='advertisements')
    favorites = models.ManyToManyField(User, related_name='favorites', blank=True)
    liked_by = models.ManyToManyField(User, related_name='liked_ads', blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)
    phone_number = PhoneNumberField(null=True, blank=True)  


    def __str__(self):
        return self.title

    def like_count(self):
        return self.liked_by.count()

    def favorite_count(self):
        return self.favorites.count()

    def increment_views(self):
        self.views_count += 1
        self.save()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'advertisement')

    def __str__(self):
        return f"{self.user.username} liked {self.advertisement.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'advertisement')

    def __str__(self):
        return f"{self.user.username} added {self.advertisement.title} to favorites"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AdvertisementImage(models.Model):
    advertisement = models.ForeignKey(
        Advertisement, related_name='images', on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='ads/', blank=True, null=True)

    def __str__(self):
        return f"Image for {self.advertisement.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Comment(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Yorum: {self.content[:30]}..."

class Rating(models.Model):
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True) 
    def __str__(self):
        return f"{self.user.username} rated {self.ad.title} with {self.rating}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message