.. surlex documentation master file, created by
   sphinx-quickstart on Sun Nov 15 09:07:51 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================
Surlex Documentation
====================

Welcome to the surlex documentation.

Surlex is a pattern-matching domain specific language useful for capturing
structured data using regular expressions and pre-defined macros. It can be
described as a language embracing a subset of regex features, but designed
for syntactic clarity.


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
string just like a simple search. This means that the surlex ``Cody``
will match the input string ``I am Cody.``


Specialized Metacharacters
==========================
Certain characters have special meaning in a surlex expression.

Caret (``^``)
-------------
    A caret at the beginning of the surlex expression makes the surlex
    only match the beginning of the input string. This means that
    ``^Cody`` will match ``Cody wrote surlex.`` but not ``His name
    is Cody.``

Dollar Sign (``$``)
-------------------
    A dollar sign at the end of the surlex expression makes the surlex
    only match the end of the input string. This means that ``Cody.$``
    will match ``Surlex was written by Cody.`` but ``Cody was his
    name``.

Parentheses (``(`` and ``)``)
-----------------------------
    By wrapping a section of a surlex expression in parentheses,
    you are marking a section of the pattern as `optional`, so
    it is not required to match. It is equivalent to wrapping a regex
    in ``()?``.

Angle Brackets (``<`` and ``>``)
--------------------------------
    A pair of angle brackets containing some text is called a `surlex
    tag` and is handled specially. Such tags are the main feature
    of surlex.

Surlex Tags
===========
Surlex tags are are special pattern-matching objects that fall into three
categories:

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

        ``My house is in zip code <zipcode:[0-9]{5}>.``

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
