import argparse

'''
usage : download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]
< command description >
optional arguments :
-h , --help       show this help message and exit
-v , --verbose    increase output verbosity
-q , --quiet      decrease output verbosity
-H , --host       server IP address
-p , --port       server port
-d , --dst        destination file path
-n , --name       file name
'''

parser = argparse.ArgumentParser(prog='download')
parser.add_argument('-v', nargs='?', help='verbose increase output verbosity')
parser.add_argument('-q', nargs='?', help='quiet decrease output verbosity')
parser.add_argument('-H', nargs='?', help='host server IP address')
parser.add_argument('-p', nargs='?', help='port server port')
parser.add_argument('-d', nargs='?', help='dst destination file path')
parser.add_argument('-n', nargs='?', help='name file name')


parser.print_help()