import actr
import annunciator
import signal
import time
import threading
import json
import sys
import os

from briefing_package import BriefingPackage, unpack_briefing_package

from echo_cognitive_model_agent import *

# Global variables
refresh_rate = 0.1
port = 5670
agent_name = "Pilot_Cognitive_Model"
device = "wlo1"
verbose = False
is_interrupted = False

# Start params
start_heading = None
ready = "False"
airspeed = 0
pitch = 0
roll = 0
heading = 0
vertical_speed = 0
altitude = 0
agent = None
v1 = 75
vr = 90
v2 = 110
target_pitch = 10
briefing_package = None
l_throttle = 0
r_throttle = 0
master_w = 0
master_c = 0
eicas_alarms = 0
engine_1_N1 = 0
engine_2_N1 = 0
engine_fire_alarm = 0
outside_event = None
response = None
rotation = False

print("initializing Pilot cognitive model...")

## def datarefs string
iasDref = "sim/cockpit2/gauges/indicators/airspeed_kts_pilot"
pitchDref = "sim/cockpit2/gauges/indicators/pitch_AHARS_deg_pilot"
altitudeDref = "sim/cockpit2/gauges/indicator/altitude_ft_pilot"
thrustDref = "sim/flightmodel/engine/ENGN_thro_override"
headingDref = "sim/cockpit2/gauges/indicators/heading_AHARS_deg_mag_pilot" # 0 to 1, override because it is a double instead of an array
rollDref = "sim/cockpit2/gauges/indicators/roll_AHARS_deg_pilot"
parkBrakeDref = "sim/cockpit2/controls/parking_brake_ratio"
verticalSpeedDref = "sim/cockpit2/gauges/indicators/vvi_fpm_pilot"
rudderDref = "sim/cockpit2/controls/yoke_heading_ratio"
elevatorDref = "sim/cockpit2/controls/yoke_pitch_ratio"
aileronDref = "sim/cockpit2/controls/yoke_roll_ratio"
mustang_l_throttle = "Mustang/cockpit/engine/l_throttle"
mustang_r_throttle = "Mustang/cockpit/engine/r_throttle"
master_wDref= "Mustang/master_warning"
master_cDref = "Mustang/master_caution"
eicas_alarmsDref = "sim/flightmodel/engine/ENGN_oil_press"
engine_1_N1Dref = "sim/cockpit2/engine/indicators/N1_percent"
engine_2_N1Dref = "sim/cockpit2/engine/indicators/N1_percent"
engine_fire_alarmDref = "sim/cockpit/warnings/annunciators/engine_fire"

#Define the states
class State:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


#Define the conditions
def is_agent_on_and_aircraft_ready():
    global ready
    return ready

def is_vr_reached():
    return airspeed >= vr

def is_v2_reached():
    return airspeed >= v2

def is_positive_rate():
    return vertical_speed >= 250 

def is_pitch_bad():
    return pitch <= 6 and pitch >= 12

def is_safe_altitude_reached():
    return altitude >= 1500

def is_performer(task):
    if briefing_package is None:
        print("Briefing package is None")
        return False
    else:
        return briefing_package.task_allocation[task] == "Pilot"

def is_supporter(task):
    if briefing_package is None:
        print("Briefing package is None")
        return False
    else:
        return briefing_package.task_allocation[task] == "TARS"
# Define the actions
def wait_for_start_action():
    print("Waiting for start.")
    agent.status_o = "Waiting for start."
    agent.flaps_o = 0.5
    agent.brake_o = 0

def acceleration_action():
    global start_heading
    start_heading = heading
    agent.status_o = "Accelerating."
    print("Full throttle! let's takeoff!")
    agent.throttle_o = 1
    time.sleep(6)
    agent.brake_o = 1
    time.sleep(3)
    runway_alignment_thread = threading.Thread(target=keep_target, args=(heading, 0.08, 0.02, 0.001, start_heading, rudderDref, False, 0.01, is_v2_reached))    
    runway_alignment_thread.daemon = True
    runway_alignment_thread.start()

def acceleration_supp():
    print("Supporting acceleration.")
    agent.status_o = "Supporting acceleration."

def rotation_action():
    global pitch
    agent.status_o = "Rotating."
    print("VR reached. Rotate!")
    # Start keep_aircraft_aligned() in a new thread
    wings_level_thread = threading.Thread(target=keep_target, args=(roll, -0.0006, 0.0014, 0.0001, 0, aileronDref, False, 0.1, is_safe_altitude_reached))
    wings_level_thread.daemon = True  # Set as a daemon thread to exit when the main program exits
    wings_level_thread.start()
    rotation_thread = threading.Thread(target=keep_target, args=(pitch, 0.006, 0.014, 0.001, target_pitch, elevatorDref, False, 0.1))
    rotation_thread.daemon = True
    rotation_thread.start()
    
def rejected_takeoff_action():
    print("Rejected takeoff.")
    agent.status_o = "Rejected takeoff."
    agent.throttle_o = 0
    agent.brake_o = 1
    agent.flaps_o = 0

def rotation_supp():
    print("Supporting rotation.")
    agent.status_o = "Supporting rotation."

def climb_action():
    global airspeed
    agent.status_o = "Climbing."
    print("Climbing to safe altitude.")
    agent.gear_o = True

def climb_supp():
    print("Supporting climb.")
    agent.status_o = "Supporting climb."

def stabilize_action():
    global target_pitch
    target_pitch = 5
    print("Stabilizing.")
    agent.status_o = "Stabilizing."
    agent.flaps_o = 0
    agent.throttle_o = 0.8

def stabilize_supp():
    print("Supporting stabilization.")
    agent.status_o = "Supporting stabilization."

def keep_target(current_value, ky, kyi, kyd, target, controller, debug=False, rate=0.01, condition=None, inversed=-1):
    global pitch, roll, heading, airspeed, vertical_speed, target_pitch
    integral = 0  # Integral term for the PID controller
    previous_error = 0  # Previous error for the derivative term
    time_old = time.time()
    while True:
        # Check if the custom condition exists and evaluates to True
        if condition is not None and condition():
            break
        # Get the current value of the data reference (e.g., indicated airspeed)
        if controller == elevatorDref:
            current_value = pitch
            target = target_pitch
        elif controller == rudderDref:
            current_value = heading
        elif controller == aileronDref:
            current_value = roll
        
        # Calculate the error (difference between current and target)
        error = current_value - target
        # Update the integral term
        time_current = time.time()
        dt = time_current - time_old
        integral += error * dt
        # Calculate the derivative term
        derivative = (error - previous_error) / dt if dt > 0.1 else 0
        # Calculate the control output using a PID controller
        proportional = ky * error
        integral_term = kyi * integral
        derivative_term = kyd * derivative
        control = proportional + integral_term + derivative_term
        # Apply the control to the elevator (or other controller)
        if controller == elevatorDref:
            agent.elevator_o = inversed * control
        elif controller == rudderDref:
            agent.rudder_o = inversed * control
        elif controller == aileronDref:
            agent.aileron_o = inversed * control
        # Debugging output
        if debug:
            print(
                f"dt = {dt}"
                f"Current: {current_value:.2f}, Target: {target}, "
                f"Error: {error:.2f}, Control: {control:.4f}, "
                f"Proportional: {proportional:.4f}, Integral: {integral_term:.4f}, Derivative: {derivative_term:.4f}"
            )
        # Update old values for the next iteration
        previous_error = error
        time_old = time_current
        # Sleep to control the loop rate
        time.sleep(rate)

def return_io_value_type_as_str(value_type):
    if value_type == igs.INTEGER_T:
        return "Airspeed"
    elif value_type == igs.DOUBLE_T:
        return "Double"
    elif value_type == igs.BOOL_T:
        return "Bool"
    elif value_type == igs.STRING_T:
        return "String"
    elif value_type == igs.IMPULSION_T:
        return "Impulsion"
    elif value_type == igs.DATA_T:
        return "Data"
    else:
        return "Unknown"

def return_event_type_as_str(event_type):
    if event_type == igs.PEER_ENTERED:
        return "PEER_ENTERED"
    elif event_type == igs.PEER_EXITED:
        return "PEER_EXITED"
    elif event_type == igs.AGENT_ENTERED:
        return "AGENT_ENTERED"
    elif event_type == igs.AGENT_UPDATED_DEFINITION:
        return "AGENT_UPDATED_DEFINITION"
    elif event_type == igs.AGENT_KNOWS_US:
        return "AGENT_KNOWS_US"
    elif event_type == igs.AGENT_EXITED:
        return "AGENT_EXITED"
    elif event_type == igs.AGENT_UPDATED_MAPPING:
        return "AGENT_UPDATED_MAPPING"
    elif event_type == igs.AGENT_WON_ELECTION:
        return "AGENT_WON_ELECTION"
    elif event_type == igs.AGENT_LOST_ELECTION:
        return "AGENT_LOST_ELECTION"
    else:
        return "UNKNOWN"

def signal_handler(signal_received, frame):
    global is_interrupted
    print("\n", signal.strsignal(signal_received), sep="")
    is_interrupted = True


def on_agent_event_callback(event, uuid, name, event_data, my_data):
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    # add code here if needed


def on_freeze_callback(is_frozen, my_data):
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    # add code here if needed
    
def string_input_callback(io_type, name, value_type, value, my_data):
    global outside_event
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    if name == "outsideEvent":
        outside_event = value

def double_input_callback(io_type, name, value_type, value, my_data):
    global airspeed, pitch, roll, heading, vertical_speed, altitude
    #igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    if name == "airspeed":
        airspeed = value
    elif name == "pitch":
        pitch = value
    elif name == "roll":
        roll = value
    elif name == "heading":
        heading = value
    elif name == "verticalSpeed":
        vertical_speed = value
    elif name == "altitude":
        altitude = value

def start_input_callback(io_type, name, value_type, value, my_data):
    global ready
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    ready = "True"
    agent_object.status_o = "Started"
    
def briefing_input_callback(io_type, name, value_type, value, my_data):
    global briefing_package
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    briefing_package = unpack_briefing_package(value)
    print(briefing_package.task_allocation)
    agent_object.status_o = "Briefing received"


# catch SIGINT handler before starting agent
signal.signal(signal.SIGINT, signal_handler)

igs.agent_set_name(agent_name)
igs.definition_set_version("1.0")
igs.log_set_console(verbose)
igs.log_set_file(True, None)
igs.log_set_stream(verbose)
igs.set_command_line(sys.executable + " " + " ".join(sys.argv))

agent = Echo()

igs.observe_agent_events(on_agent_event_callback, agent)
igs.observe_freeze(on_freeze_callback, agent)

igs.input_create("start", igs.IMPULSION_T, None)
igs.input_create("declarativeKnowledge", igs.DATA_T, None)
igs.input_create("proceduralKnowledge", igs.DATA_T, None)
igs.input_create("freeParameters", igs.DATA_T, None)
igs.input_create("briefingPackage", igs.DATA_T, None)
igs.input_create("airspeed", igs.DOUBLE_T, None)
igs.input_create("pitch", igs.DOUBLE_T, None)
igs.input_create("roll", igs.DOUBLE_T, None)
igs.input_create("heading", igs.DOUBLE_T, None)
igs.input_create("verticalSpeed", igs.DOUBLE_T, None)
igs.input_create("altitude", igs.DOUBLE_T, None)
igs.input_create("outsideEvent", igs.STRING_T, None)

igs.output_create("status", igs.STRING_T, None)
igs.output_create("elevator", igs.DOUBLE_T, None)
igs.output_create("rudder", igs.DOUBLE_T, None)
igs.output_create("aileron", igs.DOUBLE_T, None)
igs.output_create("throttle", igs.DOUBLE_T, None)
igs.output_create("flaps", igs.INTEGER_T, None)
igs.output_create("gear", igs.IMPULSION_T, None)
igs.output_create("brake", igs.IMPULSION_T, None)

igs.observe_input("start", start_input_callback, agent)
igs.observe_input("briefingPackage", briefing_input_callback, agent)
igs.observe_input("airspeed", double_input_callback, agent)
igs.observe_input("pitch", double_input_callback, agent)
igs.observe_input("roll", double_input_callback, agent)
igs.observe_input("heading", double_input_callback, agent)
igs.observe_input("verticalSpeed", double_input_callback, agent)
igs.observe_input("altitude", double_input_callback, agent)
igs.observe_input("outsideEvent", string_input_callback, agent)


igs.log_set_console(True)
igs.log_set_console_level(igs.LOG_INFO)

igs.start_with_device(device, port)
# catch SIGINT handler after starting agent
signal.signal(signal.SIGINT, signal_handler)

# Load the corresponding model
actr.load_act_r_model("/home/ben/DEVELOPMENT/Python_projects/ADAIR_Workshop/Random-Forest-TARS/Cognitive_Model/takeoff_model.lisp")

def experiment (human=False):
    global ready, master_w, master_c, eicas_alarms, airspeed, engine_1_N1, engine_2_N1, l_throttle, r_throttle, engine_fire_alarm
    actr.reset()
    #   window - the ACT-R window device list returned by using the ACT-R
    #            function open_exp_window to create a new window for 
    #            displaying the experiment 
    window = actr.open_exp_window("MUSTANG-COCKPIT", width=600, height=600)

    # display the items in the window that was opened
    #visual representation of the mustang control panel
    outside_event = actr.add_text_to_exp_window(window, "ENVIRONMENT", x=200, y=0)
    master_w_label = actr.add_text_to_exp_window(window, "MASTER W", x=50, y=25)
    master_w_item = actr.add_text_to_exp_window(window, str(master_w), x=50, y=50)
    master_c_label = actr.add_text_to_exp_window(window, "MASTER C", x=125, y=25)
    master_c_item = actr.add_text_to_exp_window(window, str(master_c), x=125, y=50)
    eicas_alarms_label = actr.add_text_to_exp_window(window, "EICAS", x=225, y=25)
    eicas_alarms_item = actr.add_text_to_exp_window(window, str(eicas_alarms), x=225, y=50)
    kias_label = actr.add_text_to_exp_window(window, "KIAS", x=50, y=75)
    kias_item = actr.add_text_to_exp_window(window, "0", x=50, y=100)
    engine_1_N1_label = actr.add_text_to_exp_window(window, "ENGINE 1 N1%", x=125, y=75)
    engine_1_N1_item = actr.add_text_to_exp_window(window, str(int(engine_1_N1)), x=125, y=100)
    engine_2_N1_label = actr.add_text_to_exp_window(window, "ENGINE 2 N1%", x=225, y=75)
    engine_2_N1_item = actr.add_text_to_exp_window(window, str(int(engine_2_N1)), x=225, y=100)
    l_throttle_label = actr.add_text_to_exp_window(window, "THROTTLE L", x=50, y=225)
    l_throttle_item = actr.add_text_to_exp_window(window, str(int(l_throttle)), x=50, y=250)
    r_throttle_label = actr.add_text_to_exp_window(window, "THROTTLE R", x=225, y=225)
    r_throttle_item = actr.add_text_to_exp_window(window, str(int(r_throttle)), x=225, y=250)
    engine_fire_alarm_label = actr.add_text_to_exp_window(window, "ENGINE FIRE ALARM", x=400, y=25)
    engine_fire_alarm_item = actr.add_text_to_exp_window(window, str(int(engine_fire_alarm)), x=400, y=50)
    ready_label = actr.add_text_to_exp_window(window, "READY", x=50, y=325)
    ready_item = actr.add_text_to_exp_window(window, str(ready), x=50, y=350)
    aviate_label = actr.add_text_to_exp_window(window, "AVIATE", x=50, y=375)
    aviate_item = actr.add_text_to_exp_window(window, "INIT", x=50, y=400)
    navigate_label = actr.add_text_to_exp_window(window, "NAVIGATE", x=150, y=375)
    navigate_item = actr.add_text_to_exp_window(window, "INIT", x=150, y=400)
    communicate_label = actr.add_text_to_exp_window(window, "COMMUNICATE", x=250, y=375)
    communicate_item = actr.add_text_to_exp_window(window, "INIT", x=250, y=400)

    actr.add_command("demo2-key-press", respond_to_key_press, "Demo2 task output-key monitor")    
    actr.monitor_command("output-key","demo2-key-press")
    global response
    response = False

    actr.add_command("agi-move-it",move_text)
    actr.schedule_event_relative (5, "agi-move-it",params=[master_w_item, "MASTER_W"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[master_c_item, "MASTER_C"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[eicas_alarms_item, "EICAS_ALARM"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[kias_item, "KIAS"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_1_N1_item, "ENGINE_1_N1%"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_2_N1_item, "ENGINE_2_N1%"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[l_throttle_item, "THROTTLE_l"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[r_throttle_item, "THROTTLE_r"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_fire_alarm_item, "ENGINE_FIRE_ALARM"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[ready_item, "READY"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[aviate_item, "AVIATE"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[navigate_item, "NAVIGATE"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[communicate_item, "COMMUNICATE"],maintenance=True)
    actr.schedule_event_relative(5, "agi-move-it",params=[outside_event, "ENVIRONMENT"],maintenance=True)
    actr.install_device(window)
    actr.run(100,True)

    actr.remove_command_monitor("output-key","demo2-key-press")
    actr.remove_command("demo2-key-press")
    actr.remove_command("agi-move-it")
    return response

def respond_to_key_press (model,key):
    global rotation
    print("model pressed key : " + key)
    if key == "1":
        print("key 1 pressed, scenario started")
    if key == "2":
        print("key 2 pressed, Pilot performing Aviate")
        acceleration_action()
    if key == "3":
        print("key 3 pressed, TARS performing Aviate")
    if key == "4":
        if not rotation:
            print("key 4 pressed, Rotation!")
            rotation_action()
            rotation = True
    if key == "5":
        print("key 5 pressed, birds detected")
        rejected_takeoff_action()

def move_text(text,type):
    global master_w, master_c, eicas_alarms, airspeed, engine_1_N1, engine_2_N1, l_throttle, r_throttle, engine_fire_alarm
    if type == "MASTER_W":
        newValue = str(master_w)
    if type == "MASTER_C":
        newValue = str(master_c)
    elif type == "EICAS_ALARM":
        newValue = str(eicas_alarms)
    elif type == "KIAS":
        if airspeed < 0: airspeed = 0
        elif airspeed > 90: newValue = "vr"
        else: newValue = str(int(airspeed))
    elif type == "ENGINE_1_N1%":
        newValue = str(int(engine_1_N1))
    elif type == "ENGINE_2_N1%":
        newValue = str(int(engine_2_N1))
    elif type == "THROTTLE_l":
        newValue = str(l_throttle)
    elif type == "THROTTLE_r":
        newValue = str(r_throttle)
    elif type == "ENGINE_FIRE_ALARM":
        newValue = str(engine_fire_alarm)
    elif type == "READY":
        newValue = ready
    elif type == "AVIATE":
        if briefing_package is not None: newValue = briefing_package.task_allocation["Aviate"]
        else: newValue = "INIT"
    elif type == "NAVIGATE":
        if briefing_package is not None: newValue = briefing_package.task_allocation["Navigate"]
        else: newValue = "INIT"
    elif type == "COMMUNICATE":
        if briefing_package is not None: newValue = briefing_package.task_allocation["Communicate"]
        else: newValue = "INIT"
    elif type == "ENVIRONMENT":
        newValue = outside_event
    actr.current_connection.evaluate_single("modify-text-for-exp-window", text, [["text", newValue]])
    actr.schedule_event_relative(4, "agi-move-it",params=[text, type],maintenance=True)

experiment()
igs.stop()