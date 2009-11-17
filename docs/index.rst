.. surlex documentation master file, created by
   sphinx-quickstart on Sun Nov 15 09:07:51 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
Surlex Documentation
====================

Welcome to the surlex documentation.

Surlex is domain specific language designed for pattern matching and data
capturing using a minimal syntax. It is similar in concept to regex and is,
in fact, a regex generator. It can be described as a language embracing and
simplifying a subset of the features of regular expressions, keeping the
power of regex available, but prioritizing syntactic clarity.

------
Basics
------

Surlex was originally designed for matching URLs. Consider the following surlex
that matches a URL:

::

    /articles/<year:Y>/<slug:s>/(<page:#>/)

This surlex would match the following URL:

::

    /articles/2009/people-like-simplicity/3/

This match would produce the following data dictionary:

::

    {
        'year': '2009',
        'slug': 'people-like-simplicity',
        'page': '3',
    }

The page number is optional, so if it was left off the URL, the surlex would
still match the URL, but only extract the year and slug.

------
Syntax
------

This syntax diagram describes the entirety of surlex syntax:

    .. image:: images/syntax-diagram.gif
       :alt: Surlex syntax diagram

The syntax of surlex is minimalistic and intended to provide the most concise
form possible for the extraction of named patterns.


Like regular expressions, surlex expressions will match a given input based
on two things: normal characters and specialized metacharacters.

Normal Characters
=================
Normal characters such as alphanumeric characters will match the input
string just like a simple search. This means that the surlex ``surlex``
will match the input string ``Maybe surlex can do that.``

Specialized Metacharacters
==========================
Certain characters have special meaning in a surlex expression.

Caret (``^``)
-------------
    A caret at the beginning of the surlex expression makes the surlex
    only match the beginning of the input string. For example, ``^surlex``
    will match ``surlex finds slugs.`` but not ``Slugs will be found by
    surlex``. This is the same behavior that regex provides.

Dollar Sign (``$``)
-------------------
    A dollar sign at the end of a phrase has exactly the opposite effect
    as a caret; it will only match the end of the input string. This means
    that ``Surlex.$`` will match ``I found this thing called Surlex.`` but
    not ``Surlex might have no use case.``.

Asterisk (``*``)
----------------
    An asterisk is a standard wildcard; it will match anything. It is the
    same as regex ``.*``.

Parentheses (``(`` and ``)``)
-----------------------------
    By wrapping a section of a surlex expression in parentheses,
    you are marking a section of the pattern as `optional`, so
    it is not required to match. It is equivalent to wrapping a regex
    in ``(`` and ``)?``.

Angle Brackets (``<`` and ``>``)
--------------------------------
    A pair of angle brackets containing some text is called a `surlex
    tag` and is handled specially. These tags are the most important
    feature of surlex in terms of it's pattern-matching capabilities.

Surlex Tags
===========
Surlex tags are are special pattern-matching objects that fall into three
categories:

    - Simple tags
    - Regex tags
    - Macro tags

Simple tags
-----------
    A simple tag contains a variable name between angle brackets. For
    example, the simple tag ``<name>`` is used the the following surlex:

        ``My name is <name>.``

    This is equivalent to the following regex:

        ``My name is (?P<name>.+)\.``

Regex tags
----------
    A regex tag is the same as a simple tag with the addition of an
    equals sign (``=``) followed by a regex after the tag name. For
    example, the following surlex matches a 5-digit number and assigns
    it to the variable ``zipcode``:

        ``My house is in zip code <zipcode=[0-9]{5}>.``

    This is equivalent to the following regex:

        ``My house is in zip code (?P<zipcode>[0-9]{5})\.``

Macro tags
----------
    A macro tag is the same as a simple tag with the addition of a
    colon (``:``) followed by a regex after the tag name. For example,
    the following surlex matches a 4-digit year and assigns it to the
    variable ``year``:

        ``It is <year:Y>.``

    This is equivalent to the following regex:

        ``It is (?P<year>[0-9]{4}).``

--------
Examples
--------

============================    =========================================   =========================   ===========================================
Surlex                          Regex equivalent                            Matches                     Extracts
============================    =========================================   =========================   ===========================================
``/<product>/<option>.html``    ``/(?P<product>.+)/(?P<option>.+)\.html``   ``/shirt/green.html``       ``{'product': 'shirt', 'option': 'green'}``
``/<product>/<option>.*``       ``/(?P<product>.+)/(?P<option>.+)\..*``     ``/shirt/red.anything``     ``{'product': 'shirt', 'option': 'red'}``
``/things/edit/<slug:s>/``      ``/things/edit/(?P<slug>[\w-]+)/``          ``/things/edit/thing-1/``   ``{'slug': 'thing-1'}``
``/real/regex/<=.*$>``          ``/real/regex/.*$``                         ``/real/regex/anything``    ``{}``
``/blog/(<year:Y>/)``           ``/blog/((?P<year>\d{4})/)?``               ``/blog/2009/``             ``{'year': '2009'}``
============================    =========================================   =========================   ===========================================
