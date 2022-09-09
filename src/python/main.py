# Initalization code

import depthai

def main():
    print("Test")

    for device in depthai.Device.getAllAvailableDevices():
        print(f"{device.getMxId()} {device.state}")
        device

if __name__ == "__main__":
    main()
