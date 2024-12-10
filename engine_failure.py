# Import the actr module for tutorial tasks

import actr
import xpc
import time
import pyttsx3
import annunciator
import log_takeoff
import threading
import queue
from collections import Counter
import flightdir

old_inference = "NA"
inference_history = []
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[24].id)
engine.setProperty('rate', 140)

# Create a queue to communicate between threads
speech_queue = queue.Queue()
classification_queue = queue.Queue()

def run_annunciator():
    annunciator.main(speech_queue)  # Pass the queue to the annunciator script

def run_log_takeoff():
    log_takeoff.main(classification_queue, eng_fail_aft_v1=True)  # Assuming log_takeoff.py has a main function

def run_flight_dir():
    flightdir.main()

def process_speech():
    while True:
        message = speech_queue.get()  # Get a message from the queue
        if message == "STOP":
            break  # Exit the loop if we receive the stop signal
        print(f"Speaking: {message}")
        engine.say(message)
        engine.runAndWait()

# Start the speech processing in the main thread
speech_thread = threading.Thread(target=process_speech)
speech_thread.daemon = True  # Allow the thread to exit when the main program exits
speech_thread.start()

# Start the annunciator in a separate thread
annunciator_thread = threading.Thread(target=run_annunciator)
annunciator_thread.start()

#Start the log_takeoff in a separate thread
log_takeoff_thread = threading.Thread(target=run_log_takeoff)
log_takeoff_thread.start()



# Load the corresponding model
actr.load_act_r_model("ACT-R:Xplane_thesis_model;engine_failure_model_mcgill_ai.lisp")
    

def move_text(text,type):
    global old_inference
    if type == "MASTER_W":
        newValue = get_dref("Mustang/master_warning")
    if type == "MASTER_C":
        newValue = get_dref("Mustang/master_caution")
    elif type == "EICAS_ALARM":
        newValue = get_dref("sim/flightmodel/engine/ENGN_oil_press")
    elif type == "KIAS":
        if annunciator.get_IAS() > 90:
            newValue = "1"
        else:
            newValue = "0"
    elif type == "ENGINE_1_N1%":
        newValue = get_eng1_n1("sim/cockpit2/engine/indicators/N1_percent")
    elif type == "ENGINE_2_N1%":
        newValue = get_eng2_n1("sim/cockpit2/engine/indicators/N1_percent")
    elif type == "THROTTLE_l":
        newValue = get_dref("Mustang/cockpit/engine/l_throttle")
    elif type == "THROTTLE_r":
        newValue = get_dref("Mustang/cockpit/engine/r_throttle")
    elif type == "ENGINE_FIRE_ALARM":
        newValue = get_dref("sim/cockpit/warnings/annunciators/engine_fire")
    elif type == "PILOT_CONTROL":
        try:
            newValue = classification_queue.get(timeout=0.01)
            print(f"inference history entry : {newValue}")
            inference_history.append(newValue)
            if inference_history:
                counts = Counter(inference_history)
                majority_vote = counts.most_common(1)[0][0]
                print(f"Majority vote: {majority_vote}")
                newValue = majority_vote
            else:
                newValue = old_inference
            old_inference = newValue
        except queue.Empty:
            newValue = old_inference
            pass

    actr.current_connection.evaluate_single("modify-text-for-exp-window", text, [["text", str(newValue)]])
    actr.schedule_event_relative(1, "agi-move-it",params=[text, type],maintenance=True)

def respond_to_key_press (model,key):
    print("model pressed key : " + key)
    if key == "a":
        call_out_master_w()
    elif key == "b":
        call_out_master_c()
    elif key == "c":
        call_out_engine_fire()
    elif key == "m":
        call_out_reject_takeoff()
    elif key == "0":
        high_loa_engine_failure()
    elif key == "1":
        low_loa_engine_failure()


def high_loa_engine_failure():
    flight_dir = threading.Thread(target=run_flight_dir)
    flight_dir.start()
    with xpc.XPlaneConnect() as client:
        left_engine = get_dref("sim/operation/failures/rel_engfir0")
        if int(left_engine) > 0:
            print("LEFT ENGINE FAIL, SET RUDDER TRIM FULL RIGHT")
            engine.say("LEFT ENGINE FAIL, SET RUDDER TRIM FULL RIGHT")
            engine.runAndWait()
            gear_dref = "sim/cockpit2/controls/rudder_trim"
            client.sendDREF(gear_dref, 1)
        else:
            print("RIGHT ENGINE FAIL, SET RUDDER TRIM FULL LEFT")
            engine.say("RIGHT ENGINE FAIL, SET RUDDER TRIM FULL LEFT")
            engine.runAndWait()
            gear_dref = "sim/cockpit2/controls/rudder_trim"
            client.sendDREF(gear_dref, -1)

def low_loa_engine_failure():
    flight_dir = threading.Thread(target=run_flight_dir)
    flight_dir.start()

def call_out_master_w():
    print("call out: MASTER WARNING")
    engine.say("MASTER WARNING")
    engine.runAndWait()

def call_out_master_c():
    print("call out: MASTER CAUTION")
    engine.say("MASTER CAUTION")
    engine.runAndWait()

def call_out_engine_fire():
    print("call out: ENGINE FIRE")
    engine.say("ENGINE FIRE")
    engine.runAndWait()

def call_out_reject_takeoff():
    print("call out: Reject Takeoff")
    engine.say("REJECT TAKEOFF")
    engine.runAndWait()


def get_dref(arg):
    with xpc.XPlaneConnect() as client:
        dref = arg
        myValue = client.getDREF(dref)
        myValueText = str(myValue).split('.')[0]
        myValueText = myValueText.replace('(','')
        if int(myValueText) < 0:
            myValueText = "C"
        return myValueText
    
def get_eng1_n1(arg):
    with xpc.XPlaneConnect() as client:
        dref = arg
        myValue = client.getDREF(dref)[0]
        myValueText = str(myValue).split('.')[0]
        myValueText = myValueText.replace('(','')
        if int(myValueText) < 0:
            myValueText = "0"
        return myValueText
    
def get_eng2_n1(arg):
    with xpc.XPlaneConnect() as client:
        dref = arg
        myValue = client.getDREF(dref)[1]
        myValueText = str(myValue).split('.')[0]
        myValueText = myValueText.replace('(','')
        if int(myValueText) < 0:
            myValueText = "0"
        return myValueText
            

def experiment (human=False):
    global old_inference
    actr.reset()
    #   window - the ACT-R window device list returned by using the ACT-R
    #            function open_exp_window to create a new window for 
    #            displaying the experiment 
    window = actr.open_exp_window("MUSTANG-COCKPIT", width=600, height=600)

    # display the items in the window that was opened
    #visual representation of the C172 control panel
    master_w = actr.add_text_to_exp_window(window, get_dref("Mustang/master_warning"), x=50, y=50)
    master_c = actr.add_text_to_exp_window(window, get_dref("Mustang/master_caution"), x=100, y=50)
    eicas_alarms = actr.add_text_to_exp_window(window, get_dref("sim/flightmodel/engine/ENGN_oil_press"), x=200, y=50)
    kias = actr.add_text_to_exp_window(window, "0", x=50, y=100)
    engine_1_N1 = actr.add_text_to_exp_window(window, get_eng1_n1("sim/cockpit2/engine/indicators/N1_percent"), x=100, y=100)
    engine_2_N1 = actr.add_text_to_exp_window(window, get_eng2_n1("sim/cockpit2/engine/indicators/N1_percent"), x=200, y=100)
    l_throttle = actr.add_text_to_exp_window(window, get_dref("Mustang/cockpit/engine/l_throttle"), x=50, y=250)
    r_throttle = actr.add_text_to_exp_window(window, get_dref("Mustang/cockpit/engine/r_throttle"), x=200, y=250)
    engine_fire_alarm = actr.add_text_to_exp_window(window, get_dref("sim/cockpit/warnings/annunciators/engine_fire"), x=400, y=50)
    expertise_inference = actr.add_text_to_exp_window(window, "NA", x=200, y=500)


    actr.add_command("demo2-key-press",respond_to_key_press, "Demo2 task output-key monitor")
    actr.add_command("x-plane-getdref", get_dref)
    
    actr.monitor_command("output-key","demo2-key-press")
    global response
    response = False

    actr.add_command("call-out-alarm", call_out_master_w)
    actr.add_command("agi-move-it",move_text)
    actr.schedule_event_relative (5, "agi-move-it",params=[master_w, "MASTER_W"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[master_c, "MASTER_C"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[eicas_alarms, "EICAS_ALARM"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[kias, "KIAS"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_1_N1, "ENGINE_1_N1%"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_2_N1, "ENGINE_2_N1%"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[l_throttle, "THROTTLE_l"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[r_throttle, "THROTTLE_r"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[engine_fire_alarm, "ENGINE_FIRE_ALARM"],maintenance=True)
    actr.schedule_event_relative (5, "agi-move-it",params=[expertise_inference, "PILOT_CONTROL"],maintenance=True)

    actr.install_device(window)
    actr.run(200,True)

    actr.remove_command_monitor("output-key","demo2-key-press")
    actr.remove_command("demo2-key-press")
    actr.remove_command("agi-move-it")
    return response


experiment()

speech_queue.put("STOP")
annunciator_thread.join()
log_takeoff_thread.join()
