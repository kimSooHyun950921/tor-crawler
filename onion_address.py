import re

#RULE = '(?:http://|https://)(?:[a-zA-Z2-7]{16}|[a-zA-Z2-7]{56})'
RULE = '(?:http://|https://)([a-zA-Z2-7]{16}|[a-zA-Z2-7]{56})'
EXT = ['.onion', '.tor2web', '.torstorm']


def extract_address(addr):
    global RULE
    global EXT
    result = ''
    for ext in EXT:
        rule = f'{RULE}{ext}'
        try:
            r = re.findall(rule, addr)
        except TypeError:
            break
        if len(r) != 0:
            result = r[0].replace(ext, '.onion')
            break
    return result
