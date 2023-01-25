from django.core.paginator import Paginator


def paginator(request, posts_list: dict, posts_in_page: int) -> dict:
    """Функция паджинатора."""
    paginator = Paginator(posts_list, posts_in_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
