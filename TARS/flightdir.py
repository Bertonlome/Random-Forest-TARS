import xpc
import time

def main():
    with xpc.XPlaneConnect() as client:
        print("SET FD")
        fd_dref = "sim/cockpit2/autopilot/flight_director_mode"
        client.sendDREF(fd_dref, 1)
        while True:
            time.sleep(0.01)
            client.sendDREF("sim/cockpit/autopilot/flight_director_pitch", 10) 