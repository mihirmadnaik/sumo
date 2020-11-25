import random

ins = [
    "utd_in_1",
    "utd_in_2",
    "9971799#2",
    "10000547#0",
    "in_6",
    "9958219#0",
    "-145893150#13",
]
outs = [
    "543181781#6",
    "out_1",
    "15199860#0",
    "-9988553#0",
    "-145893150#0",
    "out_4",
    "out_6",
    "545113561#4",
]


def generate_traffic(step):
    trip = [random.choice(ins), random.choice(outs)]
    trip_name = "trip" + str(step)
    vehicle_name = "_veh" + str(step)
    return trip_name, vehicle_name, trip
