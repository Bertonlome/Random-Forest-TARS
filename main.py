import time
#from TARS import tars
time.sleep(1)
#from Aircraft import aircraft
import threading
import os
import subprocess
import multiprocessing

def run_script(script):
    os.system(f'python3 {script}')

process_briefing = multiprocessing.Process(target=run_script, args=('Briefing/briefing.py',))
process_aircraft = multiprocessing.Process(target=run_script, args=('Aircraft/aircraft.py',))
process_cognitive_model = multiprocessing.Process(target=run_script, args=('Cognitive_Model/cognitive_model.py',))
process_tars = multiprocessing.Process(target=run_script, args=('TARS/tars.py',))
process_inference_module = multiprocessing.Process(target=run_script, args=('TARS/inference_model/log_takeoff.py',))

process_briefing.start()
process_aircraft.start()
process_cognitive_model.start()
process_tars.start()
process_inference_module.start()

process_briefing.join()
process_aircraft.join()
process_cognitive_model.join()
process_tars.join()
process_inference_module.join()


# Launch as separate processes
#process_briefing = subprocess.Popen(['python3', 'Briefing/briefing.py'])
#process_tars = subprocess.Popen(['python3', 'TARS/tars.py'])
#process_aircraft = subprocess.Popen(['python3', 'Aircraft/aircraft.py'])
#process_inference_module = subprocess.Popen(['python3', 'TARS/inference_model/log_takeoff.py'])
#process_cognitive_model = subprocess.Popen(['python3', 'Cognitive_Model/cognitive_model.py'])
# Wait for both scripts to complete
#process_briefing.wait()
#process_aircraft.wait()
#process_inference_module.wait()
#process_tars.wait()
#process_cognitive_model.wait() 

"""

def run_tars():
    tars.main()

def run_aircraft():
    aircraft.main()

tars_thread = threading.Thread(target=run_tars)
tars_thread.daemon = True  # Allow the thread to exit when the main program exits
tars_thread.start()

time.sleep(5)

#aircraft_thread = threading.Thread(target=run_aircraft)
#aircraft_thread.daemon = True  # Allow the thread to exit when the main program exits
#aircraft_thread.start()

while True:
    i = 0
    i += 1 """

'''
old_inference = "NA"
inference_history = []
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[24].id)
engine.setProperty('rate', 140)

# Create a queue to communicate between threads
speech_queue = queue.Queue()
classification_queue = queue.Queue()

def run_briefing():
    briefing.main()

def run_annunciator():
    annunciator.main(speech_queue)  # Pass the queue to the annunciator script

def run_log_takeoff():
    log_takeoff.main(classification_queue, eng_fail_aft_v1=True)

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
        
# start the briefing in a separate thread
briefing_thread = threading.Thread(target=run_briefing)
briefing_thread.daemon = True  # Allow the thread to exit when the main program exits
briefing_thread.start()

# Start the speech processing in the main thread
speech_thread = threading.Thread(target=process_speech)
speech_thread.daemon = True  # Allow the thread to exit when the main program exits
speech_thread.start()

# Start the annunciator in a separate thread
annunciator_thread = threading.Thread(target=run_annunciator)
annunciator_thread.daemon = True  # Allow the thread to exit when the main program exits
annunciator_thread.start()

#Start the log_takeoff in a separate thread
log_takeoff_thread = threading.Thread(target=run_log_takeoff)
log_takeoff_thread.daemon = True  # Allow the thread to exit when the main program exits
log_takeoff_thread.start()

speech_queue.put("STOP")
annunciator_thread.join()
log_takeoff_thread.join()
'''