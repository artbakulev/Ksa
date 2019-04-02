from django.core.paginator import Paginator


def make_paginator(objects, page, max_objects_per_page):
    paginator = Paginator(objects, max_objects_per_page)
    page = paginator.page(page)
    first_page = page.number
    second_page = False
    last_page = False
    if page.has_next():
        second_page = page.number + 1
    if first_page != paginator.num_pages and second_page != paginator.num_pages:
        last_page = paginator.num_pages

    paginator = {'page': page, 'first_page': first_page, 'second_page': second_page, 'last_page': last_page}
    return paginator
