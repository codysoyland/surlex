try:
    # post 2.4
    from io import StringIO
except ImportError:
    # for 2.4
    from StringIO import StringIO
import re

class MacroRegistry(object):
    # registering to the class makes the registry global
    # maybe we'll change this in the future
    macros = {}
    @classmethod
    def register(cls, macro, regex):
        cls.macros[macro] = regex


# todo: make regexes more restrictive
# (ie: 'm' should only match months 1-12. currently, it matches 0-99)
register_macro = MacroRegistry.register
register_macro('Y', r'\d{4}') # year, including century
register_macro('y', r'\d{2}') # year, not including century
register_macro('M', r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)') # month, abbreviated
register_macro('m', r'\d{1,2}') # month, 1 or 2 digit
register_macro('d', r'\d{1,2}') # day, 1 or 2 digit
register_macro('#', r'\d+') # number, any length
register_macro('s', r'[\w-]+') # slug

class Surlex(object):
    def __init__(self, surlex):
        self.translated = False
        self.surlex = surlex
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
                raise Exception('Malformed surlex. Expected %s.' % char)
            else:
                output += c
        return output

    def resolve_macro(self, macro):
        try:
            return (macro, MacroRegistry.macros[macro])
        except KeyError:
            raise Exception('Macro "%s" not defined' % macro)

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
                macro_name, regex = self.resolve_macro(macro)
                self.groupmacros[key] = macro_name
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

def surlex_to_regex(surlex):
    return Surlex(surlex).translate()

def parsed_surlex_object(surlex):
    object = Surlex(surlex)
    object.translate()
    return object

def match(surlex, subject):
    return Surlex(surlex).match(subject)
