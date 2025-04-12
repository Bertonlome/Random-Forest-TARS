import time
import numpy as np
import csv
import math
import classifier
import sys
import ingescape as igs


# Constants
start_lat = 43.4685335227
start_lon = -1.5103003026
runway_heading = 269.4  # Heading of the runway in degrees (West)

#inputs
lat = None
long = None
yokeRoll = None
yokePitch = None
yokeYaw = None
pitch = None
airspeed = None
throttle = None
verticalSpeed = None
altitude = None
heading = None
flaps = None
gear = None
#outputs
inference = None


#inputs
def input_callback(iop_type, name, value_type, value, my_data):
    global lat, long, yokeRoll, yokePitch, yokeYaw, pitch, airspeed, throttle, verticalSpeed, altitude, heading, flaps, gear
    if name == "lat":
        lat = value
    elif name == "long":
        long = value
    elif name == "yokeRoll":
        yokeRoll = value
    elif name == "yokePitch":
        yokePitch = value
    elif name == "yokeYaw":
        yokeYaw = value
    elif name == "pitch":
        pitch = value
    elif name == "airspeed":
        airspeed = value
    elif name == "throttle":
        throttle = value
    elif name == "verticalSpeed":
        verticalSpeed = value
    elif name == "altitude":
        altitude = value
    elif name == "heading":
        heading = value
    elif name == "flaps":
        flaps = value
    elif name == "gear":
        gear = value

refresh_rate = 0.01
port = 5670
agent_name = "Control_Inference"
device = "wlo1"
verbose = False
is_interrupted = False

igs.agent_set_name(agent_name)
igs.definition_set_version("1.0")
igs.log_set_console(True)
igs.log_set_file(True, None)
igs.set_command_line(sys.executable + " " + " ".join(sys.argv))


igs.input_create("lat", igs.DOUBLE_T, None)
igs.input_create("long", igs.DOUBLE_T, None)
igs.input_create("yokeRoll", igs.DOUBLE_T, None)
igs.input_create("yokePitch", igs.DOUBLE_T, None)
igs.input_create("yokeYaw", igs.DOUBLE_T, None)
igs.input_create("pitch", igs.DOUBLE_T, None)
igs.input_create("airspeed", igs.DOUBLE_T, None)
igs.input_create("throttle", igs.DOUBLE_T, None)
igs.input_create("verticalSpeed", igs.DOUBLE_T, None)
igs.input_create("altitude", igs.DOUBLE_T, None)
igs.input_create("heading", igs.DOUBLE_T, None)
igs.input_create("flaps", igs.DOUBLE_T, None)
igs.input_create("gear", igs.DOUBLE_T, None)

igs.output_create("inference", igs.BOOL_T, None)

igs.observe_input("lat", input_callback, None)
igs.observe_input("long", input_callback, None)
igs.observe_input("yokeRoll", input_callback, None)
igs.observe_input("yokePitch", input_callback, None)
igs.observe_input("yokeYaw", input_callback, None)
igs.observe_input("pitch", input_callback, None)
igs.observe_input("airspeed", input_callback, None)
igs.observe_input("throttle", input_callback, None)
igs.observe_input("verticalSpeed", input_callback, None)
igs.observe_input("altitude", input_callback, None)
igs.observe_input("heading", input_callback, None)
igs.observe_input("flaps", input_callback, None)
igs.observe_input("gear", input_callback, None)

igs.start_with_device(device, port)

# Haversine formula to compute the distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # distance in km

# Function to calculate the lateral deviation from the centerline
def compute_centerline_deviation(start_lat, start_lon, runway_heading, plane_lat, plane_lon):
    # Convert runway heading from degrees to radians
    heading_rad = math.radians(runway_heading)
    
    # Compute the initial distance between the centerline point and the plane (great-circle distance)
    distance_from_centerline = haversine(start_lat, start_lon, plane_lat, plane_lon)
    
    # Calculate the angle between the runway heading and the vector from centerline to aircraft
    delta_lat = plane_lat - start_lat
    delta_lon = plane_lon - start_lon
    
    # Use arctangent to get the bearing of the aircraft from the centerline
    angle_to_plane = math.atan2(delta_lon, delta_lat)
    
    # Calculate the deviation using the perpendicular component of the distance
    deviation = distance_from_centerline * math.sin(angle_to_plane - heading_rad)
    
    return deviation

def compute_rms(values):
    """Compute RMS of a list of values."""
    if len(values) == 0:
        return 0
    return math.sqrt(sum(x**2 for x in values) / len(values))


def log_data(features):
    with open("takeoff_data.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(features)

def reaction_time_to_vrotate():
    global pitch
    if pitch > 1:  # Aircraft begins to rotate
        return time.time()  # Calculate reaction time in seconds
    else:
        return 0

def reaction_time_to_retract_flaps():
    global flaps
    if flaps < 0.5:
        # Log the time at which speed crosses 120 knots
        return time.time()
    else:
        return 0

def reaction_time_to_retract_gear():
    global gear
    gear_handle_status = gear
    if gear_handle_status == 0:  # Positive rate of climb
        # Log the time for gear retraction event
        return time.time()
    else:
        return 0

# Example of how to collect and log features:
def main():
    global lat, long, yokeRoll, yokePitch, yokeYaw, pitch, airspeed, throttle, verticalSpeed, altitude, inference, heading

    # Histories for inputs and deviation
    input_history = {"aileron": [], "elevator": [], "rudder": []}
    deviation_history = []
    pitch_history = []
    pitch_rms = -1

    end = False
    speed_just_done = -1
    final_rotation_reaction_time = -1
    final_retract_gear_reaction_time = -1
    final_retract_flaps_reaction_time = -1
    pitch = -1
    calculate_pitch_flag = False
    calculate_pitch_done = False
    retract_flaps_flag = False
    retract_flaps_done = False
    retract_gear_flag = False
    retract_gear_done = False
    startFlag = False
    rotateFlag = False
    rotation_done_flag = False
    failure_flag = False

    print("INITIALIZATION...")
    while startFlag == False:
        throttle_position = throttle
        if throttle_position == 1:
            startFlag = True
            print("START!")
        time.sleep(0.01)

    start_lat = lat
    start_lon = long
    runway_heading = heading
    #startTime_for_perf = 0
    #startTime = time.time()
    while True and end == False:
        time.sleep(0.01)

        speed = int(airspeed - 5)

        deviation = compute_centerline_deviation(start_lat, start_lon, runway_heading, lat, long)

        input_history["aileron"].append(yokeRoll)
        input_history["elevator"].append(yokePitch)
        input_history["rudder"].append(yokeYaw)
        deviation_history.append(deviation)


        if speed >= 90 and rotateFlag == False:
                print("Time to rotate!")
                v_rotate_time = time.time()
                rotateFlag = True

        if rotateFlag == True and rotation_done_flag == False:
            rotation_reaction_time = reaction_time_to_vrotate()
            if rotation_reaction_time != 0:
                rotation_done_flag = True
                final_rotation_reaction_time = rotation_reaction_time - v_rotate_time
                print(f"rotation reaction time = {final_rotation_reaction_time}")
        
        if speed >= 120 and retract_flaps_flag == False:
            print("Time to retract some flaps!")
            v_two_time = time.time()
            retract_flaps_flag = True

        if retract_flaps_flag == True and retract_flaps_done == False:
            retract_flaps_reaction_time = reaction_time_to_retract_flaps()
            if retract_flaps_reaction_time != 0:
                retract_flaps_done = True
                final_retract_flaps_reaction_time = retract_flaps_reaction_time - v_two_time
                print(f"flaps retractation reaction time = {final_retract_flaps_reaction_time}")

        
        if verticalSpeed >= 300 and retract_gear_flag == False:
            print("Time to remove the shoes!")
            positive_rate_time = time.time()
            retract_gear_flag = True
            calculate_pitch_flag = True

        if retract_gear_flag == True and retract_gear_done == False:
            retract_gear_reaction_time = reaction_time_to_retract_gear()
            if retract_gear_reaction_time != 0:
                retract_gear_done = True
                final_retract_gear_reaction_time = retract_gear_reaction_time - positive_rate_time
                print(f"Gear retractation reaction time = {final_retract_gear_reaction_time}")

        if calculate_pitch_flag == True:
            pitch_history.append(pitch - 10) #10 = target

        if speed % 10 == 0 and speed != speed_just_done:
            
            aileron_rms = compute_rms(input_history["aileron"])
            elevator_rms = compute_rms(input_history["elevator"])
            rudder_rms = compute_rms(input_history["rudder"])
            deviation_rms = compute_rms(deviation_history)
            pitch_rms = compute_rms(pitch_history)
            if pitch_rms == 0:
                pitch_rms = -1
            
            # Collect all features
            features = [speed, aileron_rms, elevator_rms, rudder_rms, deviation_rms, pitch_rms, final_retract_flaps_reaction_time, final_retract_gear_reaction_time, final_rotation_reaction_time]
            myClass = classifier.classify_new_data(features)
            if myClass == 0: 
                myClass_string = "NOVICE"
                igs.output_set_bool("inference", False)
            else: 
                myClass_string = "EXPERT"
                igs.output_set_bool("inference", True)

            print(f"Classification: {myClass_string}")
            log_data(features)

            input_history = {"aileron": [], "elevator": [], "rudder": []}
            deviation_history = []
            pitch_history = []
            #loopTime = time.time() - startTime_for_perf
            #startTime_for_perf = time.time()
            speed_just_done = speed

        if altitude > 1500:
            end = True

main()
igs.stop()

