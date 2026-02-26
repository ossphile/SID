##################################################################
##################################################################
# MAP common book names to their respective OSIS names
#
# Exceptions:
# The name Song of Salomon or Song of Songs is stored WITHOUT spaces to facilitate conversion

bible_books_chapters = {
    # old Testament
    "Genesis": 50,
    "Exodus": 40,
    "Leviticus": 27,
    "Numbers": 36,
    "Deuteronomy": 34,
    "Joshua": 24,
    "Judges": 21,
    "Ruth": 4,
    "1 Samuel": 31,
    "2 Samuel": 24,
    "1 Kings": 22,
    "2 Kings": 25,
    "1 Chronicles": 29,
    "2 Chronicles": 36,
    "Ezra": 10,
    "Nehemiah": 13,
    "Esther": 10,
    "Job": 42,
    "Psalms": 150,
    "Proverbs": 31,
    "Ecclesiastes": 12,
    "Song of Songs": 8,
    "Isaiah": 66,
    "Jeremiah": 52,
    "Lamentations": 5,
    "Ezekiel": 48,
    "Daniel": 12,
    "Hosea": 14,
    "Joel": 3,
    "Amos": 9,
    "Obadiah": 1,
    "Jonah": 4,
    "Micah": 7,
    "Nahum": 3,
    "Habakkuk": 3,
    "Zephaniah": 3,
    "Haggai": 2,
    "Zechariah": 14,
    "Malachi": 4,

    # new Testament
    "Matthew": 28,
    "Mark": 16,
    "Luke": 24,
    "John": 21,
    "Acts": 28,
    "Romans": 16,
    "1 Corinthians": 16,
    "2 Corinthians": 13,
    "Galatians": 6,
    "Ephesians": 6,
    "Philippians": 4,
    "Colossians": 4,
    "1 Thessalonians": 5,
    "2 Thessalonians": 3,
    "1 Timothy": 6,
    "2 Timothy": 4,
    "Titus": 3,
    "Philemon": 1,
    "Hebrews": 13,
    "James": 5,
    "1 Peter": 5,
    "2 Peter": 3,
    "1 John": 5,
    "2 John": 1,
    "3 John": 1,
    "Jude": 1,
    "Revelation": 22
}

book_name2osis_map = {

    # old testament
    "genesis": "Gen",
    "exodus": "Exod",
    "leviticus": "Lev",
    "numbers": "Num",
    "deuteronomy": "Deut",
    "joshua": "Josh",
    "judges": "Judg",
    "ruth": "Ruth",
    "1 samuel": "1Sam",
    "2 samuel": "2Sam",
    "1 kings": "1Kgs",
    "2 kings": "2Kgs",
    "1 chronicles": "1Chr",
    "2 chronicles": "2Chr",
    "ezra": "Ezra",
    "nehemiah": "Neh",
    "esther": "Esth",
    "job": "Job",
    "psalms": "Ps",
    "psalm": "Ps",
    "proverbs": "Prov",
    "ecclesiastes": "Eccl",
    "song of solomon": "Song",
    "song of songs": "Song",
    "isaiah": "Isa",
    "jeremiah": "Jer",
    "lamentations": "Lam",
    "ezekiel": "Ezek",
    "daniel": "Dan",
    "hosea": "Hos",
    "joel": "Joel",
    "amos": "Amos",
    "obadiah": "Obad",
    "jonah": "Jonah",
    "micah": "Mic",
    "nahum": "Nah",
    "habakkuk": "Hab",
    "zephaniah": "Zeph",
    "haggai": "Hag",
    "zechariah": "Zech",
    "malachi": "Mal",

    # new testament
    "matthew": "Matt",
    "mark": "Mark",
    "luke": "Luke",
    "john": "John",
    "acts": "Acts",
    "romans": "Rom",
    "1 corinthians": "1Cor",
    "2 corinthians": "2Cor",
    "galatians": "Gal",
    "ephesians": "Eph",
    "philippians": "Phil",
    "colossians": "Col",
    "1 thessalonians": "1Thess",
    "2 thessalonians": "2Thess",
    "1 timothy": "1Tim",
    "2 timothy": "2Tim",
    "titus": "Titus",
    "philemon": "Phlm",
    "hebrews": "Heb",
    "james": "Jas",
    "1 peter": "1Pet",
    "2 peter": "2Pet",
    "1 john": "1John",
    "2 john": "2John",
    "3 john": "3John",
    "jude": "Jude",
    "revelation": "Rev"
}

# Unified Standard Format Markers
book_name2usfm_map = {
    "genesis" : "GEN",
    "exodus" : "EXO",
    "leviticus" : "LEV",
    "numbers" : "NUM",
    "deuteronomy" : "DEU",
    "joshua" : "JOS",
    "judges" : "JDG",
    "ruth" : "RUT",
    "1 samuel" : "1SA",
    "2 samuel" : "2SA",
    "1 kings" : "1KI",
    "2 kings" : "2KI",
    "1 chronicles" : "1CH",
    "2 chronicles" : "2CH",
    "ezra" : "EZR",
    "nehemiah" : "NEH",
    "esther (Hebrew)" : "EST",
    "job" : "JOB",
    "psalms" : "PSA",
    "proverbs" : "PRO",
    "ecclesiastes" : "ECC",
    "song of songs" : "SNG",
    "isaiah" : "ISA",
    "jeremiah" : "JER",
    "lamentations" : "LAM",
    "ezekiel" : "EZK",
    "daniel" : "DAN",
    "hosea" : "HOS",
    "joel" : "JOL",
    "amos" : "AMO",
    "obadiah" : "OBA",
    "jonah" : "JON",
    "micah" : "MIC",
    "nahum" : "NAM",
    "habakkuk" : "HAB",
    "zephaniah" : "ZEP",
    "haggai" : "HAG",
    "zechariah" : "ZEC",
    "malachi" : "MAL",
    "matthew" : "MAT",
    "mark" : "MRK",
    "luke" : "LUK",
    "john" : "JHN",
    "acts" : "ACT",
    "romans" : "ROM",
    "1 corinthians" : "1CO",
    "2 corinthians" : "2CO",
    "galatians" : "GAL",
    "ephesians" : "EPH",
    "philippians" : "PHP",
    "colossians" : "COL",
    "1 thessalonians" : "1TH",
    "2 thessalonians" : "2TH",
    "1 timothy" : "1TI",
    "2 timothy" : "2TI",
    "titus" : "TIT",
    "philemon" : "PHM",
    "hebrews" : "HEB",
    "james" : "JAS",
    "1 peter" : "1PE",
    "2 peter" : "2PE",
    "1 john" : "1JN",
    "2 john" : "2JN",
    "3 john" : "3JN",
    "jude" : "JUD",
    "revelation" : "REV"
}

def convert_bookname_to_osis(in_book):

    key = in_book.strip().lower()

    allparts = key.split("-")

    ret = ""

    for ap in allparts:

        if ret != "":
            ret += "-"

        parts = ap.split(" ")
        if ":" in parts[-1] or parts[-1].isdigit():
            book = " ".join(parts[:-1])
            loc = parts[-1]
        else:
            book = " ".join(parts)
            loc = ""

        if book not in book_name2osis_map:
            raise ValueError(f"Unknown book name: {in_book}")
        ret += f"{book_name2osis_map[book]} {loc}".strip()

    return ret


def convert_bookname_to_usfm(in_book):

    key = in_book.strip().lower()

    allparts = key.split("-")

    ret = ""

    for ap in allparts:

        if ret != "":
            ret += "-"

        parts = ap.split(" ")
        if ":" in parts[-1] or parts[-1].isdigit():
            book = " ".join(parts[:-1])
            loc = parts[-1]
        else:
            book = " ".join(parts)
            loc = ""

        if book not in book_name2usfm_map:
            raise ValueError(f"Unknown book name: {in_book}")
        ret += f"{book_name2usfm_map[book]} {loc}".strip()

    return ret
