from io import StringIO
import re

class Surlex(object):
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

    def translate_capture(self, capture):
        pieces = capture.split(':')
        if len(pieces) == 2:
            regex = pieces[1]
            if pieces[0] == '':
                # no key provided, assume no capture, just literal regex
                return regex
        else:
            regex = '.+'
        key = pieces[0]
        return '(?P<%s>%s)' % (key, regex)

    def translate(self):
        output = ''
        while True:
            c = self.read(1)
            if c == '':
                # end of surlex
                break
            elif c == '\\':
                # escape with backslash
                output += self.read(1)
            elif c == '<':
                # hit capture, read to end of capture and translate
                capture = self.read_until('>')
                output += self.translate_capture(capture)
            elif c == '*':
                # wildcard, output .*
                output += '.*'
            elif c == ')':
                # surlex optional match, convert to regex ()?
                output += ')?'
            elif c in ('.'):
                # output regex needs to escape "." as to not match everything
                output += '\\' + c
            else:
                # literal output (such as "/")
                output += c
        return output

    #alias to translate
    to_regex = translate

def surlex_to_regex(surlex):
    surlex = Surlex(surlex)
    return surlex.to_regex()

def match(surlex, subject):
    regex = surlex_to_regex(surlex)
    m = re.match(regex, subject)
    if m:
        return m.groupdict()
