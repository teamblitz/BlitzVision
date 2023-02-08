import json
import socket
from threading import Thread
from time import sleep

from core.time_manager import TimeManager


class RobotCommunicator(Thread):
    response_message = str.encode(json.dumps({
        "device": "nano",
        "type": "response",
        "message": "timesync message received",
    }))
    UDP_IP = "127.0.0.1"
    UDP_IP_OUT = "10.20.83.2"
    UDP_PORT = 5810

    def __init__(self):
        super().__init__()
        self.inSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.inSock.bind((self.UDP_IP, self.UDP_PORT))
        self.outSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        while True:
            data, addr = self.inSock.recvfrom(1024)
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                print(f"Error decoding packet {data}")
                continue

            if json_data.get("type", "unknown") == "timesync" and json_data.get("device", "unknown") == "roborio":
                try:
                    robot_time = int(json_data.get("message", "-1"))
                    if robot_time != -1:
                        TimeManager.set_robot_time(robot_time)
                        self.outSock.sendto(self.response_message, (self.UDP_IP_OUT, self.UDP_PORT))
                    print("Robot time -1")
                except ValueError:
                    print("Timestamp from roborio is not a number!")
            else:
                print(f"Unknown packet {data}")
