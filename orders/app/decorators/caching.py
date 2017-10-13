import functools
import hashlib
from flask import request, make_response, jsonify

def cache_control(*directives):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            rv = f(*args, **kwargs)

            # convert the returned value to a response object
            rv = make_response(rv)

            # insert the Cache-Control header and return response
            rv.headers['Cache-Control'] = ', '.join(directives)
            return rv
        return wrapped
    return decorator

def no_cache(f):
    return cache_control('private', 'no-cache', 'no-store', 'max-age=0')(f)

def etag(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        assert request.method in ['GET', 'HEAD'], '@etag is only supported on GET and HEAD requests'

        rv = f(*args, **kwargs)
        rv = make_response(rv)

        if rv.status_code != 200:
            return rv

        etag = '"' + hashlib.md5(rv.get_data()).hexdigest() + '"'
        rv.headers['ETag'] = etag

        # handle If-Match and If-None-Match request headers if present
        if_match = request.headers.get('If-Match')
        if_none_match = request.headers.get('If-None-Match')

        if if_match:
            etag_list = [tag.strip() for tag in if_match.split(',')]
            if etag not in etag_list and '*' not in etag_list:
                response = jsonify({'status': 412, 'error': 'precondition failed', 'message': 'precondition failed'})
                response.status_code = 412
                return response
        elif if_none_match:
            etag_list = [tag.strip() for tag in if_none_match.split(',')]
            if etag in etag_list or '*' in etag_list:
                response = jsonify({'status': 304, 'error': 'not modified', 'message': 'resource not modified'})
                response.status_code = 304
                return response
        return rv
    return wrapped
