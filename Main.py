import argparse
import sys
from PySide2.QtWidgets import QApplication
from Windows.MainWindow import MainWindow
from Networking.rooms import Rooms
from Networking.server import main_loop

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BP C2')
    parser.add_argument('--server',
                        dest='server',
                        help='Run a server instance',
                        action='store_true')
    parser.add_argument('--serverport',
                        dest='serverport',
                        help='TCP/UDP port to listen on (Server only)',
                        type=int,
                        default="1234")
    parser.add_argument('--clientport',
                        dest='clientport',
                        help='UDP port to listen on (Client only)',
                        type=int,
                        default="8888")
    parser.add_argument('--capacity',
                        dest='room_capacity',
                        help='Max players per room (Server only)',
                        type=int,
                        default="2")

    args = parser.parse_args()
    if args.server:
        rooms = Rooms(args.room_capacity)
        main_loop(args.serverport, args.serverport, rooms)
    else:
        app = QApplication(sys.argv)

        window = MainWindow(args.clientport)
        window.show()

        sys.exit(app.exec_())
