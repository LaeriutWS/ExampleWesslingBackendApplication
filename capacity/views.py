import os

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class GoogleLoginApi(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        """
        POST API for google login
        """

        try:
            token = request.data.get('google_token')
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(),
                                                  os.environ['GOOGLE_OAUTH_CLIENT_ID_FRONTEND'])
            email = idinfo['email']
            user = User.objects.filter(email=email).first()
            if user is None:
                return JsonResponse({"errors": {"detail": "User does not exist"}}, status=400)

            else:
                refresh = RefreshToken.for_user(user)
                user.last_login = timezone.now()
                user.save()

                return JsonResponse(
                    {"username": user.username, "refresh": str(refresh), "access": str(refresh.access_token), },
                    headers={'Access-Allow-Origin': '*'}, status=200)

        except ValueError as e:
            print(e)
            return JsonResponse({"errors": {"detail": "Invalid token"}}, status=400)
