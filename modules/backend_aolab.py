from modules.helper_booknames import *
from modules.helper_general import *
import json
from pathlib import Path

def getDescription():
    return "Supports 1000+ free-to-use bibles, including many (but not all) well-known versions. Tends to include fewer footnotes, cross-references, or section titles compare to other backends."

def getSupportedVersions():

    cache_dir = Path("cache/aolab/")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "versions.json"

    if cache_file.exists():
        with open(cache_file) as f:
            data = json.loads(f.read())
    else:

        print("Requesting online list of available bible versions... please wait.")

        js = get_page("https://bible.helloao.org/api/available_translations.json")

        with open(cache_file, "w") as f:
            f.write(js.decode())

        data = json.loads(js)


    ret_data = {}
    for entry in data['translations']:
        ret_data[entry['shortName']] = [entry['englishName'], entry['language']]

    return ret_data

def getData(version, verbose):

    return_data = []

    # get version ID
    ao_version = version
    cache_file = "cache/aolab/versions.json"
    with open(cache_file, 'r') as f:
        data = json.loads(f.read())
    for entry in data['translations']:
        if entry['shortName'] == version:
            ao_version = entry['id']

    printProgressBar(0, 1189, prefix='Book:', suffix='downloaded', length = 50)
    progressCounter = 0

    for book in bible_books_chapters:

        if verbose:
            print(f"# BOOK: {book}")

        usfm_book = convert_bookname_to_usfm(book)

        for chapter in range(1, bible_books_chapters[book]+1):

            progressCounter += 1

            if verbose:
                print(f"  chapter: {chapter}")
            else:
                printProgressBar(progressCounter, 1189, prefix='  Bible:', suffix='downloaded', length = 50)

            cache_dir = Path(f"cache/aolab/{version}/")
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / f"{book}.{chapter}.json"

            if cache_file.exists():
                if verbose:
                    print("    -> found cached file.")
                with open(cache_file, 'r') as f:
                    data = json.loads(f.read())
            else:
                url = f"https://bible.helloao.org/api/{ao_version}/{usfm_book}/{chapter}.json"
                if verbose:
                    print(f"Requesting onlne resource from: {url}")
                js = get_page(url)
                with open(cache_file, 'w') as f:
                    f.write(js.decode())
                data = json.loads(js)

            cur_data = []

            for verse in data['chapter']['content']:

                if verse['type'] == 'line_break':

                    cur_data.append('---')

                elif verse['type'] == 'heading':

                    cur_data.append(f"## {verse['content'][0]}")

                elif verse['type'] == 'hebrew_subtitle':

                    cur_data.append(f"#### {verse['content'][0]}")

                elif verse['type'] == 'verse':

                    vnum = verse['number']

                    curversetxt = ""
                    for part in verse['content']:

                        if type(part) == str:
                            if curversetxt != "":
                                curversetxt += " "
                            curversetxt += part
                        elif type(part) == dict:
                            if "noteId" in list(part.keys()):
                                for fn in data['chapter']['footnotes']:
                                    if fn['noteId'] == part['noteId']:
                                        curversetxt += f"|||{book}|{chapter}|{fn['text']}|||"
                            elif "poem" in list(part.keys()):
                                if curversetxt != "":
                                    curversetxt += "\n"
                                curversetxt += f"{'    '*int(part['poem'])}{part['text']}"
                            elif 'lineBreak' in list(part.keys()):
                                curversetxt += "\n"
                            elif "text" in list(part.keys()):
                                curversetxt += part['text']
                            else:
                                print(f"ERROR: Unknown dict of type '{verse['type']}': {part}")
                        else:
                            print(f"ERROR: Unknown part type: {type(part)}")

                    cur_data.append([str(vnum), curversetxt])

                else:
                    print(f"WARNING: Unknown entry type '{verse['type']}'")

            return_data.append({"book" : book,
                                "chapter" : chapter,
                                "content" : cur_data})

    return return_data;
