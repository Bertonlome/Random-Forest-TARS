import time
import xpc
from inference_model.log_takeoff import get_dref

def get_IAS():
    with xpc.XPlaneConnect() as client:
        #get a dref
        dref = "sim/cockpit2/gauges/indicators/airspeed_kts_pilot"
        myValue = int(client.getDREF(dref)[0])
        return myValue
    
    
def callout(speech_queue, speech):
    speech_queue.put(speech)
    
def main(speech_queue):
    vRotate = False
    vRotateValue = 90
    thrustSetFlag = False
    airspeed_alive_flag = False
    seventy_kts_flag = False
    positive_rate_flag = False
    acceleration_alt_flag = False
    speech_queue.put("TEST TEST")
    engine_failure_flag = False

    while True:
        time.sleep(0.1)

        left_engine = get_dref("sim/operation/failures/rel_engfir0")
        right_engine = get_dref("sim/operation/failures/rel_engfir0")
        if(left_engine or right_engine != 0):
            engine_failure_flag = True


        if thrustSetFlag == False:
            throttle_position = get_dref("Mustang/cockpit/engine/l_throttle")
            if throttle_position == 1:
                thrustSetFlag = True
                callout(speech_queue, "THRUST SET")

        if airspeed_alive_flag == False:
            airspeed = get_IAS()
            if int(airspeed) >= 32:
                airspeed_alive_flag = True
                callout(speech_queue, "AIRSPEED ALIVE")

        if seventy_kts_flag == False:
            airspeed = get_IAS()
            if int(airspeed) >= 70:
                seventy_kts_flag = True
                callout(speech_queue, "SEVENTY KNOTS")

        if vRotate == False:
            airspeed = get_IAS()
            if airspeed == vRotateValue and engine_failure_flag == False:
                callout(speech_queue, "ROTATE")
                vRotate = True
        
        if positive_rate_flag == False:
            vertical_speed = get_dref("sim/cockpit2/gauges/indicators/vvi_fpm_copilot")
            if vertical_speed >= 300:
                positive_rate_flag = True
                callout(speech_queue, "POSITIVE RATE")

        if acceleration_alt_flag == False:
            alt = get_dref("Mustang/alt_ft")
            if alt >= 1500:
                acceleration_alt_flag = True
                callout(speech_queue, "ACCELERATION ALTITUDE")

