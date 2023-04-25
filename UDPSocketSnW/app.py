import argparse
import ipaddress
from client import Client

COMMON_USE_PORTS = [20, 21, 22, 25, 53, 80, 123, 179, 443, 511, 587, 3389]
HELP_STRING = "" \
              "usage : download [ - h ] [ -v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ]" \
                "\n"\
              "< command description > " \
              "\n" \
              "optional arguments :"\
              "\n"\
              "-h , --help       show this help message and exit" \
                "\n"\
              "-v , --verbose    increase output verbosity" \
                "\n"\
              "-q , --quiet      decrease output verbosity" \
                "\n"\
              "-H , --host       server IP address" \
                "\n"\
              "-p , --port       server port" \
                "\n"\
              "-d , --dst        destination file path" \
                "\n"\
              "-n , --name       file name"


class App:

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)

        self.parser.add_argument("clientAction", help="client action")
        self.parser.add_argument("-h", "--help",  help="show help", action="store_true")
        self.parser.add_argument("-H", "--host", type=str, help="server IP address", nargs=1, metavar="ADDR")
        self.parser.add_argument("-p", "--port", type=str, help="server port", nargs=1, metavar="PORT")
        self.parser.add_argument("-n", "--name", type=str, help="file name", nargs=1, metavar="FILENAME")
        self.parser.add_argument("-d", "--dst", type=str, help="destination file path", nargs=1, metavar="PATH")
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        group.add_argument("-q", "--quiet", help="decrease output verbosity", action="store_false")

        args = self.parser.parse_args()
        self.action = args.clientAction
        self.help_mode = args.help
        self.host = args.host
        self.port = args.port
        self.name = args.name
        self.destination = args.dst
        self.quiet = args.quiet
        self.verbose = args.verbose

    def print_arguments(self):
        print(f"Action: {self.action}")
        print(f"Help: {self.help_mode}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Name: {self.name}")
        print(f"Destination: {self.destination}")
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

        if self.action != "download" and self.action != "upload":
            print("invalid action, please use 'upload' or 'download' command")
            return 0

        if self.help_mode:
            print(HELP_STRING)
            return 0

        if self.port is None or int(self.port[0]) in COMMON_USE_PORTS or int(self.port[0]) <= 1023:
            print("Unaveliable server port, using default port: 2001")
            self.port = ['2001']

        if self.host is None or not self.is_valid_addres(self.host[0]):
            print("Valid server address required, restart application and select an available address")
            return 0

        # aca habria que mandar la accion al cliente y sabemos q es valida, pero npi como hacer eso correctamente
        Client(self.host[0], self.port[0], self.action)

App().run()
