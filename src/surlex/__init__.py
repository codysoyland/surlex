try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import re
from exceptions import MalformedSurlex, MacroDoesNotExist

class MacroRegistry(object):
    macros = {}
    def __init__(self, macros={}):
        all_macros = {}
        all_macros.update(self.macros)
        all_macros.update(macros)
        self.macros = all_macros

    def get(self, macro_name):
        try:
            return self.macros[macro_name]
        except KeyError:
            raise MacroDoesNotExist('Macro "%s" not defined' % macro_name)

    def set(self, macro_name, regex):
        self.macros[macro_name] = regex

class DefaultMacroRegistry(MacroRegistry):
    global_macros = {}

    def __init__(self):
        super(DefaultMacroRegistry, self).__init__({
            # todo: make regexes more restrictive
            # (ie: 'm' should only match months 1-12. currently, it matches 0-99)
            'Y': r'\d{4}', # year, including century
            'y': r'\d{2}', # year, not including century
            'M': r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', # month, abbreviated
            'm': r'\d{1,2}', # month, 1 or 2 digit
            'd': r'\d{1,2}', # day, 1 or 2 digit
            '#': r'\d+', # number, any length
            's': r'[\w-]+', # slug
        })

    @classmethod
    def register(cls, macro, regex):
        cls.global_macros[macro] = regex

    def get(self, macro_name):
        try:
            return super(DefaultMacroRegistry, self).get(macro_name)
        except MacroDoesNotExist:
            try:
                return self.__class__.global_macros[macro_name]
            except KeyError:
                raise MacroDoesNotExist('Macro "%s" not defined' % macro_name)

# This allows "surlex.register_macro" to register to the default registry
register_macro = DefaultMacroRegistry.register

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
        return (macro, self.macro_registry.get(macro))

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
