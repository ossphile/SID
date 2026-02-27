from urllib.parse import urlencode
from bs4 import BeautifulSoup
from pathlib import Path
from .helper_booknames import *
from .helper_general import *

def getDescription():
    return "Supports a selection of bibles from biblegateway.org. The final bible includes section titles, cross-references, and footnotes whenever provided by biblegateway.org."

def getSupportedVersions():

    return {"AMP":      ["Amplified Bible",                              "en"],
            "ASV":      ["American Standard Version",                    "en"],
            "AKJV":     ["Authorized (King James) Version",              "en"],
            "BRG":      ["BRG Bible",                                    "en"],
            "CSB":      ["Christian Standard Bible",                     "en"],
            "EHV":      ["Evangelical Heritage Version",                 "en"],
            "ESV":      ["English Standard Version",                     "en"],
            "ESVUK":    ["English Standard Version Anglicised",          "en"],
            "GNV":      ["1599 Geneva Bible",                            "en"],
            "GW":       ["GOD’S WORD Translation",                       "en"],
            "ISV":      ["International Standard Version",               "en"],
            "JUB":      ["Jubilee Bible 2000",                           "en"],
            "KJV":      ["King James Version",                           "en"],
            "KJ21":     ["21st Century King James Version",              "en"],
            "LEB":      ["Lexham English Bible",                         "en"],
            "LSB":      ["Legacy Standard Bible",                        "en"],
            "MEV":      ["Modern English Version",                       "en"],
            "NASB":     ["New American Standard Bible",                  "en"],
            "NASB1995": ["New American Standard Bible 1995",             "en"],
            "NET":      ["New English Translation",                      "en"],
            "NIV":      ["New International Version",                    "en"],
            "NIVUK":    ["New International Version - UK",               "en"],
            "NKJV":     ["New King James Version",                       "en"],
            "NLT":      ["New Living Translation",                       "en"],
            "NLV":      ["New Life Version",                             "en"],
            "NMB":      ["New Matthew Bible",                            "en"],
            "NOG":      ["Names of God Bible",                           "en"],
            "NRSV":     ["New Revised Standard Version",                 "en"],
            "NRSVUE":   ["New Revised Standard Version Updated Edition", "en"],
            "RSV":      ["Revised Standard Version",                     "en"],
            "WEB":      ["World English Bible",                          "en"],
            "YLT":      ["Young's Literal Translation",                  "en"],
            "RVA":      ["Reina-Valera Antigua",                         "es"],
            "SCH2000":  ["Schlachter 2000",                              "de"],
            "HOF":      ["Hoffnung für Alle",                            "de"],
            "SG21":     ["Segond 21",                                    "fr"]}

def getData(version, verbose):

    return_data = []

    printProgressBar(0, 1189, prefix='Book:', suffix='downloaded', length = 50)
    progressCounter = 0

    for book in bible_books_chapters:

        if verbose:
            print(f"# BOOK: {book}")

        for chapter in range(1, bible_books_chapters[book]+1):

            progressCounter += 1

            if verbose:
                print(f"  chapter: {chapter}")
            else:
                printProgressBar(progressCounter, 1189, prefix='  Bible:', suffix='downloaded', length = 50)

            return_data.append({"book" : book,
                                "chapter" : chapter,
                                "content" : retrieveData(f"{book} {chapter}", version, verbose)})

    return return_data

###################################################################################################

# This function is adapted from the meaningless package, version 1.3.0:
# https://github.com/daniel-tran/meaningless
def retrieveData(reference, version, verbose):
    """
    Retrieves a specific passage directly from the Bible Gateway site.
    """

    # Some translations are very tricky to extract passages from, and currently, so specific extraction logic
    # for these translations should not be introduced until they need to be supported.
    if version not in getSupportedVersions():
        print(f"ERROR: version not supported: {version}")
        return []


    cache_dir = Path(f"./cache/biblegateway/{version}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{reference}.html"

    htmltxt = ""

    if cache_file.exists():
        with open(cache_file, "r") as f:
            htmltxt = f.read()
        soup = BeautifulSoup(htmltxt, 'html.parser')

    else:

        wait_shortly()

        # Use the printer-friendly view since there are fewer page elements to load and process
        source_site_params = urlencode({'version': version, 'search': reference, 'interface': 'print'})
        source_site = f'https://www.biblegateway.com/passage/?{source_site_params}'
        htmltxt = get_page(source_site).decode()
        with open(cache_file, "w") as f:
            f.write(htmltxt)
        soup = BeautifulSoup(htmltxt, 'html.parser')

    # Don't collect contents from an invalid verse, since they do not exist.
    # A fail-fast approach can be taken by checking for certain indicators of invalidity.
    if not soup.find('div', {'class': 'passage-content'}):
        if "No valid results were found for your search." not in htmltxt:
            print("ERROR: did not find passage content")
        return []

    # To get a list, the passage separator is given an actual practical use as an indicator of where to split
    # the string to create list elements.
    passage_separator = '-_-'

    # We preserve heading of the various types. They will be put into their own list entry at the end
    [h2.replaceWith(f"\n## {h2.text}\n") for h2 in soup.find_all("h2")]
    [h3.replaceWith(f"\n### {h3.text}\n") for h3 in soup.find_all("h3")]
    [h4.replaceWith(f"\n#### {h4.text}\n") for h4 in soup.find_all("h4")]

    # replace all cross-references with the respective references. This can be a comma separated list of
    # multiple references. The list starts with |[| and ends with |]|
    [sup.replaceWith(f"|[|{reference.split(" ")[0]}|{reference.split(":")[-1]}|{soup.find("li", id=sup['data-cr'][1:]).a.text}|{soup.find("li", id=sup['data-cr'][1:]).find("a", {'class', "crossref-link"})['data-bibleref']}|]|") for sup in soup.find_all("sup", {'class', "crossreference"})]

    # replace all footnotes
    [sup.replaceWith(f"|||{reference.split(" ")[0]}|{reference.split(":")[-1]}|{soup.find("li", id=sup['data-fn'][1:]).span.text}|||") for sup in soup.find_all("sup", {'class', 'footnote'})]

    # Compile the list of tags to remove from the parsed web page, corresponding to the following elements:
    # h1
    #    - Ignore passage display
    # a with 'full-chap-link' class
    #    - Ignore the "Read Full Chapter" text, which is carefully embedded within the passage
    # sup with 'crossreference' class
    #    - Ignore cross references
    # sup with 'footnote' class
    #    - Ignore in-line footnotes
    # div with one of the 'footnotes', 'dropdowns', 'crossrefs', 'passage-other-trans' classes
    #    - Ignore the footer area, which is composed of several main tags
    # p with 'translation-note' class
    #    - Ignore explicit translation notes in translations such as ESV
    # crossref
    #    - Ignore in-line references in translations such as WEB
    removable_tags = soup.find_all(re.compile('^h1$')) \
        + soup.find_all('a', {'class': re.compile('^full-chap-link$|^bibleref$')}) \
        + soup.find_all('sup', {'class': re.compile('^crossreference$|^footnote$')}) \
        + soup.find_all('div', {
                        'class': re.compile('^footnotes$|^dropdowns$|^crossrefs$|^passage-other-trans$')}) \
        + soup.find_all('p', {'class': re.compile('^translation-note$')}) \
        + soup.find_all('crossref')
    # Normally, paragraphs with the 'first-line-none' class would contain valid passage contents.
    # In the GNV version, this class name is specifically used for the blurb of notable chapter details.
    if version == 'GNV':
        removable_tags += soup.find_all('p', {'class': re.compile('^first-line-none$')})
    [tag.decompose() for tag in removable_tags]

    # Compile a list of ways Psalm interludes can be found. These are to be preserved, as it would be the
    # translation team's decision to omit these from the passage, as opposed to a code-level design decision.
    # span with 'selah' class
    #    - Explicit Psalm interludes in the translations such as NLT and CEB
    # i with 'selah' class
    #    - Explicit Psalm interludes in the translations such as NKJV
    # selah
    #    - Explicit Psalm interludes in the translations such as HCSB
    interludes = soup.find_all('span', {'class': 'selah'}) \
        + soup.find_all('i', {'class': 'selah'}) \
        + soup.find_all('selah')
    # Psalm interludes may or may not have a leading space, depending on the version.
    # In any case, always add one in so that the interlude doesn't meld into the passage contents.
    # To account for double spaces, this relies on a regex replacement later on to convert down to a single space.
    [interlude.replace_with(f' {interlude.text}') for interlude in interludes]
    # <br> tags will naturally be ignored when getting text
    [br.replace_with('\n') for br in soup.find_all('br')]
    # The versenum tag appears in only a few translations such as NIVUK, and is difficult to handle because
    # its child tags are usually decomposed before this point, but space padding seems to take its place.
    if version == 'NIVUK':
        [versenum.replace_with(f'{passage_separator}') for versenum in soup.find_all('versenum')]
    # Convert chapter numbers into new lines
    [chapter_num.replace_with('\n') for chapter_num in soup.find_all('span', {'class': 'chapternum'})]
    # Add in the passage separator while access to the verse numbers is still available
    [sup.replace_with(f'{passage_separator}') for sup in soup.find_all('sup', {'class': 'versenum'})]
    # Some verses such as Nehemiah 7:30 - 42 store text in a <table> instead of <p>, which means
    # spacing is not preserved when collecting the text. Therefore, a space is manually injected
    # onto the end of the left cell's text to stop it from joining the right cell's text.
    # Note: Python "double colon" syntax for lists is used to retrieve items at every N interval including 0.
    # TODO: If a verse with >2 columns is found, this WILL need to be updated to be more dynamic
    [td.replace_with(f'{td.text} ') for td in soup.find_all('td')[::2]]
    # Preserve paragraph spacing by manually pre-pending a new line
    # THIS MUST BE THE LAST PROCESSING STEP because doing this earlier interferes with other replacements
    [p.replace_with(f'\n{p.text}') for p in soup.find_all('p')]

    # Combine the text contents of all passage sections on the page.
    # Convert non-breaking spaces to normal spaces when retrieving the raw passage contents.
    # Also strip excess whitespaces to prevent a whitespace build-up when combining multiple passages.
    #
    # Double square brackets are removed here, as they are mostly just indicators that the passages is only kept
    # due to convention with earlier translations. This replacement is done here, as it can sometimes have a
    # trailing space which can cause double spacing, which needs to be normalised.
    raw_passage_text = '\n'.join([tag.text.replace('\xa0', ' ').strip() for tag in
                                    soup.find_all('div', {'class': 'passage-content'})]) \
        .replace('[[', '').replace(']]', '')
    # To account for spaces between tags that end up blending into the passage contents, this regex replacement is
    # specifically used to remove that additional spacing, since it is part of the actual page layout.
    all_text = re.sub('([^ ]) {2,3}([^ ])', r'\1 \2', raw_passage_text)

    # CSB has some passages with the square bracket preceding the superscript number, but not in the same element.
    # This switches them to avoid the passage separator from over-cutting the passage text when splitting it
    # when output_as_list is enabled.
    all_text = re.sub(fr'(\[)({passage_separator}[⁰¹²³⁴⁵⁶⁷⁸⁹]+ +)', r'\2\1', all_text)

    # AMP has newlines directly follow the passage number & trailing space, particularly in Psalms.
    # Bible Gateway support haven't specified a timeline for when this will be fixed, so it's handled here manually.
    if version == 'AMP':
        all_text = re.sub('([⁰¹²³⁴⁵⁶⁷⁸⁹]+ +)\n', r'\1', all_text)

    # Perform ASCII punctuation conversion after hiding superscript numbers to process a slightly shorter string
    all_text = unicode_to_ascii_punctuation(all_text)

    # Some versions include asterisks on certain words in the New Testament. This usually indicates an in-line
    # marker that the word has been translated from present-tense Greek to past-tense English for better flow
    # in modern usage, though not all versions provide consistent footnotes on what the asterisk implies.
    # As it is not actually part of the passage text itself, this is expected to be ignored.
    # Also note that this is a naive replacement - fortunately, asterisks do not seem to be used as a proper
    # text character anywhere in the currently supported Bible version.
    all_text = all_text.replace('*', '')
    # Translations such as GW add these text markers around certain words, which can be removed
    #
    # Translations such as JUB append a pilcrow character at the start of certain passages, which can be removed.
    # These usually have a trailing space, which also needs to be removed to prevent double spacing.
    # This logic would need to be revisited if there are cases of pilcrows without a trailing space.
    all_text = all_text.replace('⌞', '').replace('⌟', '').replace('¶ ', '')


    # At this point, the expectation is that the return value is a list of passages.
    # Since the passage separator is placed before the passage number, it can cause an empty first item upon
    # splitting if the first passage has a passage number.
    # Remove the first passage separator in such scenarios to prevent this from happening.
    # Also perform a one-off strip to ensure the first passage separator is correctly identified.
    if all_text.strip().startswith(passage_separator):
        all_text = all_text.replace(passage_separator, '', 1)
    passage_list = re.split(passage_separator, all_text.strip())

    # The final list for data to be returned
    ret_data = []

    # We are *almost* done at this point. All we need to ensure now is that all titles are their own
    # entry instead of being smushed onto the next or previous verse.
    # At this time we also check if any verse ends with a newline. This indicates that a new section
    # is to be started after that verse.
    # At this point we also add verse numbers.
    num_verse = 1
    for p in passage_list:

        # The current verse
        verse = p

        title_start = []
        title_end = ""
        add_section = False

        # IF there is a #### at the start of the verse
        while p.startswith("#"):
            # store the title
            parts = p.split("\n")
            title_start.append(parts[0])
            p = "\n".join(parts[1:]).strip()

        verse = p

        # IF the current data ENDS with a title
        if "#" in p:

            if "####" in p:
                hashtags = "####"
                parts = p.split("####")
            elif "###" in p:
                hashtags = "###"
                parts = p.split("###")
            elif "##" in p:
                hashtags = "##"
                parts = p.split("##")
            elif "#" in p:
                hashtags = "#"
                parts = p.split("#")

            # Store the verse data and then the title
            verse = f"{parts[0]}{"\n" if not parts[0].endswith("\n") else ""}"
            title_end = f"{hashtags} {parts[-1].strip()}"

        # If the current verse ends with a newline character
        if verse.endswith("\n"):
            add_section = True

        if len(title_start):
            ret_data += title_start
        if verse.strip() != "":
            ret_data.append([str(num_verse), verse.strip()])
            num_verse += 1
        if add_section:
            ret_data.append("---")
        if title_end != "":
            ret_data.append(title_end)

    # Return the list of
    return ret_data
