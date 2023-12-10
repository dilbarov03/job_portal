import string


def is_password_valid(password):
    allowed_characters = string.ascii_letters + string.digits + string.punctuation
    if len(password) < 5 or any(ch not in allowed_characters for ch in password):
        return False, "Parol minimum 5ta harf/raqamdan iborat bo'lishi kerak. Faqat lotin harflari va raqamlardan foydalaning!"
    return True, ""
