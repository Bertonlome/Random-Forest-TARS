import ingescape as igs
import sys


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Echo(metaclass=Singleton):
    def __init__(self):
        # inputs
        self.briefing_package_i = None
        self.control_perception_i = None

        # outputs
        self.status_o = None
        self.level_of_automation_o = None
        self.elevator_o = None
        self.aileron_o = None
        self.rudder_o = None
        self.throttle_o = None
        self.flaps_o = None
        self.gear_o = None
        self.brake_o = None

    @property
    def status_o(self):
        return self.status_o

    @status_o.setter
    def status_o(self, value):
        self._status_o = value
        if self._status_o is not None:
            igs.output_set_string("status", self._status_o)

    @property
    def level_of_automation_o(self):
        return self.level_of_automation_o
    
    @level_of_automation_o.setter
    def level_of_automation_o(self, value):
        self._level_of_automation_o = value
        if self._level_of_automation_o is not None:
            igs.output_set_string("levelOfAutomation", self._level_of_automation_o)

    @property
    def elevator_o(self):
        return self.elevator_o
    
    @elevator_o.setter
    def elevator_o(self, value):
        self._elevator_o = value
        if self._elevator_o is not None:
            igs.output_set_double("elevator", self._elevator_o)

    @property
    def aileron_o(self):
        return self.aileron_o
    
    @aileron_o.setter
    def aileron_o(self, value):
        self._aileron_o = value
        if self._aileron_o is not None:
            igs.output_set_double("aileron", self._aileron_o)
            
    @property
    def rudder_o(self):
        return self.rudder_o

    @rudder_o.setter
    def rudder_o(self, value):
        self._rudder_o = value
        if self._rudder_o is not None:
            igs.output_set_double("rudder", self._rudder_o)

    @property
    def throttle_o(self):
        return self.throttle_o

    @throttle_o.setter
    def throttle_o(self, value):
        self._throttle_o = value
        if self._throttle_o is not None:
            igs.output_set_double("throttle", self._throttle_o)

    @property
    def flaps_o(self):
        return self.flaps_o

    @flaps_o.setter
    def flaps_o(self, value):
        self._flaps_o = value
        if self._flaps_o is not None:
            igs.output_set_int("flaps", self._flaps_o)

    @property
    def gear_o(self):
        return self.gear_o

    @gear_o.setter
    def gear_o(self, value):
        self._gear_o = value
        if self._gear_o is not None:
            igs.output_set_impulsion("gear")

    @property
    def brake_o(self):
        return self.brake_o

    @brake_o.setter
    def brake_o(self, value):
        self._brake_o = value
        if self._brake_o is not None:
            igs.output_set_impulsion("brake")

    # services
    def receive_values(self, sender_agent_name, sender_agent_uuid, boolV, integer, double, string, data, token, my_data):
        igs.info(f"Service receive_values called by {sender_agent_name} ({sender_agent_uuid}) with argument_list {boolV, integer, double, string, data} and token '{token}''")

    def send_values(self, sender_agent_name, sender_agent_uuid, token, my_data):
        print(f"Service send_values called by {sender_agent_name} ({sender_agent_uuid}), token '{token}' sending values : {self.on_off_o, self.integerO, self.doubleO, self.stringO, self.dataO}")
        igs.info(sender_agent_uuid, "receive_values", (self.on_off_o, self.integerO, self.doubleO, self.stringO, self.dataO), token)