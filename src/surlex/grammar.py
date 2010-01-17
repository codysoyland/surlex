import re
from surlex.exceptions import MalformedSurlex
from surlex.macros import MacroRegistry, DefaultMacroRegistry

# Define the next function for python 2 and 3 compatibility
try:
    if next:
        pass
except NameError:
    def next(iterable):
        return iterable.next()

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

class RegexTagNode(TagNode):
    def __init__(self, name, regex):
        self.name = name
        self.regex = regex

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.regex == other.regex)

    def __repr__(self):
        return '<RegexTagNode %s: %s>' % (self.name, self.regex)

class MacroTagNode(TagNode):
    def __init__(self, name, macro):
        self.name = name
        self.macro = macro

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.macro == other.macro)

    def __repr__(self):
        return '<MacroTagNode %s: %s>' % (self.name, self.macro)

class Parser(object):
    def __init__(self, surlex):
        self.surlex = surlex
        self.chars = iter(surlex)

    def get_node_list(self):
        return list(self.parse(self.chars))

    def read_until(self, chars, char):
        try:
            next_char = next(chars)
        except StopIteration:
            raise MalformedSurlex('Malformed surlex. Expected %s.' % char)
        if next_char == char:
            return ''
        if next_char == '\\':
            # only escape what we are looking for
            escaped_char = next(chars)
            if escaped_char == char:
                return escaped_char + self.read_until(chars, char)
            else:
                return '\\' + escaped_char + self.read_until(chars, char)
        else:
            return next_char + self.read_until(chars, char)

    def parse(self, chars):
        token = ''
        for char in chars:
            if char in '<*(':
                if token:
                    yield TextNode(token)
                token = ''
            if char == '\\':
                # escape with backslash
                token += next(chars)
            elif char == '<':
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
                yield WildcardNode()
            elif char == '(':
                yield OptionalNode(list(self.parse(chars)))
            elif char == ')':
                # end of node list, stop parsing
                break
            else:
                # literal output
                token += char
        if token:
            yield TextNode(token)

class RegexScribe(object):
    def __init__(self, node_list, macro_registry=DefaultMacroRegistry()):
        self.node_list = node_list
        self.macro_registry = macro_registry

    def translate(self):
        output = ''
        for node in self.node_list:
            if isinstance(node, TextNode):
                output += node.token.replace('.', '\.')
            elif isinstance(node, WildcardNode):
                output += '.*'
            elif isinstance(node, OptionalNode):
                output += '(' + RegexScribe(node.node_list).translate() + ')?'
            elif isinstance(node, TagNode):
                if isinstance(node, MacroTagNode):
                    regex = self.macro_registry.get(node.macro)
                elif isinstance(node, RegexTagNode):
                    regex = node.regex
                else:
                    regex = '.+'
                if node.name:
                    output += '(?P<%s>%s)' % (node.name, regex)
                else:
                    output += regex
        return output

def get_all_nodes(node_list):
    for node in node_list:
        if isinstance(node, BlockNode):
            for node in get_all_nodes(node.node_list):
                yield node
        else:
            yield node
