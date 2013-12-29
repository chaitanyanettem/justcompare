def check_digit(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if i % 2: w = 3
        else: w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if r == 10: return '0'
    else: return str(r)

def convert(isbn):
    try:
        assert len(isbn) == 10
    except AssertionError:
        return isbn
    prefix = '978' + isbn[:-1]
    check = check_digit(prefix)
    return prefix + check