import re


def is_phone_valid(phone_number):
    """Check phone number is valid or not. @return: Boolean """
    if phone_number:
        mobile_regex = re.compile('^(?:\+?88)?01[15-9]\d{8}$')
        if mobile_regex.match(phone_number):
            return True
        else:
            return False
    else:
        return False
