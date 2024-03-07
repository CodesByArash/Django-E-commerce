from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from account.models import *
from .serializers import *
from .utils import *


class RevokeToken(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        request.auth.delete()
        return Response(status=204)
    
class Register(APIView):

    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data = data)
            if serializer.is_valid():
                user = serializer.save()

                email_otp = EmailOTP(user=user, email_verification_code=get_unique_code(user),)

                
                current_site = get_current_site(
                request=request).domain
                relativeLink = reverse(
                'request-verification', kwargs={'token': email_otp.email_verification_code })

                redirect_url = request.data.get('redirect_url', '')
                absurl = 'http://'+current_site + relativeLink
                email_body = 'Hello, \n Use link below to verify your email  \n' + \
                absurl+"?redirect_url="+redirect_url
                data = {'email_body': email_body, 'to_emails': [user.email,],
                    'email_subject': 'Reset your passsword'}                

                send_email(data)

                return Response({
                    'status':200,
                    'message':'registered succesfully check email',
                    'data':serializer.data,
                })
            
            return Response({
                'status':400,
                'message':'something went wrong',
                'data': serializer.errors
            })
        
        except Exception as e:
            return Response({'message': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET",])
@permission_classes([IsAuthenticated])
def request_email_verification(request):
    user = request.user
    if user.is_email_verified:
        return Response({'message': 'your email was verified'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        email_otp                         = EmailOTP.objects.get(user=user)
        email_otp.email_verification_code = get_unique_code()
        email_otp.expiration_date         = email_otp.return_date_time()
        email_otp.save()

    except EmailOTP.DoesNotExist:
        email_otp = EmailOTP(user=user, email_verification_code=get_unique_code(user),)
        email_otp.save()
    
    
    current_site = get_current_site(
    request=request).domain
    relativeLink = reverse(
    'password-reset-confirm', kwargs={'token': email_otp.email_verification_code })

    redirect_url = request.data.get('redirect_url', '')
    absurl = 'http://'+current_site + relativeLink
    email_body = 'Hello, \n Use link below to verify your email  \n' + \
    absurl+"?redirect_url="+redirect_url
    data = {'email_body': email_body, 'to_emails': [user.email,],
    'email_subject': 'Reset your passsword'}                

    send_email(data)

    return Response({'message': 'email was sent to your email address'}, status=status.HTTP_202_ACCEPTED)
        
        


@api_view(["POST",])
def verify_email(request,token):
    try:
        email_otp = EmailOTP.objects.get(email_verification_code=token)
        if email_otp.user.is_email_verified:
            return Response({'message': 'your email is already verified'}, status=status.HTTP_400_BAD_REQUEST)
    
        if email_otp.is_expired():
            return Response({'message': 'expired OTP try getting a new OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = email_otp.user
        user.is_email_verified = True
        user.save()
        # email_otp.delete()
        return Response({'message': 'email verified succesfully'}, status=status.HTTP_202_ACCEPTED)

    except EmailOTP.DoesNotExist:
        return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


 

class ForgetPassword(APIView):

    def get(self, request):
        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'reset-password', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {'email_body': email_body, 'to_emails': [user.email,],
                'email_subject': 'Reset your passsword'}
            send_email(data)
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'failed':'User not Found'},status=status.HTTP_404_NOT_FOUND)
        

class ResetPassword(APIView):

    def put(self,request, uidb64, token):
        id = smart_str(urlsafe_base64_decode(uidb64))
        try:
            user = User.objects.get(id=id)
        except:
            return Response({'failed':'User not Found'},status=status.HTTP_404_NOT_FOUND)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'failed':'Invalid token'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = ResetPasswordSerializer(data= request.data)

        if serializer.is_valid():
            # Check old password
            # if not self.object.check_password(serializer.data.get("old_password")):
            #     return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "password updated successfully"})
        else:
            return Response({"message": "failed", "details": serializer.errors})
    
     


class UpdateProfile(UpdateAPIView):
    serializer_class=UpdateProfileSerializer
    permission_classes=[IsAuthenticated]