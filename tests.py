import unittest
from surlex import surlex_to_regex as surl, match, register_macro, parsed_surlex_object, Surlex, MacroRegistry
from surlex import grammar
from surlex.exceptions import MalformedSurlex, MacroDoesNotExist
import re

class TestGrammer(unittest.TestCase):
    def test_parser_simple(self):
        parser = grammar.Parser('test')
        self.assertEqual(parser.get_node_list(), [grammar.TextNode('test')])

    def test_parser_simple1(self):
        self.assertEqual(
            grammar.Parser(r'a\backslash').get_node_list(),
            [grammar.TextNode('abackslash')],
        )

    def test_parser_wildcard_simple(self):
        parser = grammar.Parser('*')
        self.assertEqual(parser.get_node_list(), [grammar.WildcardNode()])

    def test_parser_wildcard1(self):
        self.assertEqual(
            grammar.Parser('text*').get_node_list(),
            [grammar.TextNode('text'), grammar.WildcardNode()],
        )

    def test_parser_wildcard2(self):
        self.assertEqual(
            grammar.Parser('*text').get_node_list(),
            [grammar.WildcardNode(), grammar.TextNode('text')],
        )

    def test_parser_wildcard3(self):
        self.assertEqual(
            grammar.Parser('*text*').get_node_list(),
            [grammar.WildcardNode(), grammar.TextNode('text'), grammar.WildcardNode()],
        )

    def test_optional1(self):
        self.assertEqual(
            grammar.Parser('required(optional)').get_node_list(),
            [grammar.TextNode('required'), grammar.OptionalNode([grammar.TextNode('optional')])],
        )

    def test_optional2(self):
        self.assertEqual(
            grammar.Parser('(optional)required').get_node_list(),
            [grammar.OptionalNode([grammar.TextNode('optional')]), grammar.TextNode('required')],
        )

    def test_optional_empty(self):
        self.assertEqual(
            grammar.Parser('()').get_node_list(),
            [grammar.OptionalNode([])],
        )

    def test_optional_multiple(self):
        self.assertEqual(
            grammar.Parser('()()').get_node_list(),
            [grammar.OptionalNode([]), grammar.OptionalNode([])],
        )

    def test_optional_nested(self):
        self.assertEqual(
            grammar.Parser('((text))').get_node_list(),
            [grammar.OptionalNode([grammar.OptionalNode([grammar.TextNode('text')])])],
        )

    def test_tag(self):
        self.assertEqual(
            grammar.Parser('<test>').get_node_list(),
            [grammar.TagNode('test')]
        )

    def test_regex_tag(self):
        self.assertEqual(
            grammar.Parser('<test=.*>').get_node_list(),
            [grammar.RegexTagNode('test', '.*')]
        )

    def test_macro_tag(self):
        self.assertEqual(
            grammar.Parser('<test:m>').get_node_list(),
            [grammar.MacroTagNode('test', 'm')]
        )

    def test_unnamed_regex(self):
        self.assertEqual(
            grammar.Parser('<=.*>').get_node_list(),
            [grammar.RegexTagNode('', '.*')]
        )

    def test_unnamed_macro(self):
        self.assertEqual(
            grammar.Parser('<:m>').get_node_list(),
            [grammar.MacroTagNode('', 'm')]
        )

    def test_complex(self):
        self.assertEqual(
            grammar.Parser('/articles/<id=\d{5}>/<year:Y>/(<slug>/)').get_node_list(),
            [
                grammar.TextNode('/articles/'),
                grammar.RegexTagNode('id', r'\d{5}'),
                grammar.TextNode('/'),
                grammar.MacroTagNode('year', 'Y'),
                grammar.TextNode('/'),
                grammar.OptionalNode([
                    grammar.TagNode('slug'),
                    grammar.TextNode('/'),
                ]),
            ]
        )

class TestRegexScribe(unittest.TestCase):
    def test_basic(self):
        node_list = [grammar.TextNode('test')]
        self.assertEqual(grammar.RegexScribe(node_list).translate(), 'test')

    def test_optional(self):
        node_list = [
            grammar.TextNode('required'),
            grammar.OptionalNode([
               grammar.TextNode('optional'),
            ]),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            'required(optional)?'
        )

    def test_tag(self):
        node_list = [
            grammar.TagNode('simple'),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            '(?P<simple>.+)',
        )

    def test_regex_tag(self):
        node_list = [
            grammar.RegexTagNode('simple', '[0-9]{2}'),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            '(?P<simple>[0-9]{2})',
        )

    def test_uncaptured_regex_tag(self):
        node_list = [
            grammar.RegexTagNode('', '[0-9]{2}'),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            '[0-9]{2}',
        )

    def test_macro_tag(self):
        node_list = [
            grammar.MacroTagNode('year', 'Y'),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            r'(?P<year>\d{4})',
        )

    def test_uncaptured_macro_tag(self):
        node_list = [
            grammar.MacroTagNode('', 'Y'),
        ]
        self.assertEqual(
            grammar.RegexScribe(node_list).translate(),
            r'\d{4}',
        )

class TestSurlex(unittest.TestCase):
    def setUp(self):
        # matches are pairs of surl expressions and the regex equivalent
        self.matches = (
            ('/<product>/<option>.html', '/(?P<product>.+)/(?P<option>.+)\.html'),
            ('/<product>/<option>.*', '/(?P<product>.+)/(?P<option>.+)\..*'),
            ('/things/edit/<slug>', '/things/edit/(?P<slug>.+)'),
            ('/real/regex/<=.*$>', '/real/regex/.*$'),
            ('/(checkout/)login', '/(checkout/)?login'),
        )

    def test_matches(self):
        for surlex, regex in self.matches:
            self.assertEqual(surl(surlex), regex)

    def test_basic_capture1(self):
        surlex = '/<var>/'
        regex = '/(?P<var>.+)/'
        self.assertEqual(surl(surlex), regex)

    def test_basic_capture2(self):
        surlex = '/<product>/<option>.html'
        regex = '/(?P<product>.+)/(?P<option>.+)\.html'
        self.assertEqual(surl(surlex), regex)

    def test_macro(self):
        surlex = '/year/<:Y>.html'
        regex = '/year/\d{4}\.html'
        self.assertEqual(surl(surlex), regex)

    def test_macro_capture(self):
        surlex = '/blog/<year:Y>.html'
        regex = '/blog/(?P<year>\d{4})\.html'
        self.assertEqual(surl(surlex), regex)

    def test_custom_macro(self):
        register_macro('B', 'bar')
        surlex = '/foo/<:B>/'
        regex = '/foo/bar/'
        self.assertEqual(surl(surlex), regex)

    def test_custom_macro2(self):
        registry = MacroRegistry({'int': r'[0-9]'})
        surlex = Surlex('/<foo:int>/', registry)
        self.assertEqual(surlex.translate(), '/(?P<foo>[0-9])/')

    def test_regex_capture(self):
        surlex = '/<var=[0-9]*>/'
        regex = '/(?P<var>[0-9]*)/'
        self.assertEqual(surl(surlex), regex)

    def test_optional(self):
        surlex = '/things/(<slug>/)'
        regex = '/things/((?P<slug>.+)/)?'
        self.assertEqual(surl(surlex), regex)

    def test_wildcard(self):
        surlex = '/foo/*.html'
        regex = '/foo/.*\.html'
        self.assertEqual(surl(surlex), regex)

    def test_regex(self):
        surlex = '/anything/<=.*$>'
        regex = '/anything/.*$'
        self.assertEqual(surl(surlex), regex)

    def test_regex2(self):
        surlex = r'/<=\d{5}$>'
        regex = r'/\d{5}$'
        self.assertEqual(surl(surlex), regex)

    def test_regex3(self):
        surlex = '<=\>>'
        regex = '>'
        self.assertEqual(surl(surlex), regex)

    def test_parse_fail(self):
        surlex = '<asdf'
        self.assertRaises(MalformedSurlex, surl, surlex)

    def test_macro_lookup_fail(self):
        self.assertRaises(MacroDoesNotExist, surl, '<year:UNKNOWN>')

    def test_groupmacros(self):
        known_macro = parsed_surlex_object('<year:Y>')
        unnamed_macro = parsed_surlex_object('<:Y>')
        self.assertEqual(known_macro.groupmacros['year'], 'Y')
        self.assertEqual(unnamed_macro.groupmacros[''], 'Y')

    def test_match(self):
        surlex = '/articles/<year>/<slug>/'
        subject = '/articles/2008/this-article/'
        m = match(surlex, subject)
        self.assertEqual(m['year'], '2008')
        self.assertEqual(m['slug'], 'this-article')

if __name__ == '__main__':
    unittest.main()
