import unittest
from surlex import surlex_to_regex as surl, match, register_macro, parsed_surlex_object
import re

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

    def test_groupmacros(self):
        known_macro = parsed_surlex_object('<year:Y>')
        unnamed_macro = parsed_surlex_object('<:Y>')
        self.assertEqual(known_macro.groupmacros['year'], 'Y')
        self.assertRaises(Exception, parsed_surlex_object, '<year:UNKNOWN>')
        self.assertEqual(unnamed_macro.groupmacros[''], 'Y')

    def test_match(self):
        surlex = '/articles/<year>/<slug>/'
        subject = '/articles/2008/this-article/'
        m = match(surlex, subject)
        self.assertEqual(m['year'], '2008')
        self.assertEqual(m['slug'], 'this-article')
