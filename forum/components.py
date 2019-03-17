from configuration import TOTAL_QUESTIONS_ON_PAGE


def generate_paginator(questions, page):
    first_page = page
    second_page = 0
    total_questions = len(questions)
    last_page = total_questions // TOTAL_QUESTIONS_ON_PAGE
    if total_questions % TOTAL_QUESTIONS_ON_PAGE > 0:
        last_page += 1

    if last_page > 1 and first_page < last_page:
        second_page = first_page + 1
    questions = questions[(page-1)*TOTAL_QUESTIONS_ON_PAGE:(page-1) * TOTAL_QUESTIONS_ON_PAGE + TOTAL_QUESTIONS_ON_PAGE]
    return questions, first_page, second_page, last_page
