from customtkinter import *
from PIL import Image
import json
import signal


from echo_briefing_agent import *

refresh_rate = 0.1
port = 5670
agent_name = "Briefing"
device = "wlo1"
verbose = False
is_interrupted = False
start_heading = None

def weather_report_callback(io_type, name, value_type, value, my_data):
    # add code here if needed
    pass

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

igs.input_create("weatherReport", igs.DATA_T, None)

igs.output_create("status", igs.STRING_T, None)
igs.output_create("briefingPackage", igs.DATA_T, None)

igs.observe_input("weatherReport", weather_report_callback, agent)

igs.log_set_console(True)
igs.log_set_console_level(igs.LOG_INFO)

igs.start_with_device(device, port)
# catch SIGINT handler after starting agent
signal.signal(signal.SIGINT, signal_handler)

def create_package():
    data = {
        "departure_airport": departure_airport_input.get(),
        "arrival_airport": arrival_airport_input.get(),
        "flight_rules": radio_var.get(),
        "v1_speed": v1_speed_input.get(),
        "vr_speed": vr_speed_input.get(),
        "v2_speed": v2_speed_input.get(),
        "safe_altitude": safe_altitude_input.get(),
        "aviate": aviate_var.get(),
        "navigate": navigate_var.get(),
        "communicate": communicate_var.get()
    }
    
    print(json.dumps(data, indent=4))
    
    
    with open("briefing_package.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    byte_data = json.dumps(data).encode('utf-8')
    agent.briefing_package_o = byte_data
    agent.status_o = "Completed"


def radiobutton_event():
    print("Radiobutton event, current value: ", radio_var.get())

set_appearance_mode("dark")

app = CTk()
app.geometry("1500x1080")
app.title("Briefing")


tabview = CTkTabview(master=app)
tabview.grid(row=0, column= 0, padx=15, pady=15, sticky="w")
tabview.add("Flight Plan")
tabview.add("Weather")
tabview.add("Performances")
tabview.add("Fuel Plan")
tabview.add("Weight & Balance")
tabview.add("Departure Procedure")
tabview.add("Emergency Procedures")
tabview.add("Commmunication Plan")
tabview.add("Crew Roles")
tabview.add("Contingency Plan")
tabview.add("Aircraft Status")
tabview.add("Automation Plan")
tabview.add("Review")

mustang_image = CTkImage(size=(600,400), light_image=Image.open("/home/ben/DEVELOPMENT/Python_projects/ADAIR_Workshop/Random-Forest-TARS/Briefing/mustang.png"))
mustang_image_label = CTkLabel(master=app,text="", image=mustang_image)
mustang_image_label.grid(row=1, column=0, padx=20, pady=20)

flight_plan_title = CTkLabel(master=tabview.tab("Flight Plan"), text="Enter Flight plan details here...")
flight_plan_title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
weather_title = CTkLabel(master=tabview.tab("Weather"), text="Enter Weather details here...")
weather_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
performances_title = CTkLabel(master=tabview.tab("Performances"), text="Enter Performances details here...")
performances_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
fuel_plan_title = CTkLabel(master=tabview.tab("Fuel Plan"), text="Enter Fuel Plan details here...")
fuel_plan_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
weight_balance_title = CTkLabel(master=tabview.tab("Weight & Balance"), text="Enter Weight & Balance details here...")
weight_balance_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
departure_procedure_title = CTkLabel(master=tabview.tab("Departure Procedure"), text="Enter Departure Procedure details here...")
departure_procedure_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
emergency_procedures_title = CTkLabel(master=tabview.tab("Emergency Procedures"), text="Enter Emergency Procedures details here...")
emergency_procedures_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
communication_plan_title = CTkLabel(master=tabview.tab("Commmunication Plan"), text="Enter Communication Plan details here...")
communication_plan_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
crew_roles_title = CTkLabel(master=tabview.tab("Crew Roles"), text="Enter Crew Roles details here...")
crew_roles_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
contingency_plan_title = CTkLabel(master=tabview.tab("Contingency Plan"), text="Enter Contingency Plan details here...")
contingency_plan_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
aircraft_status_title = CTkLabel(master=tabview.tab("Aircraft Status"), text="Enter Aircraft Status details here...")
aircraft_status_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
automation_plan_title = CTkLabel(master=tabview.tab("Automation Plan"), text="Enter Automation Plan details here...")
automation_plan_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")
review_title = CTkLabel(master=tabview.tab("Review"), text="Review details here...")
review_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")

#Flight Plan Tab
departure_airport_label = CTkLabel(master=tabview.tab("Flight Plan"), text="Departure Airport:")
departure_airport_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
departure_airport_input = CTkEntry(master=tabview.tab("Flight Plan"), placeholder_text="Enter Departure Airport", width=300)
departure_airport_input.grid(row=1, column=1, padx=20, pady=(20, 5), sticky="w")

arrival_airport_label = CTkLabel(master=tabview.tab("Flight Plan"), text="Arrival Airport:")
arrival_airport_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
arrival_airport_input = CTkEntry(master=tabview.tab("Flight Plan"), placeholder_text="Enter Arrival Airport", width=300)
arrival_airport_input.grid(row=2, column=1, padx=20, pady=5, sticky="w")

radio_var = StringVar(value="")
radiobutton_vfr = CTkRadioButton(master=tabview.tab("Flight Plan"), text="VFR", command=lambda: print("VFR"), variable=radio_var, value="VFR")
radiobutton_vfr.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")
radiobutton_ifr = CTkRadioButton(master=tabview.tab("Flight Plan"), text="IFR", command=lambda: print("IFR"), variable=radio_var, value="IFR")
radiobutton_ifr.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="w")

#Performance Tab
v1_speed_label = CTkLabel(master=tabview.tab("Performances"), text="V1 Speed:")
v1_speed_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
v1speed = StringVar(value="70")
v1_speed_input = CTkEntry(master=tabview.tab("Performances"), placeholder_text="Enter V1 Speed in kts", width=300, textvariable=v1speed)
v1_speed_input.grid(row=1, column=1, padx=20, pady=(20, 5), sticky="w")
vr_speed_label = CTkLabel(master=tabview.tab("Performances"), text="VR Speed:")
vr_speed_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
vrspeed = StringVar(value="90")
vr_speed_input = CTkEntry(master=tabview.tab("Performances"), placeholder_text="Enter VR Speed", width=300, textvariable=vrspeed)
vr_speed_input.grid(row=2, column=1, padx=20, pady=5, sticky="w")
v2_speed_label = CTkLabel(master=tabview.tab("Performances"), text="V2 Speed:")
v2_speed_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
v2speed = StringVar(value="110")
v2_speed_input = CTkEntry(master=tabview.tab("Performances"), placeholder_text="Enter V2 Speed", width=300, textvariable=v2speed)
v2_speed_input.grid(row=3, column=1, padx=20, pady=5, sticky="w")

#Departure procedure Tab
safe_altitude_label = CTkLabel(master=tabview.tab("Departure Procedure"), text="Safe Altitude:")
safe_altitude_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
safealtitude = StringVar(value="1500")
safe_altitude_input = CTkEntry(master=tabview.tab("Departure Procedure"), placeholder_text="Enter Safe Altitude", width=300, textvariable=safealtitude)
safe_altitude_input.grid(row=1, column=1, padx=20, pady=(20, 5), sticky="w")

#Crew roles Tab
aviate_label = CTkLabel(master=tabview.tab("Crew Roles"), text="Aviate:")
aviate_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
aviate_var = StringVar(value="")
aviate_radiobutton_1 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="Pilot", variable=aviate_var, value="Aviate: Pilot")
aviate_radiobutton_1.grid(row=1, column=1, padx=20, pady=(20, 5), sticky="w")
aviate_radiobutton_2 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="TARS", variable=aviate_var, value="Aviate: TARS")
aviate_radiobutton_2.grid(row=1, column=2, padx=20, pady=(20, 5), sticky="w")

navigate_label = CTkLabel(master=tabview.tab("Crew Roles"), text="Navigate:")
navigate_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
navigate_var = StringVar(value="")
navigate_radiobutton_1 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="Pilot", variable=navigate_var, value="Navigate: Pilot")
navigate_radiobutton_1.grid(row=2, column=1, padx=20, pady=5, sticky="w")
navigate_radiobutton_2 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="TARS", variable=navigate_var, value="Navigate: TARS")
navigate_radiobutton_2.grid(row=2, column=2, padx=20, pady=5, sticky="w")

communicate_label = CTkLabel(master=tabview.tab("Crew Roles"), text="Communicate:")
communicate_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
communicate_var = StringVar(value="")
communicate_radiobutton_1 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="Pilot", variable=communicate_var, value="Communicate: Pilot")
communicate_radiobutton_1.grid(row=3, column=1, padx=20, pady=5, sticky="w")
communicate_radiobutton_2 = CTkRadioButton(master=tabview.tab("Crew Roles"), text="TARS", variable=communicate_var, value="Communicate: TARS")
communicate_radiobutton_2.grid(row=3, column=2, padx=20, pady=5, sticky="w")


#Review Tab
send_button = CTkButton(master=tabview.tab("Review"), text="Create Briefing package", command=create_package, corner_radius=32)
send_button.grid(row=0, column=0, padx=20, pady=20)

app.mainloop()