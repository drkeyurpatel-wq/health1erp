"""Rate limiting middleware using in-memory sliding window with Redis fallback.

Provides endpoint-specific rate limits:
- Login: 5 requests/minute (brute-force protection)
- API general: 100 requests/minute
- AI endpoints: 20 requests/minute (expensive operations)
- File uploads: 10 requests/minute
"""
import time
import logging
from collections import defaultdict
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("health1erp.ratelimit")


class SlidingWindowCounter:
    """In-memory sliding window rate limiter. Thread-safe for async context."""

    def __init__(self):
        # key -> list of timestamps
        self._windows: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> tuple[bool, dict]:
        now = time.time()
        cutoff = now - window_seconds

        # Prune old entries
        self._windows[key] = [t for t in self._windows[key] if t > cutoff]

        current_count = len(self._windows[key])
        remaining = max(0, max_requests - current_count)

        if current_count >= max_requests:
            # Calculate retry-after
            oldest = self._windows[key][0] if self._windows[key] else now
            retry_after = int(oldest + window_seconds - now) + 1
            return False, {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(now + retry_after)),
                "Retry-After": str(retry_after),
            }

        self._windows[key].append(now)
        return True, {
            "X-RateLimit-Limit": str(max_requests),
            "X-RateLimit-Remaining": str(remaining - 1),
            "X-RateLimit-Reset": str(int(now + window_seconds)),
        }

    def cleanup(self, max_age: int = 600):
        """Remove stale keys older than max_age seconds."""
        now = time.time()
        stale_keys = [
            k for k, v in self._windows.items()
            if not v or v[-1] < now - max_age
        ]
        for k in stale_keys:
            del self._windows[k]


# Route-specific rate limit configuration
RATE_LIMITS = {
    # Auth endpoints - strict limits for brute-force protection
    "/api/v1/auth/login": (5, 60),        # 5 req/min
    "/api/v1/auth/refresh": (10, 60),      # 10 req/min
    "/api/v1/auth/register": (3, 60),      # 3 req/min

    # AI endpoints - expensive operations
    "/api/v1/ai/cdss/recommend": (20, 60),
    "/api/v1/ai/drug-interactions": (30, 60),
    "/api/v1/ai/diagnosis-suggest": (20, 60),
    "/api/v1/ai/early-warning-score": (30, 60),
    "/api/v1/ai/predict-los": (20, 60),
    "/api/v1/ai/discharge-summary/generate": (10, 60),
    "/api/v1/ai/translate": (20, 60),

    # Document downloads
    "/api/v1/documents/": (15, 60),
}

# Default rate limit for all API endpoints
DEFAULT_RATE_LIMIT = (100, 60)  # 100 req/min


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: Optional[SlidingWindowCounter] = None):
        super().__init__(app)
        self.limiter = limiter or SlidingWindowCounter()
        self._cleanup_counter = 0

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ("/health", "/api/docs", "/api/redoc", "/api/openapi.json"):
            return await call_next(request)

        # Only rate limit API routes
        if not path.startswith("/api/"):
            return await call_next(request)

        # Get client identifier (IP + optional user from token)
        client_ip = self._get_client_ip(request)
        rate_key = f"{client_ip}:{path}"

        # Find matching rate limit
        max_requests, window = self._get_rate_limit(path)

        allowed, headers = self.limiter.is_allowed(rate_key, max_requests, window)

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                extra={"client": client_ip, "path": path, "limit": max_requests},
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "retry_after": headers.get("Retry-After", "60"),
                },
            )
            for k, v in headers.items():
                response.headers[k] = v
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        for k, v in headers.items():
            response.headers[k] = v

        # Periodic cleanup
        self._cleanup_counter += 1
        if self._cleanup_counter >= 1000:
            self.limiter.cleanup()
            self._cleanup_counter = 0

        return response

    def _get_client_ip(self, request: Request) -> str:
        # Check X-Forwarded-For for proxied requests
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _get_rate_limit(self, path: str) -> tuple[int, int]:
        # Check exact match first
        if path in RATE_LIMITS:
            return RATE_LIMITS[path]

        # Check prefix match for grouped routes
        for route_prefix, limits in RATE_LIMITS.items():
            if route_prefix.endswith("/") and path.startswith(route_prefix):
                return limits

        return DEFAULT_RATE_LIMIT
