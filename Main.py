import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BP C2')
    parser.add_argument('--server',
                        dest='server',
                        help='Run a server instance',
                        action='store_true')
    parser.add_argument('--serverport',
                        dest='serverport',
                        help='TCP/UDP port to listen on for client connections (Server only)',
                        type=int,
                        default="1234")
    parser.add_argument('--clientport',
                        dest='clientport',
                        help='UDP port to listen on for updated from Server (Client only)',
                        type=int,
                        default="8888")
    parser.add_argument('--capacity',
                        dest='room_capacity',
                        help='Max operators per room (Server only)',
                        type=int,
                        default="2")
    parser.add_argument('--hivemind_server',
                        dest='hivemind_server',
                        help='Hivemind Server IP (Server only)',
                        type=str,
                        default=None)
    parser.add_argument('--hivemind_port',
                        dest='hivemind_port',
                        help='Hivemind Port (Server only)',
                        type=int,
                        default=None)
    parser.add_argument('--bp_listen_port',
                        dest='bp_listen_port',
                        help='Port for BP to listen on and respond from (Server only)',
                        type=int,
                        default='53')
    parser.add_argument('--bp_push_port',
                        dest='bp_push_port',
                        help='Port for BP to try and send packets to when pushing (Server only)',
                        type=int,
                        default='53')

    args = parser.parse_args()
    if args.server:
        from Networking.rooms import Rooms
        from Networking.server import main_loop

        rooms = Rooms(args.room_capacity)
        main_loop(args.serverport, args.serverport, rooms, args.bp_listen_port, args.bp_push_port, args.hivemind_server, args.hivemind_port)
    else:
        from PySide2.QtWidgets import QApplication
        from Windows.MainWindow import MainWindow

        app = QApplication(sys.argv)

        window = MainWindow(args.clientport)
        window.show()

        sys.exit(app.exec_())
