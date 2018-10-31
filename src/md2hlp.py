#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# vim: set ts=4 ai :
#
# $Id: md2hlp.py $
# $Author: assinie <github@assinie.info> $
# $Date: 2018-10-30 $
# $Revision: 0.2 $
#
# ------------------------------------------------------------------------------

from __future__ import print_function

import os
import sys
import argparse

import ConfigParser
import re
import textwrap

from pprint import pprint

# ------------------------------------------------------------------------------
__program_name__ = 'md2hlp'
__description__ = "Convert from Markdown to Orix Help"
__plugin_type__ = 'TOOL'
__version__ = '0.2'

# ------------------------------------------------------------------------------
heading = re.compile(r'^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')

list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
link = re.compile(r'\[([^\]]+)]\(([^)]+)\)')

repls = list()
for i in range(27):
    repls.append(('^' + chr(64 + i), chr(i)))


# ------------------------------------------------------------------------------
def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


# ------------------------------------------------------------------------------
def lineWrap(line, initial='      ', subsequent='  ', break_on_hyphens=True):

    initial = initial.replace('_', ' ')
    if initial and initial[0] in ['"', "'"]:
        initial = initial[1:-1]

    subsequent = subsequent.replace('_', ' ')
    if subsequent and subsequent[0] in ['"', "'"]:
        subsequent = subsequent[1:-1]

    line = reduce(lambda a, kv: a.replace(*kv), repls, line)
    initial = reduce(lambda a, kv: a.replace(*kv), repls, initial)
    subsequent = reduce(lambda a, kv: a.replace(*kv), repls, subsequent)

    line = textwrap.wrap(line,
                         width=40,
                         initial_indent=initial,
                         subsequent_indent=subsequent,
                         break_on_hyphens=break_on_hyphens,
                         replace_whitespace=False)

    for i in range(len(line)):
        line[i] = ("{:<40}".format(line[i]))

    line = ''.join(line)

    return line


# ------------------------------------------------------------------------------
class md2hlp():
    def __init__(self, mdfile, config, verbose=0):
        self.mdfile = mdfile
        self.config = ConfigParser.SafeConfigParser()
        self.verbose = verbose

        self.config.read(config)

    def convert(self):
        head = 'DEFAULT'
        paragraph = ''
        first = True
        output = ''

        if self.mdfile is not None:
            fd = open(self.mdfile)
        else:
            fd = sys.stdin

        if fd:
            line = fd.readline()

            while line:
                line = line.strip(' \n')
                # print line, len(line)

                pos = 1
                l = link.search(line,pos)
                while l:
                    if self.verbose > 1:
                        eprint('Found link', l.groups(), l.span(2) )

                    line = line[:l.start(0)].strip(' ') + '^D' + l.group(1) + '^G' + line[l.end(0):].strip(' ')
                    pos = l.start(0) + len(l.group(1))
                    l = link.search(line,pos)

                h = heading.match(line)
                l = list_bullet.match(line)

                if not line and paragraph:
                    output += lineWrap(paragraph,
                                       initial=self.config.get(head, 'initial indent'),
                                       subsequent=self.config.get(head, 'subsequent indent'),
                                       break_on_hyphens=self.config.getboolean(head, 'break on hyphens'))
                    output += ' ' * 40
                    paragraph = ''
                    first = True

                if (h or l) and paragraph:
                    output += lineWrap(paragraph,
                                       initial=self.config.get(head, 'initial indent'),
                                       subsequent=self.config.get(head, 'subsequent indent'),
                                       break_on_hyphens=self.config.getboolean(head, 'break on hyphens'))
                    paragraph = ''

                if h:
                    level = len(h.group(1))
                    head = h.group(2)
                    headx = 'Heading%d' % level

                    if self.verbose > 1:
                        eprint('Found heading', h.groups(), h.span(2), 'Level: ', level, head)

                    if self.config.has_section(head):
                        if self.verbose > 1:
                            eprint(self.config.items(head))

                    elif self.config.has_section(headx):
                        head = headx
                        if self.verbose > 1:
                            eprint(self.config.items(headx))

                    else:
                        head = 'DEFAULT'

                    # Saut de ligne ou ligne avant
                    if self.config.has_option(head, 'text'):
                        output += lineWrap(self.config.get(head, 'text'), initial='', subsequent='')
                    elif not first:
                        output += ' ' * 40

                    # Alignement
                    initial = self.config.get(head, 'head')
                    if self.config.get(head, 'align') == '^':
                        l = (40 - len(h.group(2)) - len(self.config.get(head, 'head'))) / 2
                        initial = ' ' * l + initial

                    elif self.config.get(head, 'align') == '>':
                        l = 40 - len(h.group(2)) - len(self.config.get(head, 'head'))
                        initial = ' ' * l + initial

                    # Ligne a afficher
                    line = lineWrap(h.group(2),
                                    initial=initial,
                                    subsequent='')

                    output += line

                    # Affiche une deuxieme fois si double hauteur
                    if '^J' in self.config.get(head, 'head'):
                        output += line

                    first = False

                elif l:
                    if self.verbose > 1:
                        eprint('Found list', l.group(), l.span(0), line[l.end(0):])

                    output += lineWrap(line[l.end(0):],
                                       initial=self.config.get(head, 'initial indent') + self.config.get(head, 'list'),
                                       subsequent='')

                    first = False

                else:
                    if paragraph:
                        paragraph = paragraph + ' ' + line
                    else:
                        paragraph = line

                line = fd.readline()

            if paragraph:
                output += lineWrap(paragraph,
                                   initial=self.config.get(head, 'initial indent'),
                                   subsequent=self.config.get(head, 'subsequent indent'),
                                   break_on_hyphens=self.config.getboolean(head, 'break on hyphens'))

        else:
            eprint("Error, can't open '%s' file" % self.mdfile)
            sys.exit(1)

        return output


# ------------------------------------------------------------------------------
def main():

    parser = argparse.ArgumentParser(prog=__program_name__, description=__description__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--config', '-c', required=False, type=str, default=None, help='Configuration filename')
    parser.add_argument('--file', '-f', required=False, type=str, default=None, help='Input filename')
    parser.add_argument('--output', '-o', required=False, type=str, default=None, help='output filename')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='increase verbosity')
    parser.add_argument('--version', '-V', action='version', version='%%(prog)s v%s' % __version__)

    args = parser.parse_args()

    env_var = os.environ.get(__program_name__.upper() + '_PATH')

    if args.config is not None:
        if not os.path.isfile(args.config):
            eprint("Configuration file '%s' not found" % args.config)
            sys.exit(1)
    else:
        if not os.path.isfile(__program_name__ + '.cfg'):
            if env_var is not None:
                if not os.path.isfile('%s/%s.cfg' % (env_var, __program_name__)):
                    eprint("Configuration file '%s' not found" % args.config)
                    sys.exit(1)
                else:
                    args.config = '%s/%s.cfg' % (env_var, __program_name__)
            else:
                eprint("Configuration file '%s.cfg' not found" % __program_name__)
                sys.exit(1)
        else:
            args.config = '%s.cfg' % (__program_name__)


    if args.file is not None:
        if not os.path.isfile(args.file):
            eprint("File '%s' not found" % args.template)
            sys.exit(1)

    if args.verbose:
        eprint('')
        eprint('Config file: ', args.config)
        eprint('Input file : ', args.file)
        eprint('Output file: ', args.output)
        eprint('')

    hlpfile = md2hlp(args.file, args.config, args.verbose).convert()

    if args.output is None:
        print(hlpfile)
    else:
        with open(args.output, 'wb') as fd:
            fd.write(hlpfile)


# ------------------------------------------------------------------------------
if __name__ == '__main__':

        main()
