#!/usr/bin/env python
from surlex import Surlex
import sys
from optparse import OptionParser

def main():
    parser = OptionParser()
    parser.set_usage('surlex2regex.py <surlex>')
    if len(sys.argv) == 1:
        argv = ['-h']
    else:
        argv = sys.argv[1:]
    options, args = parser.parse_args(argv)
    print (Surlex(args[0]).translate())

if __name__ == '__main__':
    main()
