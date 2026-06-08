"""Custom throttle classes for authentication endpoints."""

from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Aggressive rate limiting: 5 attempts/minute per IP on auth endpoints."""

    rate = "5/minute"
    scope = "auth"
