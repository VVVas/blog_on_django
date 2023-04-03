from django.conf import settings
from django.core.paginator import Paginator


def paginate(posts, page_number):
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)
