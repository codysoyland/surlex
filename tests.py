import unittest
from surlex import surlex_to_regex as surl, match, register_macro, parsed_surlex_object, Surlex, MacroRegistry
from surlex import grammer
from surlex.exceptions import MalformedSurlex, MacroDoesNotExist
import re

class TestGrammer(unittest.TestCase):
    def test_parser_simple(self):
        parser = grammer.Parser('test')
        self.assertEqual(parser.get_node_list(), [grammer.TextNode('test')])

    def test_parser_simple1(self):
        self.assertEqual(
            grammer.Parser(r'a\backslash').get_node_list(),
            [grammer.TextNode('abackslash')],
        )

    def test_parser_wildcard_simple(self):
        parser = grammer.Parser('*')
        self.assertEqual(parser.get_node_list(), [grammer.WildcardNode()])

    def test_parser_wildcard1(self):
        self.assertEqual(
            grammer.Parser('text*').get_node_list(),
            [grammer.TextNode('text'), grammer.WildcardNode()],
        )

    def test_parser_wildcard2(self):
        self.assertEqual(
            grammer.Parser('*text').get_node_list(),
            [grammer.WildcardNode(), grammer.TextNode('text')],
        )

    def test_parser_wildcard3(self):
        self.assertEqual(
            grammer.Parser('*text*').get_node_list(),
            [grammer.WildcardNode(), grammer.TextNode('text'), grammer.WildcardNode()],
        )

    def test_optional1(self):
        self.assertEqual(
            grammer.Parser('required(optional)').get_node_list(),
            [grammer.TextNode('required'), grammer.OptionalNode([grammer.TextNode('optional')])],
        )

    def test_optional2(self):
        self.assertEqual(
            grammer.Parser('(optional)required').get_node_list(),
            [grammer.OptionalNode([grammer.TextNode('optional')]), grammer.TextNode('required')],
        )

    def test_optional_empty(self):
        self.assertEqual(
            grammer.Parser('()').get_node_list(),
            [grammer.OptionalNode([])],
        )

    def test_optional_multiple(self):
        self.assertEqual(
            grammer.Parser('()()').get_node_list(),
            [grammer.OptionalNode([]), grammer.OptionalNode([])],
        )

    def test_optional_nested(self):
        self.assertEqual(
            grammer.Parser('((text))').get_node_list(),
            [grammer.OptionalNode([grammer.OptionalNode([grammer.TextNode('text')])])],
        )

    def test_tag(self):
        self.assertEqual(
            grammer.Parser('<test>').get_node_list(),
            [grammer.TagNode('test')]
        )

    def test_regex_tag(self):
        self.assertEqual(
            grammer.Parser('<test=.*>').get_node_list(),
            [grammer.RegexTagNode('test', '.*')]
        )

    def test_macro_tag(self):
        self.assertEqual(
            grammer.Parser('<test:m>').get_node_list(),
            [grammer.MacroTagNode('test', 'm')]
        )

    def test_unnamed_regex(self):
        self.assertEqual(
            grammer.Parser('<=.*>').get_node_list(),
            [grammer.RegexTagNode('', '.*')]
        )

    def test_unnamed_macro(self):
        self.assertEqual(
            grammer.Parser('<:m>').get_node_list(),
            [grammer.MacroTagNode('', 'm')]
        )

    def test_complex(self):
        self.assertEqual(
            grammer.Parser('/articles/<id=\d{5}>/<year:Y>/(<slug>/)').get_node_list(),
            [
                grammer.TextNode('/articles/'),
                grammer.RegexTagNode('id', r'\d{5}'),
                grammer.TextNode('/'),
                grammer.MacroTagNode('year', 'Y'),
                grammer.TextNode('/'),
                grammer.OptionalNode([
                    grammer.TagNode('slug'),
                    grammer.TextNode('/'),
                ]),
            ]
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
