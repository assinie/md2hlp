#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# vim: set ts=4 ai :
#
# $Id: md2hlp.py $
# $Author: assinie <github@assinie.info> $
# $Date: 2018-11-02 $
# $Revision: 0.3 $
#
# ------------------------------------------------------------------------------
import os
import sys
import argparse

import re
import textwrap

from functools import reduce

from configparser import ConfigParser


# ------------------------------------------------------------------------------
__program_name__ = 'md2hlp'
__description__ = "Convert from Markdown to Orix Help"
__plugin_type__ = 'TOOL'
__version__ = '0.3'

# ------------------------------------------------------------------------------
heading = re.compile(r'^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')

list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')

link = re.compile(r'\[([^\]]+)]\(([^)]+)\)')
italic = re.compile(r'\*([^ ][^\*]+)\*')
bold = re.compile(r'\*\*([^ ][^\*]+)\*\*')
underline = re.compile(r'__([^ ][^_]+)__')
strike_through = re.compile(r'~~([^_]+)~~')
quote = re.compile(r'` *([^`]+) *`')

cite = re.compile(r'^ {,3}> (.+)')
quote_block = re.compile(r'^```')

inverse_style = re.compile(r'\^v(((?!\^v).)+)\^v')

styles = {'link': link, 'bold': bold, 'italic': italic, 'underline': underline,
          'strike_through': strike_through, 'quote': quote, 'cite': cite}


repls = list()
for i in range(27):
    repls.append(('^' + chr(64 + i), chr(i)))

inverse_char = list()
for i in range(32, 125):
    inverse_char.append((chr(i), chr(i+128)))

escape_chars = list()
for i in "\\`*_{}[]()#+-.!~^":
    escape_chars.append(('\\' + i, i))


# ------------------------------------------------------------------------------
def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


# ------------------------------------------------------------------------------
def lineWrap(line, initial='      ', subsequent='  ', break_on_hyphens=True, keep_spaces=False):

    initial = initial.replace('_', ' ')
    if initial and initial[0] in ['"', "'"]:
        initial = initial[1:-1]

    subsequent = subsequent.replace('_', ' ')
    if subsequent and subsequent[0] in ['"', "'"]:
        subsequent = subsequent[1:-1]

    line = reduce(lambda a, kv: a.replace(*kv), repls, line)
    line = reduce(lambda a, kv: a.replace(*kv), escape_chars, line)
    initial = reduce(lambda a, kv: a.replace(*kv), repls, initial)
    subsequent = reduce(lambda a, kv: a.replace(*kv), repls, subsequent)

    if not keep_spaces:
        line = re.sub(r' +', ' ', line)

    line = textwrap.wrap(line,
                         width=40,
                         initial_indent=initial,
                         subsequent_indent=subsequent,
                         break_on_hyphens=break_on_hyphens,
                         # expand_tabs=False,
                         replace_whitespace=False)

    for i in range(len(line)):
        line[i] = ("{:<40}".format(line[i]))

    line = ''.join(line)

    return line


# ------------------------------------------------------------------------------
class md2hlp():
    def __init__(self, mdfile, config, verbose=0):
        self.mdfile = mdfile
        self.config = ConfigParser()
        self.verbose = verbose

        self.config.read(config)

    def convert(self):
        head = 'DEFAULT'
        paragraph = ''
        first = True
        output = ''
        cite_start = ''
        quote_block_found = False

        if self.mdfile is not None:
            fd = open(self.mdfile)
        else:
            fd = sys.stdin

        if fd:
            line = fd.readline()

            while line:
                if quote_block_found:
                    # Supprime les "espaces" uniquement en fin de ligne
                    line = line.rstrip(' \n\r')

                else:
                    # Supprime les "espaces" et début et à la fin de la ligne
                    line = line.strip(' \n\r')

                if self.verbose > 1:
                    eprint(line)

                if line == '\\':
                    output += ' ' * 40
                    line = ''

                if quote_block.search(line):
                    if self.verbose > 1:
                        eprint('Quote bloc found')

                    if quote_block_found:
                        # Ajoute une ligne vide après le bloc
                        output += ' ' * 40

                        quote_block_found = False

                    else:
                        quote_block_found = True

                    line = ''

                for style_name in list(styles.keys()):
                    if self.config.has_option(head, style_name):
                        (style_start, style_stop) = self.config.get(head, style_name).split(',')

                        style_start = style_start.replace('_', ' ')
                        if style_start and style_start[0] in ['"', "'"]:
                            style_start = style_start[1:-1]

                        style_stop = style_stop.replace('_', ' ')
                        if style_stop and style_stop[0] in ['"', "'"]:
                            style_stop = style_stop[1:-1]

                    else:
                        style_start = ''
                        style_stop = ''

                    pos = 0
                    block = styles[style_name].search(line, pos)
                    while block:
                        if self.verbose > 1:
                            eprint('Found '+style_name, block.groups(), block.span(1))
                            eprint('style_start: ', style_start, ', style_stop: ', style_stop, 'cite_start: ', cite_start)

                        if block.start(0) == 0 or (block.start(0) > 0 and line[block.start(0)-1] != "\\"):
                            if style_name == 'cite' and cite_start:
                                line = line[:block.start(0)] + block.group(1) + line[block.end(0):]

                            else:
                                if '^v' not in style_start:
                                    # On suppose qu'il y a un caractère de contrôle donc on supprime tous les espaces
                                    # avant et après le style puisqu'il sera remplacé par le caractère de contrôle.
                                    # Sinon il ne faudrait pas faire ce test et ne conserver que la ligne du "else:"
                                    line = line[:block.start(0)].strip(' ') + style_start + block.group(1) + style_stop + line[block.end(0):].strip(' ')
                                else:
                                    line = line[:block.start(0)] + style_start + block.group(1) + style_stop + line[block.end(0):]

                            if style_name == 'cite':
                                cite_start = style_start

                            pos = block.start(0) + len(block.group(1))

                        else:
                            pos = block.start(0)+1

                        block = styles[style_name].search(line, pos)

                pos = 0
                block = inverse_style.search(line, pos)
                while block:
                    if self.verbose > 1:
                        eprint('Found inverse', block.groups(), block.span(1))

                    if block.start(0) == 0 or (block.start(0) > 0 and line[block.start(0)-1] != "\\"):
                        inverse = reduce(lambda a, kv: a.replace(*kv), inverse_char, block.group(1))

                        line = line[:block.start(0)] + inverse + line[block.end(0):]
                        pos = block.start(0) + len(block.group(1))
                    else:
                            pos = block.start(0)+1

                    block = inverse_style.search(line, pos)

                h = heading.match(line)
                liste = list_bullet.match(line)

                if not line and paragraph:
                    output += lineWrap(paragraph,
                                       initial=self.config.get(head, 'initial indent'),
                                       subsequent=self.config.get(head, 'subsequent indent')+cite_start,
                                       break_on_hyphens=self.config.getboolean(head, 'break on hyphens'))
                    output += ' ' * 40
                    paragraph = ''
                    first = True
                    cite_start = ''

                if (h or liste) and paragraph:
                    output += lineWrap(paragraph,
                                       initial=self.config.get(head, 'initial indent'),
                                       subsequent=self.config.get(head, 'subsequent indent')+cite_start,
                                       break_on_hyphens=self.config.getboolean(head, 'break on hyphens'))
                    paragraph = ''
                    cite_start = ''

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
                        length = (40 - len(h.group(2)) - len(self.config.get(head, 'head'))) // 2
                        initial = ' ' * length + initial

                    elif self.config.get(head, 'align') == '>':
                        length = 40 - len(h.group(2)) - len(self.config.get(head, 'head'))
                        initial = ' ' * length + initial

                    # Ligne a afficher
                    line = lineWrap(h.group(2),
                                    initial=initial,
                                    subsequent=''+cite_start)

                    output += line

                    # Affiche une deuxieme fois si double hauteur
                    if '^J' in self.config.get(head, 'head'):
                        output += line

                    first = False

                elif liste:
                    if self.verbose > 1:
                        eprint('Found list', liste.group(), liste.span(0), line[liste.end(0):])

                    output += lineWrap(line[liste.end(0):],
                                       initial=self.config.get(head, 'initial indent') + self.config.get(head, 'list'),
                                       subsequent='' + cite_start)

                    first = False
                    cite_start = ''

                else:
                    if paragraph:
                        paragraph = paragraph + ' ' + line
                    else:
                        if quote_block_found:
                            if self.config.has_option(head, 'quote block'):
                                initial = self.config.get(head, 'quote block')
                                subsequent = initial
                            else:
                                initial = ''
                                subsequent = ''

                            output += lineWrap(line,
                                               initial=initial,
                                               subsequent=initial,
                                               break_on_hyphens=self.config.getboolean(head, 'break on hyphens'),
                                               keep_spaces=True)

                        else:
                            paragraph = line

                line = fd.readline()

            if paragraph:
                output += lineWrap(paragraph,
                                   initial=self.config.get(head, 'initial indent'),
                                   subsequent=self.config.get(head, 'subsequent indent')+cite_start,
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
        with open(args.output, 'w') as fd:
            fd.write(hlpfile)


# ------------------------------------------------------------------------------
if __name__ == '__main__':

        main()
