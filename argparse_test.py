import argparse

'''
usage : download [ - h ] [ -v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]
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
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-v', '--verbose', help='increase output verbosity', metavar='\b', type=str, action='store')
group.add_argument('-q', '--quiet', help='decrease output verbosity', metavar='\b', type=str, action='store')
parser.add_argument('-H', '--host', nargs=1, required=False, help='server IP address', metavar='ADDR', type=str, action='store')
parser.add_argument('-p', '--port', nargs=1, required=False, help='server port', metavar='PORT', type=int, action='store')
parser.add_argument('-d', '--dst', nargs=1, required=False, help='destination file path', metavar='FILEPATH', type=str, action='store')
parser.add_argument('-n', '--name', nargs=1, required=False, help='file name', metavar='FILENAME', type=str, action='store')

parser.print_help()