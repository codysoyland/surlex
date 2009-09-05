from io import StringIO
import re

class SurlexParser(object):
    def __init__(self, surlex):
        self.surlex = surlex
        self.io = StringIO(self.surlex)

    def read(self, count):
        return self.io.read(count)

    def read_until(self, char):
        output = ''
        while 1:
            c = self.read(len(char))
            if c == char:
                return output
            elif c == '\\':
                output += self.read(1)
            else:
                output += c
        return output

    def parse_capture(self, capture):
        pieces = capture.split(':')
        if len(pieces) == 2:
            regex = pieces[1]
        else:
            regex = '.+'
        key = pieces[0]
        if key[0] == '#':
            key = key[1:]
            regex = '[0-9]+'
        return '(?P<%s>%s)' % (key, regex)

    def parse(self):
        while True:
            c = self.read(1)
            if c == '':
                raise StopIteration
            elif c == '<':
                capture = self.read_until('>')
                yield self.parse_capture(capture)
            elif c == '\\':
                yield self.read(1)
            elif c == '*':
                yield '.*'
            elif c == ')':
                yield ')?'
            elif c == '{':
                yield self.read_until('}')
            elif c in ('.'):
                yield '\\' + c
            else:
                yield c
    def to_regex(self):
        return ''.join(self.parse())

def surlex_to_regex(surlex):
    surlex = SurlexParser(surlex)
    return surlex.to_regex()

def match(surlex, subject):
    regex = surlex_to_regex(surlex)
    m = re.match(regex, subject)
    if m:
        return m.groupdict()
