#!/usr/bin/env python3
# coding: utf-8
# =========================================================================
# main.py
#
# Copyright (c) the Contributors as noted in the AUTHORS file.
# This file is part of Ingescape, see https://github.com/zeromq/ingescape.
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =========================================================================
#
import signal
import time
import threading
import json
import sys
import os
from collections import Counter

sys.path.append(os.path.join(os.path.dirname(__file__), "../Briefing"))
from briefing_package import BriefingPackage, unpack_briefing_package

from echo_tars_agent import *
#from echo_tars_agent import *

refresh_rate = 0.1
port = 5670
agent_name = "TARS"
device = "wlo1"
verbose = False
is_interrupted = False
start_heading = None
briefing = None
ready = False
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
print("initializing TARS...")
briefing_package = BriefingPackage("LFBZ", "LESO", "IFR", v1, vr, v2, 1500, {"Aviate": "TARS", "Navigate": "TARS", "Communicate": "TARS"})
inference_history = []

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


#Define the states
class State:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

# Define the transitions
class Transition:
    def __init__(self, current_state, next_state, action, condition=None, allocation=None):
        self.current_state = current_state
        self.next_state = next_state
        self.action = action
        self.condition = condition
        self.allocation = allocation
        
    def is_condition_met(self):
        if self.condition is None:
            return True
        return self.condition()
    
    def is_allocation_met(self):
        if self.allocation is None:
            return True
        return self.allocation()

    def __repr__(self):
        return f"{self.current_state} -> {self.next_state} : {self.action}"

# Define the Finite State Machine
class FiniteStateMachine:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.transitions = []

    def add_transition(self, transition):
        self.transitions.append(transition)

    def run(self):
        print(f"Starting state: {self.current_state}")
        while (not is_interrupted) and igs.is_started():
            for transition in self.transitions:
                if transition.current_state == self.current_state and transition.is_condition_met() and transition.is_allocation_met():
                    print(f"Transitioning from {transition.current_state} to {transition.next_state}")
                    transition.action()
                    self.current_state = transition.next_state
                    transition_found = True
                    break  # Exit the for loop after executing a valid transition

            time.sleep(refresh_rate)  # Sleep to control the refresh rate

        if igs.is_started():
            igs.stop()


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
        return briefing_package.task_allocation[task] == "TARS"

def is_supporter(task):
    if briefing_package is None:
        print("Briefing package is None")
        return False
    else:
        return briefing_package.task_allocation[task] == "Pilot"
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
    runway_alignment_thread = threading.Thread(target=keep_target, args=(heading, 0.08, 0.02, 0.015, start_heading, rudderDref, False, 0.01, is_v2_reached))    
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
    wings_level_thread = threading.Thread(target=keep_target, args=(roll, -0.0006, 0.0014, 0.0001, 0, aileronDref, True, 0.1, is_safe_altitude_reached))
    wings_level_thread.daemon = True  # Set as a daemon thread to exit when the main program exits
    wings_level_thread.start()
    
    rotation_thread = threading.Thread(target=keep_target, args=(pitch, 0.006, 0.014, 0.001, target_pitch, elevatorDref, False, 0.1, is_safe_altitude_reached))
    rotation_thread.daemon = True
    rotation_thread.start()

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

# Create the states
wait_for_start = State("WaitForstart")
acceleration = State("Acceleration")
rotation = State("Rotation")
climb = State("Climb")
stabilize = State("Stabilize")

# Create the transitions
transition1_perf = Transition(wait_for_start, acceleration, acceleration_action, condition=is_agent_on_and_aircraft_ready, allocation=lambda: is_performer("Aviate"))
transition2_perf = Transition(acceleration, rotation, rotation_action, condition=is_vr_reached, allocation=lambda: is_performer("Aviate"))
transition3_perf = Transition(rotation, climb, climb_action, condition=is_positive_rate, allocation=lambda: is_performer("Aviate"))
transition4_perf = Transition(climb, stabilize, stabilize_action, condition=is_safe_altitude_reached, allocation=lambda: is_performer("Aviate"))

transition1_supp = Transition(wait_for_start, acceleration, acceleration_supp, condition=is_agent_on_and_aircraft_ready, allocation=lambda: is_supporter("Aviate"))
transition2_supp = Transition(acceleration, rotation, rotation_supp, condition=is_vr_reached, allocation= lambda: is_supporter("Aviate"))
transition3_supp = Transition(rotation, climb, climb_supp, condition=is_positive_rate, allocation= lambda: is_supporter("Aviate"))
transition4_supp = Transition(climb, stabilize, stabilize_supp, condition=is_safe_altitude_reached, allocation= lambda: is_supporter("Aviate"))


# Create the FSM and add transitions
fsm = FiniteStateMachine(wait_for_start)
fsm.add_transition(transition1_perf)
fsm.add_transition(transition2_perf)
fsm.add_transition(transition3_perf)
fsm.add_transition(transition4_perf)
fsm.add_transition(transition1_supp)
fsm.add_transition(transition2_supp)
fsm.add_transition(transition3_supp)
fsm.add_transition(transition4_supp)

def keep_target(current_value, ky, kyi, kyd, target, controller, debug=True, rate=0.01, condition=None, inversed=-1):
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
        if controller == rudderDref:
            derivative = (error - previous_error) / dt if dt > 0.01 else 0
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
    ready = True
    agent_object.status_o = "Started"
    
def briefing_input_callback(io_type, name, value_type, value, my_data):
    global briefing_package
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    briefing_package = unpack_briefing_package(value)
    print(briefing_package.task_allocation)
    agent_object.status_o = "Briefing received"

def controlPerception_input_callback(io_type, name, value_type, value, my_data):
    global control
    if value == True:
        print(f"Inference received :  Pilot is in control")
        agent.status_o = "Pilot is in control"
    else:
        print(f"Inference received :  Pilot has poor control")
        agent.status_o = "Pilot has poor control"
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    control = value
    inference_history.append(value)
    counts = Counter(inference_history)
    majority_vote = counts.most_common(1)[0][0]
    print(f"Majority vote: {majority_vote}")
    if majority_vote == True:
        agent_object.level_of_automation_o = "Low LOA"
    else:
        agent_object.level_of_automation_o = "High LOA"



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
igs.input_create("briefingPackage", igs.DATA_T, None)
igs.input_create("controlPerception", igs.BOOL_T, None)
igs.input_create("airspeed", igs.DOUBLE_T, None)
igs.input_create("pitch", igs.DOUBLE_T, None)
igs.input_create("roll", igs.DOUBLE_T, None)
igs.input_create("heading", igs.DOUBLE_T, None)
igs.input_create("verticalSpeed", igs.DOUBLE_T, None)
igs.input_create("altitude", igs.DOUBLE_T, None)

igs.output_create("status", igs.STRING_T, None)
igs.output_create("levelOfAutomation", igs.STRING_T, None)
igs.output_create("elevator", igs.DOUBLE_T, None)
igs.output_create("rudder", igs.DOUBLE_T, None)
igs.output_create("aileron", igs.DOUBLE_T, None)
igs.output_create("throttle", igs.DOUBLE_T, None)
igs.output_create("flaps", igs.INTEGER_T, None)
igs.output_create("gear", igs.IMPULSION_T, None)
igs.output_create("brake", igs.IMPULSION_T, None)

igs.observe_input("start", start_input_callback, agent)
igs.observe_input("briefingPackage", briefing_input_callback, agent)
igs.observe_input("controlPerception", controlPerception_input_callback, agent)
igs.observe_input("airspeed", double_input_callback, agent)
igs.observe_input("pitch", double_input_callback, agent)
igs.observe_input("roll", double_input_callback, agent)
igs.observe_input("heading", double_input_callback, agent)
igs.observe_input("verticalSpeed", double_input_callback, agent)
igs.observe_input("altitude", double_input_callback, agent)


igs.log_set_console(True)
igs.log_set_console_level(igs.LOG_INFO)

igs.start_with_device(device, port)
# catch SIGINT handler after starting agent
signal.signal(signal.SIGINT, signal_handler)

def main():
    fsm.run()

main()
