import hashlib


def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


def format_date(date):
    return date.strftime("%a %d %b %Y %X")
