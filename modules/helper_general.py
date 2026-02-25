from urllib.error import URLError
from urllib.request import urlopen
import re
from time import sleep
from random import randint

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def wait_shortly():
    sleep(randint(1,10)/10)

# A helper function that returns the contents of a web page.
def get_page(url, retry_count=3, retry_delay=2):
    # Cap the values to ensure the function isn't suspended for an eternity, but still attempts at least once
    delay_multiplier = 2
    # The extra addition to the range end is to account for the initial request
    for retry in range(0, retry_count + 1):
        try:
            with urlopen(url) as response:
                return response.read()
        except URLError as exception:
            if retry < retry_count:
                sleep(retry_delay)
                retry_delay *= delay_multiplier
                continue
            raise exception

# A helper function to convert certain punctuation characters from Unicode to ASCII
def unicode_to_ascii_punctuation(text):
    punctuation_map = text.maketrans('“‘—’”', '"\'-\'"')
    return text.translate(punctuation_map)
