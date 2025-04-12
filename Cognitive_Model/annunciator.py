import time
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