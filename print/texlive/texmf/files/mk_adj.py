#!/usr/bin/env python3
"""
Generate adj.mk.

This script recursively inspects a directory looking for files with shebangs
(e.g. #!/bin/sh). Interpreter paths which are dynamic (depend upon LOCALBASE
and are not in OpenBSD base) are emitted into adj.mk under the appropriate make
variable for later substitution.

In case an unknown interpreter is encountered, or an interpreter path requires
manual patching, warnings are printed to stderr.

Usage: mk_adj.py <root-dir> <strip-prefix>

Arguments:
    root-dir: The directory from which to start searching.
    strip-prefix: The prefix to strip from each path in the output fragment.
"""

import os
import sys
import re
from collections import defaultdict


class UnknownInterpreterError(Exception):
    pass


# Decides if the first line of a file looks like a shebang and groups
# the interpreter path and arguments for later inspection
SHEBANG_PATTERN = re.compile("#\s*!\s*(\S+)(.*)")

# OpenBSD base interpreter paths (which can remain hard-coded).
BASE_INTERPRETERS = [
    "/bin/csh",
    "/bin/ksh",
    "/bin/sh",
    "/usr/bin/awk",
    "/usr/bin/perl",
]

SUBST_INTERPRETERS = {
    "bash": "BASH_ADJ_FILES",
    "fontforge": "FONTFORGE_ADJ_FILES",
    "lua": "LUA_ADJ_FILES",
    "perl": "MODPERL_ADJ_FILES",
    "python": "PYTHON2_ADJ_FILES",
    "python2": "PYTHON2_ADJ_FILES",
    "python2.7": "PYTHON2_ADJ_FILES",
    "python3": "PYTHON3_ADJ_FILES",
    #"python3.6": "PYTHON3_ADJ_FILES",
    "python3.7": "PYTHON3_ADJ_FILES",
    "ruby": "RUBY_ADJ_FILES",
    "ruby18": "RUBY_ADJ_FILES",
    "texlua": "TEXLUA_ADJ_FILES",
    "wish": "WISH_ADJ_FILES",
    "wish8.5": "WISH_ADJ_FILES",
}


def process_file(dirpath, filename, substs, strip_prefix):
    path = os.path.join(dirpath, filename)
    stripped_path = os.path.relpath(path, strip_prefix)

    try:
        fh = open(path, "rb")
    except IOError:
        # ignore broken symlinks
        if os.path.islink(path):
            return
        raise

    line1 = fh.readline().strip().decode(errors='ignore')
    fh.close()

    # There are some `.in` files with placeholder shebangs, ignore.
    if "@" in line1 and filename.endswith(".in"):
        return

    match = re.match(SHEBANG_PATTERN, line1)
    if not match:
        return  # No shebang

    interp = match.group(1)
    if interp in BASE_INTERPRETERS:
        # Fine as-is
        return

    interp = os.path.basename(interp)
    interp_args = match.group(2).split()

    # If the interpreter is `env`, we want to look at the next field
    if interp == "env":
        interp = interp_args[0]
        interp_args = interp_args[1:]

    subst_var = None
    try:
        subst_var = SUBST_INTERPRETERS[interp]
    except KeyError:
        raise UnknownInterpreterError(stripped_path, interp)
        return

    substs[subst_var].add(os.path.relpath(path, strip_prefix))


def main(root_dir, strip_prefix):
    # subsitutions: maps make variables to a set of files
    substs = defaultdict(set)

    # Files whose interpreters have extra args, thus need manual patching
    # Contains triples: (filename, interpreter, args)

    # Files whose interpreters are mysterious and unknown.
    # Contains pairs: (filename, interpreter)
    unknown_interp_files = []

    for dirpath, dirname, filenames in os.walk(root_dir):
        for filename in filenames:
            try:
                process_file(dirpath, filename, substs, strip_prefix)
            except UnknownInterpreterError as e:
                unknown_interp_files.append(e.args)

    print("# $OpenBSD$")
    print("#")
    print("# This file is automatically generated. Do not edit.\n")

    for subst_var, paths in sorted(substs.items(), key=lambda t: t[0]):
        joined_paths = " \\\n\t".join(sorted(paths))
        print("\n%s += \\\n\t%s" % (subst_var, joined_paths))

    # Emit any errors to stderr
    if unknown_interp_files:
        sys.stderr.write("\nwarning: the following files have "
                         "unknown interpreters:\n")
        for tup in unknown_interp_files:
            sys.stderr.write("    %s: %s\n" % tup)


if __name__ == "__main__":
    try:
        root_dir = sys.argv[1]
        strip_prefix = sys.argv[2]
    except IndexError:
        sys.stderr.write(__doc__)
        sys.exit(1)

    if not os.path.exists(root_dir):
        sys.stderr.write("mk_adj: root dir is non-existent\n")
        sys.exit(1)

    main(root_dir, strip_prefix)
