import json
import socket
from threading import Thread
from time import sleep

from time_manager import TimeManager


class RobotCommunicator(Thread):
    UDP_IP = "10.20.83.130"
    UDP_PORT = 5810

    def __init__(self):
        super().__init__()
        self.inSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.inSock.bind((self.UDP_IP, self.UDP_PORT))
        self.setDaemon(True)

    def run(self):
        while True:
            data, addr = self.inSock.recvfrom(1024)
            
            robot_time = -1

            try:
                robot_time = int.from_bytes(data, byteorder='big', signed=True)
            except ValueError:
                print(f"{data} is bad!!!")

            if robot_time != -1:
                TimeManager.set_robot_time(robot_time)

if __name__ == "__main__":
    RobotCommunicator().start()