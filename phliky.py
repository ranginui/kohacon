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

# inline regexes
balanced = re.compile(r'\\(\w+){([^{}]*?)}', re.DOTALL | re.VERBOSE)

## ----------------------------------------------------------------------------

def esc(text):
    return cgi.escape(text, True)

def text2html(text):
    html = ''
    # these \r's were doing my head in, so get rid of them
    text = re.sub('\r', '', text)
    for chunk in text.split('\n\n'):
        html = html + do_chunk(chunk) + '\n'

    return html

def do_chunk(chunk):
    m = heading.search(chunk)
    if m:
        return '<h%s>%s</h%s>' % (m.group(1), do_inline(esc(m.group(2))), m.group(1))

    m = pre.search(chunk)
    if m:
        return '<pre>' + esc(chunk) + '</pre>'

    m = html.search(chunk)
    if m:
        return m.group(1)

    m = blockquote.search(chunk)
    if m:
        return '<blockquote>' + do_inline(esc(m.group(1))) + '</blockquote>'

    # just a normal paragraph
    return '<p>' + do_inline(esc(chunk)) + '</p>'

def do_inline(line):
    finished = False
    while not finished:
        m = balanced.search(line)
        if m:
            type = m.group(1)
            str = m.group(2)

            if type == 'b':
                line = balanced.sub(r'<strong>\2</strong>', line, 1)
                # line[m.start():m.end()] = '<strong>%s</strong' % str

            elif type == 'i':
                line = balanced.sub(r'<em>\2</em>', line, 1)

            elif type == 'u':
                line = balanced.sub(r'<span style="text-decoration: underline;">\2</span>', line, 1)

            elif type == 'c':
                line = balanced.sub(r'<code>\2</code>', line, 1)

            elif type == 'l':
                (text, href) = str.split(r'|')
                line = balanced.sub('<a href="%s">%s</a>' % (href, text), line, 1)

            elif type == 'h':
                line = balanced.sub('<a href="%s">%s</a>' % (str, str), line, 1)

            elif type == 'w':
                line = balanced.sub('<a href="%s.html">%s</a>' % (str, str), line, 1)

            elif type == 'img':
                (title, src) = str.split(r'|')
                line = balanced.sub('<img src="%s" title="%s" />' % (src, title), line, 1)

            elif type == 'a':
                (abbr, abbreviation) = str.split(r'|')
                line = balanced.sub('<acronym title="%s">%s</acronym>' % (abbreviation, abbr), line, 1)

            elif type == 'br':
                line = balanced.sub('<br />', line, 1)

            elif type == 'copy':
                line = balanced.sub('&copy;', line, 1)

            else:
                line = balanced.sub(r'\[\1]{\2}', line, 1)
        else:
            finished = True

    return line

def list(chunk):
    return chunk

## ----------------------------------------------------------------------------
