import re
import os
import shutil
import subprocess
import xml.etree.ElementTree as EleTree
from xml.dom import minidom
from pathlib import Path
import importlib
import sys
import argparse
import math

from modules.helper_booknames import *
from modules.helper_general import *

arg_verbose = False

##################################################################
##################################################################
# available backends

backends = ["biblegateway", "helloao"]

##################################################################
##################################################################
# condense reference ranges

def condense_reference_ranges(ref):

    if not "-" in ref:
        return ref

    parts = ref.split("-")

    parts0 = parts[0].split(" ")
    parts1 = parts[1].split(" ")

    book1 = " ".join(parts0[-1])
    book2 = " ".join(parts1[-1])

    if book1 != book2:
        return ref

    chapter1 = parts0[-1].split(":")[0]
    chapter2 = parts1[-1].split(":")[0]
    verse1 = parts0.split(":")[1]
    verse2 = parts1.split(":")[1]

    if chapter1 != chapter2:
        return f"{book1} {chapter1}:{verse1}={chapter2}:{verse2}"

    return f"{book1} {chapter1}:{verse1}-{verse2}"

##################################################################
##################################################################
# replace placeholders for cross references with proper xml

def make_xrefs(text):

    # no cross references -> nothing to do
    if "|[|" not in text:
        return text

    # split along start of cross references
    parts = text.split("|[|")

    # what came before is unchanged
    ret = parts[0]

    prevbook = ""
    prevchapter = ""

    # iterate through parts
    for p in parts[1:]:

        # split along end of cross reference section
        pp = p.split("|]|")

        # extract book name, chapter, and verse number from start of section
        book = pp[0].split("|")[0]
        shortbook = convert_bookname_to_osis(book)
        chapter = pp[0].split("|")[1]
        verse = pp[0].split("|")[2]

        if book != prevbook or prevchapter != chapter:
            # this converts to lower case 'a'
            refletter = 97
            prefix = -1
            prevbook = book
            prevchapter = chapter

        # get a list of all references
        allrefs = list(filter(str.strip, pp[0].split("|")[-1].split(",")))

        # start of reference section
        ret += f'<note type="crossReference" n="{chr(prefix) if prefix > 0 else ""}{chr(refletter)}" osisID="{shortbook}.{chapter}.{verse}!crossReference.{chr(prefix) if prefix > 0 else ""}{chr(refletter)}">'
        # add an entry for all references
        for i,r in enumerate(allrefs):
            ret += f'{";" if i>0 else ""}<reference osisRef="{condense_reference_ranges(convert_bookname_to_osis(r)).replace(" ",".").replace(":",".")}">{condense_reference_ranges(r.strip())}</reference>'
        # end of reference section
        ret += "</note>"

        # go to the next letter, unless we reached the 'z', then start over with 'a'
        if refletter == 122:
            if prefix == -1:
                prefix = 97
            else:
                prefix += 1
        refletter = (97 if refletter == 122 else refletter+1)

        if prefix > 122:
            print("ERROR: More cross references received than expected... this need to be fixed in the code!")
            print("Resetting prefix to 97.")
            prefix = 97

        # the part that came after the end of the cross reference section is kept unchanged
        ret += pp[1]

    return ret


##################################################################
##################################################################
# replace placeholders for footnotes with proper xml

def make_footnotes(text):

    # no footnotes -> nothing to do
    if "|||" not in text:
        return text

    # split along footnotes delimiter (both start and end use same delimiter)
    parts = text.split("|||")

    # what comes before the first footnote is kept unchanged
    ret = parts[0]

    fn_id = 1

    prevbook = "Genesis"
    prevchapter = "1"

    # loop through all parts in steps of two (as the start and end have the same delimiter)
    for i in range(1,len(parts), 2):

        # we keep italic and bold markers
        pp = parts[i]

        book = pp.split("|")[0]
        chapter = pp.split("|")[1]
        footnote = pp.split("|")[2]

        if book != prevbook or chapter != prevchapter:
            prevbook = book
            prevchapter = chapter
            fn_id = 1

        toreplace = {"&lt;i&gt;" : "<i>",
                     "&lt;/i&gt;" : "</i>",
                     "&lt;b&gt;" : "<b>",
                     "&lt;/b&gt;" : "</b>"}
        for t in toreplace:
            footnote = footnote.replace(t, toreplace[t])

        # add footnote
        ret += f'<note type="explanation" n="{fn_id}">{footnote}</note>'
        # and add everything after the end of the footnote unchanged
        ret += parts[i+1]

        fn_id += 1

    return ret


##################################################################
##################################################################
# generate OSIS xml file

def create_osis(data, name, path):

    # namespace handle
    name_space = "http://www.bibletechnologies.net/2003/OSIS/namespace"

    # start XML element tree
    EleTree.register_namespace('', name_space)

    # create OSIS tags
    osis = EleTree.Element(f"{{{name_space}}}osis")
    text = EleTree.SubElement(osis, f"{{{name_space}}}osisText",
                         {"osisIDWork": name, "osisRefWork": "Bible"})

    # create header and work sub elements
    header = EleTree.SubElement(text, f"{{{name_space}}}header")
    work = EleTree.SubElement(header, f"{{{name_space}}}work", {"osisWork": name})

    # store name as work text
    EleTree.SubElement(work, f"{{{name_space}}}title").text = name

    prevbook = ""

    # loop over all data
    for entry in data:

        if entry == "Info":
            continue

        book = entry['book']
        shortbook = convert_bookname_to_osis(book)
        chapter = entry['chapter']

        if book != prevbook:

            # create new book sub element
            bdiv = EleTree.SubElement(text, f"{{{name_space}}}div",
                                {"type": "book", "osisID": shortbook})

            prevbook = book

        # create chapter sub element
        cdiv = EleTree.SubElement(bdiv, f"{{{name_space}}}chapter",
                                {"osisID": f"{shortbook}.{chapter}"})

        in_section = False

        for c in entry['content']:

            first = (c[0] if type(c) == list else c).lstrip()
            second = (c[1] if type(c) == list else "").lstrip()

            if first == "":
                continue

            # new section
            if first == "---":

                csec = EleTree.SubElement(cdiv, f"{{{name_space}}}div",
                                {"type": "section"})
                in_section = True

                continue

            if first.startswith("## "):

                title = EleTree.SubElement(cdiv, f"{{{name_space}}}title",
                                           {"type": "chapter"})
                title.text = first.split("# ")[1].strip()

                # first = "\n".join(first.split("\n")[1:])

                csec = EleTree.SubElement(cdiv, f"{{{name_space}}}div",
                                            {"type": "section"})
                in_section = True

                continue

            # create title
            elif first.startswith("#"):

                if not in_section:
                    csec = EleTree.SubElement(cdiv, f"{{{name_space}}}div",
                                                {"type": "section"})
                    in_section = True

                title = EleTree.SubElement(csec, f"{{{name_space}}}title",
                                           {"type": "section"})
                title.text = first.split("# ")[1].strip()

                continue

            if not in_section:
                csec = EleTree.SubElement(cdiv, f"{{{name_space}}}div",
                                            {"type": "section"})
                in_section = True

            # no verse data -> skip
            if second == "":
                continue

            # create verse sub element
            verse = EleTree.SubElement(csec, f"{{{name_space}}}verse",
                                    {"osisID": f"{shortbook}.{chapter}.{first}"})

            # poetry:
            if "\n" in second:

                parts = second.lstrip("\n").split("\n")

                poetry = EleTree.SubElement(verse, f"{{{name_space}}}lg")

                for p in parts:

                    if p.strip() == "":
                        continue

                    level = math.ceil((len(p) - len(p.lstrip(' ')))/4)

                    poetryline = EleTree.SubElement(poetry, f"{{{name_space}}}l",
                                                    {"level": str(level)})
                    poetryline.text = p.strip()

            else:

                # store plain verse text
                verse.text = second

    # create pretty xml from our string
    xml = minidom.parseString(EleTree.tostring(osis, encoding="utf-8")).toprettyxml(indent="  ")

    # format cross references and footnotes
    # we do that AFTER prettying the XML above to keep its formatting unchanged
    xml = make_xrefs(xml)
    xml = make_footnotes(xml)

    # store xml file
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)


##################################################################
##################################################################
# validate the xml to be sure

def validate_xml(path):

    from lxml import etree

    # if the parsing fails, then it is invalid XML
    try:
        etree.parse(path)
        if arg_verbose:
            print("  XML structure valid.")
    except etree.XMLSyntaxError as e:
        print("  XML validation error:")
        print(e)
        raise


##################################################################
##################################################################
# build module and install it in the right folder structure

def build_and_install(name, longname, language, osis_path, description, author):

    # we create the file structure in a temp directory
    install_root = Path("./build_temp")

    # the modules and mods.d directories
    module_path = install_root / "modules" / "texts" / "ztext" / name.lower()
    mods_d = install_root / "mods.d"

    # Clean old builds
    if module_path.exists():
        shutil.rmtree(module_path)
    if mods_d.exists():
        shutil.rmtree(mods_d)

    # create directories
    module_path.mkdir(parents=True)
    mods_d.mkdir(parents=True)

    # Compile module with `osis2mod`
    cmd = ["osis2mod", str(module_path), str(osis_path), "-z"]
    if arg_verbose:
        print("  Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True)

    # Create conf
    conf = f"""[{longname}]
DataPath=./modules/texts/ztext/{name.lower()}/
ModDrv=zText
Encoding=UTF-8
SourceType=OSIS
CompressType=ZIP
BlockType=BOOK
Lang={language}
Version=1.0
Description={description}
About=Built with Python Sword Builder
DistributionLicense=Public Domain
TextSource={author}
"""

    # write configuration file
    with open(mods_d / f"{name}.conf", "w") as f:
        f.write(conf)


##################################################################
##################################################################
# pack zip module file
def create_zip_module(name, root_dir):

    import zipfile

    zip_path = Path("output/")
    zip_path.mkdir(exist_ok=True)

    # handler for the zip file
    zf = zipfile.ZipFile(zip_path / f"{name}.zip", "w")

    # we descend down into where the root of the zip file is supposed to be
    # without that we will have additional root folders we don't want
    # we store the cwd to go back to where we came from at the end
    curcwd = os.getcwd()
    os.chdir(root_dir)

    # add the .conf file from the modules subdir
    for dirname, subdirs, files in os.walk("modules"):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    # add the compiled text files from the mods.d subdir
    for dirname, subdirs, files in os.walk("mods.d"):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))

    # done
    zf.close()
    # and go back to where we started
    os.chdir(curcwd)

##################################################################
##################################################################
# MAIN ENTRY FUNCTION to be called to start the full process

def generate_module(name, content,
                    longname,
                    language,
                    description,
                    author):

    # create temporary build directory
    build_dir = Path("./build_temp")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(exist_ok=True)

    # here we build the XML file
    osis_path = build_dir / f"{name}.osis.xml"

    if arg_verbose:
        print(" Creating OSIS...")
    create_osis(content, name, osis_path)

    if arg_verbose:
        print(" Validating XML...")
    validate_xml(str(osis_path))

    if arg_verbose:
        print(" Building + Installing to temporary directory...")
    build_and_install(name, longname, language, osis_path, description, author)

    if arg_verbose:
        print(" Creating ZIP module file...")
    create_zip_module(name, build_dir)

    if arg_verbose:
        print(" Cleaning up temporary files...")
    shutil.rmtree(build_dir)

########################################################################
########################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='SID',
                    description='SWORD bible module generator')

    parser.add_argument('--verbose', action='store_true', help="Enable verbose messages about what is happening.")
    parser.add_argument('--backend', default="", help=f"Automatically choose the specified backend.\nPossible values are: {", ".join(backends)}")
    parser.add_argument('--bible-version', default="", help="Automatically choose the specified bible version.")
    parser.add_argument('--confirm-rights', default=False, action='store_true', help="Don't ask whether I have the required permissions.")
    parser.add_argument('--ignore-cache', default=False, action='store_true', help="Don't use any cached files, re-download everything fresh.")
    parser.add_argument('--supported-versions', default=False, action='store_true', help="List all bible versions that are supported for the given backend.")

    args = parser.parse_args()

    arg_backend = args.backend
    arg_listsupported = args.supported_versions
    arg_version = args.bible_version
    arg_confirmrights = args.confirm_rights
    arg_cache = (not args.ignore_cache)
    arg_verbose = args.verbose

    ########################################################################

    print("")
    print(" ******************")
    print(" * WELCOME TO SID *")
    print(" ******************")
    print("")
    print("")

    ########################################################################

    if arg_backend == "":
        print("First choose which backend to use:")
        print("")
        for b in range(len(backends)):
            print(f"   ({b+1}) {backends[b]}")
        print("")
        print(" Enter choice (default: 1): ", end="")
        arg_backend = input()
        print("")

        if arg_backend == "":
            arg_backend = "1"
        if arg_backend.isdigit():
            arg_backend = int(arg_backend)-1
        else:
            arg_backend = -1

        if arg_backend < 0 or arg_backend >= len(backends):
            print(f" [Error] Invalid backend selected: {arg_backend}")
            print("")
            exit()

        arg_backend = backends[arg_backend]

    else:

        if arg_backend not in backends:
            print(f" The requested backend ({arg_backend}) is not available.")
            print(f" Possible backends are: {", ".join(backends)}")
            exit()

        if arg_verbose:
            print(f" Using provided backend: {arg_backend}")

    mod = __import__(f'modules.backend_{arg_backend.replace(".","")}', fromlist=[''])
    all_versions = mod.getSupportedVersions()

    ########################################################################

    if arg_listsupported:

        print(f" The supported bible versions of the backend '{arg_backend}' are:")
        print("")
        [print(f"{ver:>12} | {all_versions[ver][0]} ({all_versions[ver][1]})") for ver in all_versions]
        print("")

        exit()

    ########################################################################

    if arg_version == "":
        print("")
        print("What version do you want to create?")
        print("")
        print(" Enter choice (default: NIV): ", end="")
        arg_version = input()
        print("")

        if arg_version == "":
            arg_version = "NIV"

        if arg_version not in all_versions:
            print(f" The requested version ({arg_version}) is not supported by the selected backends.")
            print(f" Possible versions are: {", ".join(list(all_versions.keys()))}")
            exit()

    else:

        if arg_version not in all_versions:
            print(f" The requested version ({arg_version}) is not supported by the selected backends.")
            print(f" Possible versions are: {", ".join(list(all_versions.keys()))}")
            exit()

        if arg_verbose:
            print(f" Using provided version: {arg_version}")

    ########################################################################

    if not arg_confirmrights:
        print("")
        print("Depending on where you live, you might not have the automatic right to a digital version\n"
            "of a physical book. By continuing you confirm that you either have the right to or have\n"
            "obtained permission to make a digital copy of this bible version.")
        print("")
        cont = ""
        while cont != "y" and cont != "n":
            print(" Continue? [y/n] ", end="")
            cont = input().lower()
            if cont == "yes":
                cont = "y"
            elif cont == "no":
                cont = "n"
            if cont != "y" and cont != "n":
                print("  Please enter either y or n.")

        if cont == "n":
            print("")
            print("  Stopping here.")
            print("")
            exit()

    elif arg_verbose:
        print(" Automatically confirmed that you have the necessary rights.")

    ########################################################################

    print(" Working with this configuration:")
    print("")
    print(f"  Backend: {arg_backend}")
    print(f"  Version: {arg_version}")
    print(f"  Rights confirmed: yes")
    print(f"  Caching: {"yes" if arg_cache else "no"}")
    print("")
    print("")

    ########################################################################

    print(" Launching download. This might take a short while...")
    print("")

    data = mod.getData(arg_version, arg_verbose, arg_cache)

    ########################################################################

    print("")
    print(" Download completed! Generating module...")
    print("")

    generate_module(name=f"{arg_version}_{arg_backend.replace(".","")}",
                    content=data,
                    longname=all_versions[arg_version][0],
                    language=all_versions[arg_version][1],
                    description=f"{arg_version} ({arg_backend})",
                    author="SID")

    ########################################################################

    print(" Done!")
