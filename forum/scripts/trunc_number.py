# make like this: 100000 -> 100K
# 10000000 -> 1M
def trunc_number(number):
    number = str(number)
    suffix = ''
    if len(number) > 6:
        suffix = 'M'
    elif len(number) > 3:
        suffix = 'K'

    return number[:len(number) % 3] + suffix
