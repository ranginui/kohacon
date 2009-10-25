## ----------------------------------------------------------------------------
import logging
import cgi
import re

## ----------------------------------------------------------------------------
# regexes

heading = re.compile('^!([123456])\s+(.*)', re.DOTALL)
pre = re.compile('^\s')
html = re.compile('^<\s(.*)', re.DOTALL)
blockquote = re.compile('^"\s+(.*)', re.DOTALL)

## ----------------------------------------------------------------------------

def esc(text):
    return cgi.escape(text, True)

def text2html(text):
    # join lines up which should be together (ie. the line ends with '\')
    # Perl: $text =~ s{ \\\n\s+ }{ }gxms;

    html = ''
    chunks = text.split('\n\n')
    for chunk in chunks:
        html = html + parse_chunk(chunk) + '\n'

    return html

def parse_chunk(chunk):
    m = heading.match(chunk)
    if m:
        return '<h%s>%s</h%s>' % (m.group(1), parse_inline(m.group(2)), m.group(1))

    m = pre.match(chunk)
    if m:
        return '<pre>' + esc(chunk) + '</pre>'

    m = html.match(chunk)
    if m:
        return m.group(1)

    m = blockquote.match(chunk)
    if m:
        return '<blockquote>' + parse_inline(esc(m.group(1))) + '</blockquote>'

    # just a normal paragraph
    return '<p>' + parse_inline(esc(chunk)) + '</p>'

def parse_inline(line):
    return line

def parse_list(chunk):
    return chunk

## ----------------------------------------------------------------------------
