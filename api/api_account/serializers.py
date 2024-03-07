from rest_framework import serializers
from account.models import User
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'is_email_verified', ]

    def create(self, validated_data):
        """ Creates and returns a new user """

        # Validating Data
        user = User(
        email=validated_data['email'],
        password=validated_data['password'],)
        user.set_password(validated_data['password'])
        user.save()

        return user


class ResetPasswordSerializer(serializers.Serializer):
    
    new_password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError("passwords should match")
        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context['request'].user
        if not check_password(data['old_password'], user.password):
            raise serializers.ValidationError({'old_password': 'Wrong password.'})
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({'new_password': 'new password should not match with old password'})
        if data['new_password'] != data['confirmed_password']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return data
    
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name','last_name','zip_code','address','phone_no', ]
