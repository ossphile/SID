import argparse
import textwrap
from modules.worker import *

########################################################################
########################################################################

parser = argparse.ArgumentParser(
                prog='SID',
                description='SWORD bible module generator')

parser.add_argument('--verbose', action='store_true', help="Enable verbose messages about what is happening.")
parser.add_argument('--backend', default="", help=f"Automatically choose the specified backend.\nPossible values are: {", ".join(backends)}")
parser.add_argument('--bible-version', default="", help="Automatically choose the specified bible version.")
parser.add_argument('--confirm-rights', default=False, action='store_true', help="Don't ask whether I have the required permissions.")
parser.add_argument('--supported-versions', default=False, action='store_true', help="List all bible versions that are supported for the given backend.")

args = parser.parse_args()

arg_backend = args.backend
arg_listsupported = args.supported_versions
arg_version = args.bible_version
arg_confirmrights = args.confirm_rights
arg_verbose = args.verbose

########################################################################

print("")
print(" ******************")
print(" * WELCOME TO SID *")
print(" ******************")
print("")

########################################################################

if arg_backend == "":
    print("")
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

    mod = __import__(f'modules.backend_{arg_backend.replace(".","")}', fromlist=[''])

else:

    if arg_backend not in backends:
        print(f" The requested backend ({arg_backend}) is not available.")
        print(f" Possible backends are: {", ".join(backends)}")
        exit()

print(f"      Using backend: {arg_backend}")
mod = __import__(f'modules.backend_{arg_backend.replace(".","")}', fromlist=[''])
desc = textwrap.fill(mod.getDescription(), 75)
[print(f"{' '*21}{l}") for l in desc.split("\n")]
print("")

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

print(f" Requesting Version: {arg_version} ({all_versions[arg_version][0]})")

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

    print("")

########################################################################

print("   Rights confirmed: yes")
print("")

########################################################################

print(" Launching download. This might take a little while...")
print("")

data = mod.getData(arg_version, arg_verbose)

########################################################################

print("")
print(" Download completed! Generating module...")

generate_module(name=f"{arg_version}_{arg_backend.replace(".","")}",
                content=data,
                longname=all_versions[arg_version][0],
                language=all_versions[arg_version][1],
                description=f"{arg_version} ({arg_backend})",
                author="SID",
                verbose=arg_verbose)

########################################################################

print("")
print(" Done!")
