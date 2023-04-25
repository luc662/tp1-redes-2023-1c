import argparse
import ipaddress
import download
from upload import Upload
from logging import Logger

COMMON_USE_PORTS = [20, 21, 22, 25, 53, 80, 123, 179, 443, 511, 587, 3389]
HELP_STRING = "" \
              "usage : upload [ - h ] [ -v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ]" \
              "\n" \
              " Upload a file in file destination " \
              "\n" \
              "optional arguments :" \
              "\n" \
              "-h , --help       show this help message and exit" \
              "\n" \
              "-v , --verbose    increase output verbosity" \
              "\n" \
              "-q , --quiet      decrease output verbosity" \
              "\n" \
              "-H , --host       server IP address" \
              "\n" \
              "-p , --port       server port" \
              "\n" \
              "-s , --src        Source file path" \
              "\n" \
              "-n , --name       file name"


class AppUpload:

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

        self.parser.add_argument("-h", "--help", help="show help", action="store_true")
        self.parser.add_argument("-H", "--host", type=str, help="server IP address", nargs=1, metavar="ADDR")
        self.parser.add_argument("-p", "--port", type=str, help="server port", nargs=1, metavar="PORT")
        self.parser.add_argument("-n", "--name", type=str, help="file name", nargs=1, metavar="FILENAME")
        paths = self.parser.add_mutually_exclusive_group()
        paths.add_argument("-s", "--src", type=str, help="source file path", nargs=1, metavar="UPLOAD PATH")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        group.add_argument("-q", "--quiet", help="decrease output verbosity", action="store_false")

        args = self.parser.parse_args()
        self.help_mode = args.help
        self.host = args.host
        self.port = args.port
        self.name = args.name
        self.source = args.src

        self.quiet = args.quiet
        self.verbose = args.verbose

    def print_arguments(self):
        #print(f"Action: {self.action}")
        print(f"Help: {self.help_mode}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Name: {self.name}")
        #print(f"Destination: {self.destination}")
        print(f"Source: {self.source}")
        print(f"Quiet: {self.quiet}")
        print(f"Verbose: {self.verbose}")

    def is_valid_addres(self, address) -> bool:
        try:
            ipaddress.IPv4Address(address)
            return True
        except ValueError:
            return False

    def run(self):

        # todo limitar el tamaño del archivo y chequear directorio
        self.print_arguments()

        if self.help_mode:
            print(HELP_STRING)
            return 0
        if self.quiet is not None:
            Logger.disabled = True

        if self.port is None or int(self.port[0]) in COMMON_USE_PORTS or int(self.port[0]) <= 1023:
            print("Unaveliable server port, using default port: 2001")

            return 0

        if self.host is None or not self.is_valid_addres(self.host[0]):
            print("Valid server address required, restart application and select an available address")
            return 0

        if self.name is None:
            print("No file name provided")
            return 0

        if self.source is None:
            print("No Source path provided for upload")
            return 0

        return 0
        #upload.Upload(self.host[0], int(self.port[0]), self.name[0], self.source[0])


AppUpload().run()
