from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Advertisement


class AdvertisementModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.advertisement = Advertisement.objects.create(
            title="Test Advertisement",
            description="Test Description",
            price=100,
            user=cls.user
        )
        
    def test_advertisement_list_view(self):
        url = reverse('ads')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Advertisement') 

    def test_advertisement_view(self):
        url = reverse('ad_detail', args=[self.advertisement.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Advertisement')

    def test_advertisement_creation(self):
        advertisement = Advertisement.objects.create(
            title="New Ad",
            description="New Description",
            price=200,
            user=self.user
        )
        self.assertEqual(advertisement.title, 'New Ad')
        self.assertEqual(advertisement.user, self.user)
    
    def test_advertisement_like(self):
        advertisement = Advertisement.objects.create(
            title="Liked Ad",
            description="Liked Ad Description",
            price=150,
            user=self.user
        )
        advertisement.liked_by.add(self.user)
        self.assertEqual(advertisement.liked_by.count(), 1)

    def test_advertisement_favorite(self):
        advertisement = Advertisement.objects.create(
            title="Favorite Ad",
            description="Favorite Ad Description",
            price=250,
            user=self.user
        )
        advertisement.favorites.add(self.user) 
        self.assertEqual(advertisement.favorites.count(), 1)