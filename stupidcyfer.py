#!/usr/bin/python3

# Stupid Cyfer
#
# Extremely simplistic cipher tool
# to minimally obfuscate text files
# to evade basic keyword censorship
# also preserves whitespacing to allow
# simple diffs for source control 
# NOT INTENDED for sensitive or private data
#
# This is free and unencumbered software
# released into the public domain
# under the unlicense. For more information,
# please refer to <http://unlicense.org>

import argparse, sys;
from functools import partial;

alphasubkey = 'stupidcyferzwonxabghjklmqv';

argparser = argparse.ArgumentParser();
argparser.add_argument("inputfile");
argparser.add_argument("-o", "--outfile", dest="outfile", default=None,
                       help="destination filename to write to");
argparser.add_argument("-p", "--stdout", dest="stdout", action='store_true', default=None,
                       help="print output to stdout");
argparser.add_argument("-e", "--encipher", dest="encipher", action='store_true', default=None,
                       help="encipher mode");
argparser.add_argument("-d", "--decipher", dest="decipher", action='store_true', default=None,
                       help="decipher mode");
argparser.add_argument("-y", "--overwrite", dest="overwrite", action='store_true', default=None,
                       help="overwrite outfile if it exists");
argparser.add_argument("-n", dest="noheader", action='store_true', default=None,
                       help="no interpretter line");

args = argparser.parse_args();


# very simply shift and sub the string
# rotates or flips some ranges, substitutes alphas
# used for both encipher and decipher
def shuffler(alphasubkey, uppersubkey, unicodeoffset, string):
    ret = '';
    for c in string:
        # reverse numbers
        if(c >= '0' and c <= '9'):
            ret += str(9 - int(c));
        # sub uppers
        elif(c >= 'A' and c <= 'Z'):
            ret += uppersubkey[ord(c) - ord('A')];
        # sub lowers
        elif(c >= 'a' and c <= 'z'):
            ret += alphasubkey[ord(c) - ord('a')];
        # shift unicode in general
        elif(ord(c) > 0xFF):
            ret += chr(ord(c) + unicodeoffset);
        else:
            ret += c;
    return ret;

#-----------
# main begin

# set a default fileout? and mode?
if(not args.outfile and not args.stdout):
    if(args.inputfile[-4:] == '.scy'):
        args.decipher = True;
        args.outfile = args.inputfile[:-4];
    else:
        args.encipher = True;
        args.outfile = args.inputfile + ".scy";

# open output file (or use stdout)
if(args.outfile):
    try:
        outf = open(args.outfile, 'w' if args.overwrite else 'x');
    except FileExistsError as e:
        print("File %s already exists, use -y to overwrite?" % args.outfile);
        sys.exit(1);
else:
    outf = sys.stdout;

# open input file!
contents = open(args.inputfile, 'r').readlines();

# deterine if it has the interpretter specified
if(len(contents) and len(contents[0]) > 2 and '#!' == contents[0][:2] and 'stupidcyfer' in contents[0]):
    args.decipher = True;
    contents = contents[1:];

# create the inverse key and upper keys (reversed)
uppersubkey = alphasubkey.upper()[::-1];
inversekey = ''.join([chr(ord('a') + alphasubkey.index(chr(ord('a') + l))) for l in range(26)]);
upperinversesubkey = ''.join([chr(ord('A') + uppersubkey.index(chr(ord('A') + l))) for l in range(26)]);

# set the mode
if(args.decipher):
    handler = partial(shuffler, inversekey, upperinversesubkey, -10);
else:
    handler = partial(shuffler, alphasubkey, uppersubkey, 10);
    if(not args.noheader):
        print('#!/usr/bin/env stupidcyfer.py', file=outf);

# finally the main loop, go through line by line and handle them
for line in contents:
    print(handler(line), end='', flush=True, file=outf);

