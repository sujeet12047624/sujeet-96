"""Authentication views: Sign-up, Login, Logout, Token Refresh, Profile."""

import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, SignUpSerializer, UserProfileSerializer
from .throttles import AuthRateThrottle

logger = logging.getLogger(__name__)
User = get_user_model()


def _set_auth_cookies(response, access_token, refresh_token):
    """Attach JWT tokens as HttpOnly cookies."""
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt_settings["AUTH_COOKIE"],
        value=str(access_token),
        httponly=jwt_settings["AUTH_COOKIE_HTTP_ONLY"],
        secure=jwt_settings["AUTH_COOKIE_SECURE"],
        samesite=jwt_settings["AUTH_COOKIE_SAMESITE"],
        path=jwt_settings["AUTH_COOKIE_PATH"],
        max_age=int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )
    response.set_cookie(
        key=jwt_settings["AUTH_COOKIE_REFRESH"],
        value=str(refresh_token),
        httponly=jwt_settings["AUTH_COOKIE_HTTP_ONLY"],
        secure=jwt_settings["AUTH_COOKIE_SECURE"],
        samesite=jwt_settings["AUTH_COOKIE_SAMESITE"],
        path=jwt_settings["AUTH_COOKIE_PATH"],
        max_age=int(jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    )
    return response


class SignUpView(generics.CreateAPIView):
    """Register a new UPSC aspirant account."""

    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        return _set_auth_cookies(response, refresh.access_token, refresh)


class LoginView(APIView):
    """Authenticate user and issue JWT tokens in HttpOnly cookies."""

    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        response = Response(
            {
                "message": "Login successful.",
                "user": UserProfileSerializer(user).data,
            }
        )
        return _set_auth_cookies(response, refresh.access_token, refresh)


class LogoutView(APIView):
    """Blacklist refresh token and clear auth cookies."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            logger.warning("Failed to blacklist refresh token during logout.")

        response = Response({"message": "Logged out successfully."})
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        return response


class TokenRefreshView(APIView):
    """Rotate refresh token from HttpOnly cookie."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        if not refresh_token:
            return Response(
                {"error": "No refresh token provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            old_refresh = RefreshToken(refresh_token)
            old_refresh.blacklist()

            user = User.objects.get(id=old_refresh["user_id"])
            new_refresh = RefreshToken.for_user(user)
            response = Response({"message": "Token refreshed."})
            return _set_auth_cookies(response, new_refresh.access_token, new_refresh)
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
