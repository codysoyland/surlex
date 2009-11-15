try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import re
from exceptions import MalformedSurlex
from macros import MacroRegistry, DefaultMacroRegistry

class Node(object):
    pass

class TextNode(Node):
    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.token == other.token)

    def __repr__(self):
        return '<TextNode "%s">' % self.token

class WildcardNode(Node):
    def __init__(self):
        pass
    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __repr__(self):
        return '<WildcardNode>'

class BlockNode(Node):
    def __init__(self, node_list):
        self.node_list = node_list

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.node_list == other.node_list)

class OptionalNode(BlockNode):
    def __repr__(self):
        return '<OptionalNode: %s>' % self.node_list

class TagNode(Node):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name)

    def __repr__(self):
        return '<TagNode: %s>' % self.name

class RegexTagNode(Node):
    def __init__(self, name, regex):
        self.name = name
        self.regex = regex

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.regex == other.regex)

    def __repr__(self):
        return '<RegexTagNode %s: %s' % (self.name, self.regex)

class MacroTagNode(Node):
    def __init__(self, name, macro):
        self.name = name
        self.macro = macro

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.macro == other.macro)

    def __repr__(self):
        return '<MacroTagNode %s: %s' % (self.name, self.macro)

class Parser(object):
    def __init__(self, surlex):
        self.surlex = surlex
        #self.chars = list(surlex) # make this generator
        self.chars = (char for char in surlex)

    def get_node_list(self):
        return list(self.parse(self.chars))
        #return [TextNode('test')]

    def read_until(self, chars, char):
        try:
            next_char = chars.next()
        except StopIteration:
            raise MalformedSurlex('Malformed surlex. Expected %s.' % char)
        if next_char == char:
            return ''
        if next_char == '\\':
            # only escape what we are looking for
            next = chars.next()
            if next == char:
                return next + self.read_until(chars, char)
            else:
                return '\\' + next + self.read_until(chars, char)
        else:
            return next_char + self.read_until(chars, char)

    def parse(self, chars):
        token = ''
        for char in chars:
            if char == '\\':
                # escape with backslash
                token += chars.next()
            elif char == '<':
                if token:
                    yield TextNode(token)
                token = ''
                tag_content = self.read_until(chars, '>')
                name = ''
                regex = None
                macro = None
                for char in tag_content:
                    if char == '=':
                        name, regex = tag_content.split('=', 1)
                        break
                    if char == ':':
                        name, macro = tag_content.split(':', 1)
                        break
                if regex:
                    yield RegexTagNode(name, regex)
                elif macro:
                    yield MacroTagNode(name, macro)
                else:
                    yield TagNode(tag_content)
            elif char == '*':
                # wildcard
                if token:
                    yield TextNode(token)
                token = ''
                yield WildcardNode()
            elif char == '(':
                if token:
                    yield TextNode(token)
                token = ''
                yield OptionalNode(list(self.parse(chars)))
            elif char == ')':
                # end of node list, stop parsing
                break
            else:
                # literal output
                token += char
        if token:
            yield TextNode(token)

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

