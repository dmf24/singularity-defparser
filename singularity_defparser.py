#!/usr/bin/env python3
import sys

# Simple definition parser.

# headers retrieved from here:
# https://github.com/sylabs/singularity/blob/213e05dd3b22b39e48e29ca3d325a10c339d7b3f/pkg/build/types/parser/deffile.go#L573
valid_headers = [
    "bootstrap",
    "from",
    "includecmd",
    "mirrorurl",
    "updateurl",
    "osversion",
    "include",
    "library",
    "registry",
    "namespace",
    "stage",
    "product",
    "user",
    "regcode",
    "productpgp",
    "registerurl",
    "modules",
    "otherurl&n",
    "fingerprints",
    "setopt"]

valid_sections = [
    "help",
    "setup",
    "files",
    "labels",
    "environment",
    "pre",
    "post",
    "runscript",
    "test",
    "startscript",
    "arguments"]

def blank_or_comment(line):
    sline = line.strip()
    return sline == '' or sline.startswith('#')

def trimcomment(line):
    return line.split('#')[0].strip()

def continueline(trimline):
    return trimline.endswith('\\')

def get_section_name(line):
    return line[line.index('%')+1:].split(' ')[0]

def parsefile(filename):
    txt = open(filename, 'r').readlines()
    lines = open(filename, 'r').readlines()
    sections_begun = False
    continuing = False
    current_header = None
    current_section = None
    results = {'headers': {}, 'sections': {}}
    for line in lines:
        if not sections_begun:
            if not blank_or_comment(line):
                trimline = trimcomment(line)
                if continuing:
                    if continueline(trimline):
                        results['headers'][current_header] += trimline[:-1]
                    else:
                        results['headers'][current_header] += trimline
                        continuing = False
                        current_header = None
                else:
                    if not trimline.startswith('%'):
                        linetokens = trimline.split(':')
                        current_header = linetokens[0].lower()
                        rest = ':'.join(linetokens[1:])
                        continuing = continueline(rest)
                        results['headers'][current_header] = rest
                    else:
                        sections_begun = True
        if sections_begun:
            if trimline.startswith('%'):
                current_section = get_section_name(trimline)
                # The actual parser does some special stuff with files that I'm skipping for now.
                # https://github.com/sylabs/singularity/blob/213e05dd3b22b39e48e29ca3d325a10c339d7b3f/pkg/build/types/parser/deffile.go#L136
                results['sections'].setdefault(current_section, [])
            else:
                results['sections'][current_section].append(line)
    return results
        
def validate(results):
    returncode = 0
    for header in results['headers'].keys():
        if header not in valid_headers:
            sys.stderr.write("invalid header: %s\n" % header)
            returncode = returncode | 1
    for section in results['sections'].keys():
        if section not in valid_sections:
            sys.stderr.write("invalid section name: %s\n" % section)
            returncode = returncode | 2
    return returncode

def usage():
    print('%s <singularity_definition_file>' % sys.argv[0])
    print()
    print("This script parses a singularity file and returns the following exit codes:")
    print("  0 - success")
    print("  1 - invalid header")
    print("  2 - invalid section")
    print("  3 - invalid header and section")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            sys.stderr.write('Warning: to get usage, run script with no arguments.\n')
        if len(sys.argv) > 2:
            sys.stderr.write('Warning: multiple arguments given, only the first argument will be processed.\n')
        sys.exit(validate(parsefile(sys.argv[1])))
    else:
        usage()
