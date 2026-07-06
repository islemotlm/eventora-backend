from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'avatar', 'phone', 'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2', 'role', 'phone']

    def validate_email(self, value):
        value = (value or '').strip().lower()
        if not value:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_role(self, value):
        if value == 'admin':
            raise serializers.ValidationError('Admin accounts cannot self-register. Contact an existing administrator.')
        if value not in {'client', 'organizer', 'participant'}:
            raise serializers.ValidationError('Invalid role.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        # New accounts are inactive until admin approves them.
        user.is_active = False
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Allow login with email: look up the username from the email and swap it
        # in so Django's authenticate() finds the account normally.
        login_value = attrs.get(self.username_field, '')
        if login_value and '@' in login_value:
            user_by_email = User.objects.filter(email__iexact=login_value).first()
            if user_by_email:
                attrs[self.username_field] = user_by_email.username

        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed:
            # Give a clearer message if the account exists but is inactive.
            lookup = attrs.get(self.username_field, '')
            user = (
                User.objects.filter(username=lookup).first()
                or User.objects.filter(email__iexact=login_value).first()
            )
            if user and not user.is_active and user.check_password(attrs.get('password', '')):
                raise exceptions.AuthenticationFailed(
                    'Your account is pending administrator approval.',
                    code='account_pending_approval',
                )
            raise
        data['user'] = UserSerializer(self.user).data
        return data
