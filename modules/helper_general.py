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

# Print iterations progress
# Code taken from: https://stackoverflow.com/a/34325723
def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
