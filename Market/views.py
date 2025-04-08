from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def main_page(request: HttpRequest) -> HttpResponse:
    """Функция, отвечающая за отображение главной страницы"""

    return render(request=request, template_name='market/main_page.html')
