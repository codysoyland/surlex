try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import re
from exceptions import MalformedSurlex
from macros import MacroRegistry, DefaultMacroRegistry

class Surlex(object):
    def __init__(self, surlex, macro_registry=DefaultMacroRegistry()):
        self.translated = False
        self.surlex = surlex
        self.macro_registry = macro_registry
        self.io = StringIO(self.surlex)
        self.groupmacros = {}

    def read(self, count):
        return self.io.read(count)

    def read_until(self, char):
        output = ''
        while 1:
            c = self.read(1)
            if c == char:
                return output
            elif c == '\\':
                next = self.read(1)
                if next == char:
                    output += next
                else:
                    output += '\\' + next
            elif c == '':
                raise MalformedSurlex('Malformed surlex. Expected %s.' % char)
            else:
                output += c
        return output

    def resolve_macro(self, macro):
        return self.macro_registry.get(macro)

    def translate_capture(self, capture):
        capture_io = StringIO(capture)
        key = ''
        # if no regex or macro is provided, default to match anything (.+)
        regex = '.+'
        while True:
            char = capture_io.read(1)
            if char == '': break
            elif char == ':':
                # macro match
                macro = capture_io.read()
                regex = self.resolve_macro(macro)
                self.groupmacros[key] = macro
            elif char == '=':
                # regex match
                regex = capture_io.read()
            else:
                key += char
        if key == '':
            # no key provided, assume no capture, just literal regex
            return regex
        else:
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
            elif c in '[]{}.+|?':
                # output regex needs to escape regex metacharacters
                output += '\\' + c
            else:
                # literal output (such as "/")
                output += c
        self.regex = output
        self.translated = True
        return output

    #alias to translate
    to_regex = translate

    def match(self, subject):
        if not self.translated:
            self.translate()
        m = re.match(self.regex, subject)
        if m:
            return m.groupdict()

