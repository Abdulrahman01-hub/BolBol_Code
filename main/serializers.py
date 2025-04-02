from rest_framework import serializers
from .models import Advertisement, UserProfile


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Fiyat negatif olamaz.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'profile_image']