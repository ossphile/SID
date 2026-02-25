# SID - SWORD bIble moDule generator

SID is a helper program that is capable of getting the bible from various different backends, generating a SWORD bible module at the end. Such a module can then be used with any software (desktop, mobile) that supports such modules.

It is sufficient to execute the main python file `sword.py` with Python, it will guide you through everything. The various options is requests can also be specified with various parameter flags, but this is not necessary.

---

**NOTE**

These Python scripts are still in a very early stage. Feel free to test them already, the basic usage already works just fine, but they likely change a bit in the days and weeks to come.

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

- Adding a footnote can be done in this way: `This is some|||sometimes also <i>some random</i>||| text.` The data between the triple `|` is converted into a footnote at this position
- Adding a cros references is done in a similar way: `This is also|[|Gen|1|Genesis 1:5|]| some text.`. Between the triple `|[|` and `|]|`, three pieces of information are expected, each separated by a vertical line `|`: 
    1. The current book.
    2. The current chapter.
    3. The current verse.
    4. The cross references. This can be a comma separated list.
- If a verse contains line breaks, then it is assumed to be poetry and will be formatted accordingly. Four leading spaces for one such line will cause the line to be indented by a level in the final module.


This is all that is needed for a backend to work with SID. The code for the backend needs to be wrapped in a function called `getText` that expected three parameters: `version`, (which bible version was requested), `verbose` (whether the user wants verbose feedback of what is going on), and `cache` (whether the backend is expected to dome some caching of downloaded files). This function, then, needs to be stored in a file with filename `backend_[identifier].py`, where identifier is any string of letters that will allow the user to select this backend.

The backend needs to be added to SID now by adding its identifier to the `backends` list at the start of the `__main__` section of `sword.py`. Note that the entry in the list *can* include dots, but these will be removed before importing the backend module.

And now you are ready to test your new backend with SID.
