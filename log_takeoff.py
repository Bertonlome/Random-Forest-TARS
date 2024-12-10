import time
import xpc
import numpy as np
import csv
import math
from geopy.distance import geodesic
import classifier
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

def send_birds():
    with xpc.XPlaneConnect() as client:
        # Send the mighty birds
        print("Birds incoming ! :)")
        bird_dref = "sim/operation/failures/rel_bird_strike"
        client.sendDREF(bird_dref, 2)

def get_lat():
    with xpc.XPlaneConnect() as client:
        lat = client.getDREF("sim/flightmodel/position/latitude")[0]
        return lat

def get_long():
    with xpc.XPlaneConnect() as client:
        long = client.getDREF("sim/flightmodel/position/longitude")[0]
        return long

start_lat = 43.4685335227
start_lon = -1.5103003026
runway_heading = 269.4  # Heading of the runway in degrees (West)

def compute_rms(values):
    """Compute RMS of a list of values."""
    if len(values) == 0:
        return 0
    return math.sqrt(sum(x**2 for x in values) / len(values))


def get_control_inputs():
    with xpc.XPlaneConnect() as client:
        aileron = client.getDREF("sim/cockpit2/controls/yoke_roll_ratio")[0]
        elevator = client.getDREF("sim/cockpit2/controls/yoke_pitch_ratio")[0]
        rudder = client.getDREF("sim/cockpit2/controls/yoke_heading_ratio")[0]
        return aileron, elevator, rudder
    
def get_position():
    with xpc.XPlaneConnect() as client:
        local_x = client.getDREF("sim/flightmodel/position/local_x")[0]
        local_y = client.getDREF("sim/flightmodel/position/local_y")[0]
        return local_x, local_y

def get_pitch():
    pitch = get_dref("sim/cockpit2/gauges/indicators/pitch_AHARS_deg_pilot")
    return pitch,

def reaction_time_to_vrotate():
    pitch = get_pitch()[0]
    if pitch > 1:  # Aircraft begins to rotate
        return time.time()  # Calculate reaction time in seconds
    else:
        return 0

def reaction_time_to_retract_flaps():
    with xpc.XPlaneConnect() as client:
        flaps = client.getDREF("sim/cockpit2/controls/flap_ratio")[0]
        if flaps < 0.5:
            # Log the time at which speed crosses 120 knots
            return time.time()
        else:
            return 0

def reaction_time_to_retract_gear():
    with xpc.XPlaneConnect() as client:
        gear_handle_status = client.getDREF("sim/cockpit/switches/gear_handle_status")[0]
        if gear_handle_status == 0:  # Positive rate of climb
            # Log the time for gear retraction event
            return time.time()
        else:
            return 0


def log_data(features):
    with open("takeoff_data.csv", mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(features)

# Example of how to collect and log features:
def main(result_queue, eng_fail_aft_v1):

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
        throttle_position = get_dref("Mustang/cockpit/engine/l_throttle")
        if throttle_position == 1:
            startFlag = True
            print("START!")
        time.sleep(0.01)

    #startTime_for_perf = 0
    #startTime = time.time()
    while True and end == False:
        time.sleep(0.01)

        speed = int(get_dref("sim/cockpit2/gauges/indicators/airspeed_kts_pilot")) - 5

        if eng_fail_aft_v1 == True and speed > 130 and failure_flag == False:
            send_birds()
            failure_flag = True
        
        if eng_fail_aft_v1 == False and 65 < speed < 80 and failure_flag == False:
            send_birds()
            failure_flag = True


        aileron, elevator, rudder = get_control_inputs()
        deviation = compute_centerline_deviation(start_lat, start_lon, runway_heading, get_lat(), get_long())

        input_history["aileron"].append(aileron)
        input_history["elevator"].append(elevator)
        input_history["rudder"].append(rudder)
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




        vertical_speed = get_dref("sim/cockpit2/gauges/indicators/vvi_fpm_copilot")
        
        if vertical_speed >= 300 and retract_gear_flag == False:
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
            pitch = get_pitch()[0]
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
            result_queue.put(myClass)
            if myClass == 0: myClass_string = "NOVICE" 
            else: myClass_string = "EXPERT" 
            print(f"Classification: {myClass_string}")
            log_data(features)

            input_history = {"aileron": [], "elevator": [], "rudder": []}
            deviation_history = []
            pitch_history = []
            #loopTime = time.time() - startTime_for_perf
            #startTime_for_perf = time.time()
            speed_just_done = speed

        if get_dref("Mustang/alt_ft") > 1500:
            end = True


def get_dref(arg):
    with xpc.XPlaneConnect() as client:
        #get a dref
        dref = arg
        myValue = client.getDREF(dref)[0]
        return myValue