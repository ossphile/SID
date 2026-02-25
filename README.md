# SID - SWORD bible module generator

SID is a helper program that is capable of getting the bible from various different backends, generating a SWORD bible module at the end. Such a module can then be used with any software (desktop, mobile) that supports such modules.

It is sufficient to execute the main python file `sword.py` with Python, it will guide you through everything. The various options is requests can also be specified with various parameter flags, but this is not necessary.

---

### How does it work?

SID relies on different backends that can be selected at runtime. Each backend is responsible for extracting all the required data and return them to SID in a unified fashion. SID, in turn, takes the returned data, generates the proper XML file and converts it (using `osis2mod`) to the compiled module.

At the end of its run, you will find a ZIP file in the root folder that can be used to install the module wherever you want it to.

### How do I install a module?

These scripts produce a ZIP file that often can be installed by some piece of software. If not, you can extract the zip file and place the `mods.d` and `modules` subdirectory, for example, into the `~/.sword/` location for it to be picked up by your bible software.

### What about rights?

Depending on where in the world you live you might not have automatic permission to have a digital copy of any physical book you have. You need to confirm that you indeed have the necessary rights. SID does not assume any responsibility in this regard. SID does not provide any bible text data itself, but merely functions as middle man between you and an external server. It is on you, the user, to ensure that all rights are respected.

### Can you also support this bible website?

Sure, any wesite that presents bible texts in some form can be supported. All that is required is a backend that parses the data and returns the results ot SID. Pull requests are always welcome.

---

### How can I add a new backend to SID?

The way SID functions is rather straight forward and should be easy to be implemented by anybody:

Each backend is expected to return a Python `list` where each entry in the list corresponds to one chapter of one book of the bible. Each entry in the list is expected to be a dictionary of this shape:

```
data = {"book" : "name of the book",
        "chapter" : the current chapter",
        "content" : [] }    # a list for all the content
```

The content stored in the dictionary is another `list` that contains the verses and styling data of the given chapter. Possible entries in the list include:
- `# title`: a section title. The number of `#` is arbitrary, they are all treated the same
- `---`: A section divider.
- `["1", "In the beginning"]`: A verse consisting of the verse number (first entry) and the actual verse text (second entry).

SID also supports cross-references and footnotes to be contained in verses:

- Adding a footnote can be done in this way: `This is some|||Genesis|1|sometimes also <i>some random</i>||| text.` Between the triple `|||` on both ends, three pieces of information are expected, each separated by a vertical line `|` which will be converted into a footnote at this position:
    1. The current book.
    2. The current chapter.
    3. The footnote which can include basic HTML tags (like `<i>` or `<b>`).

- Adding a cros references is done in a similar way: `This is also|[|Genesis|1|Genesis 1:5|]| some text.`. Between the triple `|[|` and `|]|`, four pieces of information are expected, each separated by a vertical line `|`: 
    1. The current book.
    2. The current chapter.
    3. The current verse.
    4. The cross references. This can be a comma separated list.
- If a verse contains line breaks, then it is assumed to be poetry and will be formatted accordingly. Four leading spaces for one such line will cause the line to be indented by a level in the final module.

All the code for this extraction needs to be wrapped in a function called `getData` that expects three parameters: `version`, (which bible version was requested), `verbose` (whether the user wants verbose feedback of what is going on), and `cache` (whether the backend is expected to dome some caching of downloaded files). 

In addition to the `getData` function for extracting the bible text in the format described above, one additional function that is necessary is the function called `getSupportedVersions`. This function returns a dictionary as described by this sample data:
```
data = {'NIV'     : ['New International Version', 'en'],
        'SCH2000' : ['Schlachter 2000'          , 'de']}
```
The keys are the bible version identifiers that the user will use to select the desired version, and the values are lists containing exactly two elements: The first entry is the proper name of that bible version, and the second entry is the two-character identifier of the language.

Both of these functions, and any other code needed by a backend, need to be stored in a file with filename `backend_[identifier].py`, where identifier is any string of letters that will allow the user to select this backend (for example: `backend_biblegateway.py`). In addition that idenfitier (*without* the `backend_` prefix *nor* the `.py` suffix), needs to be added to the `backends` list near the top of the `sword.py` file.

There are a few helper functions that can be helpful that are provided in the two files `helper_general.py` and `helper_booknames.py`. They are all pretty much self-explanatory and are of course not obligatory to be used.

And now you are ready to test your new backend with SID.
