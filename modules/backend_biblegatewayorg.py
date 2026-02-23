import requests
from bs4 import BeautifulSoup
import html2text
import re
from pathlib import Path
from .helper_booknames import *
from .helper_general import *

def getText(version, verbose=False, cache=True):

    # ensure cache directory exists
    cache_dir = Path(f"./cache/biblegateway.org/{version}/")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # the full bible should result in a dictionary that measures somewhere ~5MB, easy to store in memory
    return_data = []

    # the current book and its short name
    for book in bible_books_chapters:

        book_short = convert_bookname_to_osis(book)

        print(f" > Retrieving book: {book} ({book_short})")

        for chapter in range(1,bible_books_chapters[book]+1):

            if verbose:
                print(f"   > Chapter: {chapter}")

            htmltxt = ""

            # check if cached file exists
            cache_file = cache_dir / f"{book_short}.{chapter}.html"
            if cache and cache_file.exists():

                if verbose:
                    print("     > Cached file found, using that")

                with open(cache_file, "r") as f:
                    htmltxt = f.read()

            else:

                wait_shortly()

                url = f"https://www.biblegateway.com/passage/?search={book}+{chapter}&version={version}"
                if verbose:
                    print(f"     URL: {url}")

                # fetch the page content, using a User-Agent header to avoid being blocked by basic bot filters
                headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }

                # try to get webpage
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                except Exception as e:
                    print(f"Error fetching the URL: {e}")
                    return

                # the response html
                htmltxt = response.text

                # if caching is enabled, write file to cache
                if cache:
                    with open(cache_file, "w") as f:
                        f.write(htmltxt)

            # mark different sections in a way that is left unchanged in place
            htmltxt = htmltxt.replace("</p> <p>", "</p> -|-|-<p>")
            htmltxt = htmltxt.replace('<sup class="versenum">', '</p> -|-|- <p><sup class="versenum">')

            # parse HTML with BeautifulSoup
            soup = BeautifulSoup(htmltxt, 'html.parser')

            # replace the chapter number by the first verse number (if there is any chapter number)
            chapnum = soup.find('span', class_='chapternum')
            if chapnum:
                chapnum.name = "sup"
                chapnum['class'] = "versenum"
                chapnum.string = f"1 "

            # Target the specific scripture content
            # BibleGateway usually wraps the text in a div with the class 'std-text'
            passage_div = soup.find('div', class_='std-text')

            # bad data received or web content changed
            if not passage_div:
                print("Could not find the scripture content on this page.")
                return

            # mark footnotes and cross-references
            for extra in passage_div.find_all(['sup', 'div'], class_=['footnote', 'crossreference', 'footnotes']):
                if "footnote" in extra['class']:
                    extra.replace_with(f"|||{extra['data-fn']}|||")
                if "crossreference" in extra['class']:
                    extra.replace_with(f"[[[{extra['data-cr']}]]]")
                extra.decompose()

            # convert HTML to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = True  # ignore links inside the text
            h.body_width = 0       # don't wrap lines

            current_markdown_text = h.handle(str(passage_div))

            # re-add section markers
            current_markdown_text = current_markdown_text.replace("-|-|-", "---")

            # replace all double line breaks, we don't need them
            while "\n\n" in current_markdown_text:
                current_markdown_text = current_markdown_text.replace("\n\n", "\n")

            # find all cross reference values
            xrefs_pattern = r"\[\[\[(.*?)\]\]\]"
            xrefs_ids = re.findall(xrefs_pattern, current_markdown_text)
            for xref in xrefs_ids:
                current_markdown_text = current_markdown_text.replace(f"[[[{xref}]]]", f"[[[{book}|{chapter}|{soup.select_one(f'{xref} a').text.split(":")[-1]}|{soup.select_one(f'{xref} .crossref-link')['data-bibleref']}]]]")

            # find all footnote values
            fns_pattern = r"\|\|\|(.*?)\|\|\|"
            fns_ids = re.findall(fns_pattern, current_markdown_text)
            for fn in fns_ids:
                current_markdown_text = current_markdown_text.replace(f"|||{fn}|||", f"|||{soup.select_one(f'{fn} .footnote-text').decode_contents()}|||")

            # we then loop over all lines and put them into a dictionary:
            # book, chapter, content
            current_data = {"book" : book,
                            "chapter" : chapter,
                            "content" : []}

            # we then loop over all lines that do NOT start a new verse, attach them to the end of the previous one with a <br> in between
            parts = current_markdown_text.split("\n")
            working = ""
            workingverse = ""
            for p in parts:
                p = p.strip()
                if p == "":
                    continue
                if working == "":
                    if re.match(r"^[0-9]+\s", p):
                        spacebreak = p.strip().split(" ")
                        workingverse = spacebreak[0]
                        working = " ".join(spacebreak[1:])
                    else:
                        working = p
                    continue
                if re.match(r"^[0-9]+\s", p) or p == "---" or p.startswith("#"):
                    if re.match(r"^[0-9]+\s", p):
                        if workingverse == "":
                            current_data['content'].append([working])
                        else:
                            current_data['content'].append([workingverse, working])
                        spacebreak = p.strip().split(" ")
                        workingverse = spacebreak[0]
                        working = " ".join(spacebreak[1:])
                    else:
                        if workingverse == "":
                            current_data['content'].append([working])
                        else:
                            current_data['content'].append([workingverse, working])
                        working = p
                        workingverse = ""
                    continue
                else:
                    # TODO: handle poetry
                    working = f"{working} {p}"

            if workingverse == "":
                current_data['content'].append([working])
            else:
                current_data['content'].append([workingverse, working])

            return_data.append(current_data)

    return return_data
