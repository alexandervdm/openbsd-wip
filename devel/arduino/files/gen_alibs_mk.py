#!/usr/bin/env python2.7
#
# Compute source files and include dirs for arduino std lib.
# (c) 2015 Edd Barrett <edd@openbsd.org>

import sys
import os

class Lib(object):
    def __init__(self, path, cpps, inc_dirs):
        self.path = path
        self.cpps = cpps
        self.inc_dirs = set(inc_dirs)

def collect_lib_files(path):
    cpps = []
    inc_dirs = []

    ls = os.listdir(path)
    for f in ls:
        fpath = os.path.join(path, f)
        if os.path.isfile(fpath):
            if f.endswith(".cpp") or f.endswith(".c"):
                cpps.append(fpath)
            elif f.endswith(".h"):
                inc_dirs.append(os.path.dirname(fpath))
        elif os.path.isdir(fpath):
            n_cpps, n_inc_dirs = collect_lib_files(fpath) # recurse
            cpps.extend(n_cpps)
            inc_dirs.extend(n_inc_dirs)

    return cpps, inc_dirs

def collect_libs(ad_base):
    # name * arch -> Lib
    lib_tab = {}
    lib_names = set()

    search =  {
        "common":   os.path.join(ad_base, "libraries"),
        "avr":      os.path.join(ad_base, "avr", "libraries"),
        "sam":      os.path.join(ad_base, "sam", "libraries"),
    }

    for arch, path in search.iteritems():
        print("Searching %s" % path)
        ls = os.listdir(path)

        for fln in ls:
            full_path = os.path.join(path, fln)
            if os.path.isdir(full_path):
                cpps, inc_dirs = collect_lib_files(full_path)
                lib_names |= set([fln])
                lib_tab[fln, arch] = Lib(full_path, cpps, inc_dirs)
            else:
                assert False # shouldn't happen

    return lib_tab, lib_names

MAKE_HEADER = "# Autogenerated! Do not manually edit.\n"

def emit_make_frag(lib_tab, lib_names):
    with open("alibs.mk", "w") as mf:
        w = mf.write
        w(MAKE_HEADER)

        for lib in sorted(lib_names):
            for arch in ["avr", "sam"]:
                common_lib = lib_tab.get((lib, "common"), None)
                plat_lib = lib_tab.get((lib, arch), None)

                cpps, incs = [], []
                if common_lib:
                    cpps.extend(common_lib.cpps)
                    incs.extend(common_lib.inc_dirs)

                if plat_lib:
                    cpps.extend(plat_lib.cpps)
                    incs.extend(plat_lib.inc_dirs)

                local = "/usr/local/share/arduino/"
                asupport = "arduino-support/"
                cpps = [("\t%s" % x).replace(local, asupport) for x in cpps]
                incs = [("\t-I%s" % x).replace(local, asupport) for x in incs]

                var_prefix = "%s_%s_" % (lib, arch)
                if cpps or incs:
                    w("# %s for %s\n" % (lib, arch))
                    if cpps:
                        w("%sCPPS = \\\n%s\n" %
                          (var_prefix, " \\\n".join(cpps)))
                    if incs:
                        w("%sINC_DIRS = \\\n%s\n" %
                          (var_prefix, " \\\n ".join(incs)))
                    w("\n")

def main(ad_base):
    lib_tab, lib_names = collect_libs(ad_base)
    emit_make_frag(lib_tab, lib_names)

ARDUINO_BASE = "/usr/local/share/arduino/"
if __name__ == "__main__":
    main(ARDUINO_BASE)
