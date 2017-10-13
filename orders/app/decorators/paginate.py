import functools
from flask import url_for, request

def paginate(collection, max_per_page=25):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            query = f(*args, **kwargs)

            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', max_per_page, type=int), max_per_page)
            extended = request.args.get('extended', 0, type=int)

            p = query.paginate(page, per_page)

            pages = {'page': page, 'per_page': per_page, 'total': p.total,
            'pages': p.pages}

            if p.has_prev:
                pages['prev_url'] = url_for(request.endpoint, page=p.prev_num,
                per_page=per_page, extended=extended, _external=True, **kwargs)
            else:
                pages['prev_url'] = None

            if p.has_next:
                pages['next_url'] = url_for(request.endpoint, page=p.next_num,
                per_page=per_page, extended=extended, _external=True, **kwargs)
            else:
                pages['next_url'] = None

            pages['first_url'] = url_for(request.endpoint, page=1,
            per_page=per_page, extended=extended, _external=True, **kwargs)

            pages['last_url'] = url_for(request.endpoint, page=p.pages,
            per_page=per_page, extended=extended, _external=True, **kwargs)

            # return a dictionary as a response
            if extended == 1:
                return { collection: [item.export_data() for item in p.items], 'pages': pages}
            return { collection: [item.get_url() for item in p.items], 'pages': pages}
        return wrapped
    return decorator
