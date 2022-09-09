import depthai

#mxid for our device
# 0 is for front, when we get more cameras we can do more
ids: str = [""]
names: str = ["Front"]

def main():
    for i in range(1):
        found, device_info = depthai.Device.getDeviceByMxId(ids[i])

        if found:
            #Start device
        else:
            print(f"{names[i]} Oak-D not ")
