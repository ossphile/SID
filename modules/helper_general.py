def remove_html_tags(data):
    import re
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def wait_shortly():
    from random import randint
    from time import sleep
    sleep(randint(1,3))
