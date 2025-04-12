import json

class BriefingPackage:
    def __init__(self, departure_airport, arrival_airport, flight_rules, v1_speed, vr_speed, v2_speed, safe_altitude, task_allocation):
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.flight_rules = flight_rules
        self.v1_speed = v1_speed
        self.vr_speed = vr_speed
        self.v2_speed = v2_speed
        self.safe_altitude = safe_altitude
        self.task_allocation = task_allocation

    def __repr__(self):
        return (f"BriefingPackage(departure_airport={self.departure_airport}, arrival_airport={self.arrival_airport}, "
                f"flight_rules={self.flight_rules}, v1_speed={self.v1_speed}, vr_speed={self.vr_speed}, "
                f"v2_speed={self.v2_speed}, safe_altitude={self.safe_altitude}, task_allocation={self.task_allocation})")

def unpack_briefing_package(byte_data):
    data = json.loads(byte_data.decode('utf-8'))
    task_allocation = {
        "Aviate": data['aviate'].split(': ')[1],
        "Navigate": data['navigate'].split(': ')[1],
        "Communicate": data['communicate'].split(': ')[1]
    }
    briefing_package = BriefingPackage(
        departure_airport=data['departure_airport'],
        arrival_airport=data['arrival_airport'],
        flight_rules=data['flight_rules'],
        v1_speed=data['v1_speed'],
        vr_speed=data['vr_speed'],
        v2_speed=data['v2_speed'],
        safe_altitude=data['safe_altitude'],
        task_allocation=task_allocation
    )
    return briefing_package