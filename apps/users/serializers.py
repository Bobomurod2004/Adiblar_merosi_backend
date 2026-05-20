from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import UserProfile, Bookmark


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Token ichiga qo'shimcha ma'lumot qo'shish (ixtiyoriy)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    """Django User"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserProfileSerializer(serializers.ModelSerializer):
    """User Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'user', 'avatar', 'bio', 'phone_number', 'telegram_username', 'website', 'location',
            'article_count', 'joined_date', 'receive_email_notifications'
        )
        read_only_fields = ('user', 'article_count', 'joined_date')


class UserRegisterSerializer(serializers.ModelSerializer):
    """User Registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    telegram_username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'telegram_username')
    
    def validate(self, data):
        """Passwords birini tekshirish"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Parollar mos emas!")
        return data
    
    def create(self, validated_data):
        """Create user with profile"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        telegram_username = validated_data.pop('telegram_username', '')
        
        user = User.objects.create_user(**validated_data, password=password)
        UserProfile.objects.create(user=user, telegram_username=telegram_username)
        return user


class BookmarkSerializer(serializers.ModelSerializer):
    """Bookmarks - Saved works"""
    work_title = serializers.CharField(source='work.title', read_only=True)
    work_writer = serializers.CharField(source='work.writer.full_name', read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ('id', 'work', 'work_title', 'work_writer', 'note', 'created_at')
        read_only_fields = ('created_at',)
