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
    parser.add_argument('--tcpport',
                        dest='tcp_port',
                        help='Listening tcp port (Server only)',
                        type=int,
                        default="1234")
    parser.add_argument('--udpport',
                        dest='udp_port',
                        help='Listening udp port (Server or Client)',
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
        main_loop(args.tcp_port, args.udp_port, rooms)
    else:
        app = QApplication(sys.argv)

        window = MainWindow(args.udp_port)
        window.show()

        sys.exit(app.exec_())
