import functools
from time import time
from flask import current_app, request, g, jsonify

_limiter = None

class MemRateLimit(object):
    """Rate limiter that uses a Python dictionary as storage."""
    def __init__(self):
        self.counters = {}

    def is_allowed(self, key, limit, period):
        now = int(time())
        begin_period = now
        end_period = begin_period + period

        self.cleanup(now)
        if key in self.counters:
            self.counters[key]['hits'] += 1
        else:
            self.counters[key] = {'hits': 1, 'reset': end_period}
        allow = True
        remaining = limit - self.counters[key]['hits']
        if remaining < 0:
            remaining = 0
            allow = False
        return allow, remaining, self.counters[key]['reset']

    def cleanup(self, now):
        """Eliminate expired keys."""
        for key, value in list(self.counters.items()):
            if value['reset'] < now:
                del self.counters[key]


def rate_limit(limit, period):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if current_app.config['TESTING']:
                return f(*args, **kwargs)
            else:
                global _limiter
                if _limiter is None:
                    _limiter = MemRateLimit()

                key = '{0}/{1}'.format(f.__name__, request.remote_addr)
                allowed, remaining, reset = _limiter.is_allowed(key, limit, period)

                g.headers = {
                    'X-RateLimit-Remaining': str(remaining),
                    'X-RateLimit-Limit': str(limit),
                    'X-RateLimit-Reset': str(reset)
                }

                if not allowed:
                    response = jsonify({'status': 429, 'error': 'too many requests', 'message': 'You have exceeded your request rate'})
                    response.status_code = 429
                    return response

                return f(*args, **kwargs)
            return wrapped
        return decorator
