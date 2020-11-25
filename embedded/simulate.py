import lib.import_sumo

import traci
import traci.constants as tc
from time import sleep, time
import random
from generate_traffic import generate_traffic
import os

from iotery_embedded_python_sdk import Iotery


def is_vehicle_on_network(id):
    # Use this helper function to check if a vehicle is on the network
    return id in traci.vehicle.getIDList()


# Set up and start SUMO
sumoBinary = "sumo-gui"
sumoCmd = [
    sumoBinary,
    "-c",
    "utd.sumocfg",
    "--start",
    "--time-to-teleport",
    "100000000",
]
traci.start(sumoCmd)
step = 0
fleetFuelEconomy = 0
totalFuelConsumed = 0
distance = 0
milesPerGallon = 0
numberOfVehiclesDispatched = 0
sumFuelEconomy = 0

# TEAM_ID = "your-team-id"  # team ID found on the dashboard: https://iotery.io/system
TEAM_ID = "f3df29e0-f300-11ea-9df0-d283610663ec"

# # Sample Widget Delivery Vehicle with a trip (a trip is an "auto-route")
# traci.route.add("delivery_trip_1", ["GATE_1_IN", "DELIVERY_DROP"])
# traci.vehicle.add("delivery_veh_1", "delivery_trip_1")
# traci.vehicle.setColor("delivery_veh_1", [255, 0, 0])

# # You can also add a delivery vehicle with a specific route:
# traci.route.add("delivery_route_1", ["GATE_1_IN", "-gneE5", "-gneE4"])
# traci.vehicle.add("delivery_veh_2", "delivery_route_1")
# traci.vehicle.setColor("delivery_veh_2", [255, 0, 0])

# You will need to create the appropriate devices in your team's Iotery account.
# Each device should correspond to a vehicle (or a traffic light)
# Remember, you can only use the embedded device SDK in the embedded domain!
vehicle_credentials = [{"key": "DVEH1", "serial": "DVEH1", "secret": "DVEH1"}]

# Delivery Vehicle 1
delivery_vehicle_1_connector = Iotery()
delivery_vehicle_1_token = delivery_vehicle_1_connector.getDeviceTokenBasic(
    data={
        "key": vehicle_credentials[0]["key"],
        "serial": vehicle_credentials[0]["serial"],
        "secret": vehicle_credentials[0]["secret"],
        "teamUuid": TEAM_ID
    })
delivery_vehicle_1_connector.set_token(delivery_vehicle_1_token["token"])
delivery_vehicle_1 = delivery_vehicle_1_connector.getMe()

# Save the name of the vehicle to be used as SUMO vehicle name
dv1_serial = delivery_vehicle_1["serial"]

###################################################################################################################################################################
# Helpful hint: include a dispatch controller device (a general sensor that sits at your manufacturing plant) and keeps tabs on your devices that are at your HQ at a given time.
# This can be used communicate with your VAS' (by posting data in-the-loop) and using webhooks to post to your VAS
infrastructure_coordinator = {
    "key": "COORDINATOR",
    "serial": "COORDINATOR",
    "secret": "COORDINATOR"
}
coordinator_connector = Iotery()
c_token = coordinator_connector.getDeviceTokenBasic(
    data={
        "key": infrastructure_coordinator["key"],
        "serial": infrastructure_coordinator["serial"],
        "secret": infrastructure_coordinator["secret"],
        "teamUuid": TEAM_ID
    })
coordinator_connector.set_token(c_token["token"])
coordinator = coordinator_connector.getMe()

###################################################################################################################################################################
# Traffic Light 1 (bottom traffic light at the Campell and Waterview intersection; TL ID =81984600)
traffic_light_1_credentials = [{
    "key": "TL_1",
    "serial": "81984600",
    "secret": "TL_1"
}]

traffic_light_1_connector = Iotery()
traffic_light_1_token = traffic_light_1_connector.getDeviceTokenBasic(
    data={
        "key": traffic_light_1_credentials[0]["key"],
        "serial": traffic_light_1_credentials[0]["serial"],
        "secret": traffic_light_1_credentials[0]["secret"],
        "teamUuid": TEAM_ID
    })
traffic_light_1_connector.set_token(traffic_light_1_token["token"])
traffic_light_1 = traffic_light_1_connector.getMe()

###################################################################################################################################################################


def post_coordinator_data(data):
    # Create a coordinator data post helper function to clean up simulation loop code
    return coordinator_connector.postData(deviceUuid=coordinator["uuid"],
                                          data={
                                              "packets": [{
                                                  "deviceUuid":
                                                  coordinator["uuid"],
                                                  "timestamp":
                                                  int(time()),
                                                  "data":
                                                  data
                                              }]
                                          })


def post_vehicle_data(data):
    # Create a coordinator data post helper function to clean up simulation loop code
    return delivery_vehicle_1_connector.postData(
        deviceUuid=delivery_vehicle_1["uuid"],
        data={
            "packets": [{
                "deviceUuid": delivery_vehicle_1["uuid"],
                "data": data
            }]
        })


def post_traffic_light_data(data):
    # Create a traffic light data post helper function to clean up simulation loop code
    return traffic_light_1_connector.postData(
        deviceUuid=traffic_light_1["uuid"],
        data={
            "packets": [{
                "deviceUuid": traffic_light_1["uuid"],
                "data": data
            }]
        })


# To control a traffic light, you will need to find its ID using netedit.  For example, the last intersection traffic light that a vehicle will approach coming from the manufacturing HQ would be 81742684:
# This will set the phase of all lights (going clockwise around the intersection) to red.
#traci.trafficlight.setRedYellowGreenState("81742684", "rrrrrrrr")

# Each "r" corresponds to a light for a lane.  It may look like there are only 8 total lanes in the intersection (don't forget the turn lanes) controlled lights in the intersection!
# So, to make only the northern most lights green, the string would be "rrrrgggg"
# More information: http://sumo.sourceforge.net/pydoc/traci._trafficlight.html

vehicle_1_dispatched = 0
while step < 10000:

    # Only send to the coordinator every 100 simulation steps
    if step % 100 == 0:
        coordinator_data = post_coordinator_data({
            "beacon":
            step,
            "vehicle_1_dispatched":
            vehicle_1_dispatched
        })
        command_instances = coordinator_data["unexecutedCommands"]["device"]

        # Process command instances as they come in for a single vehicle
        if len(command_instances) > 0:
            for command in command_instances:
                if (command["commandTypeEnum"] == "DISPATCH_VEHICLE"):
                    command_uuid = command["uuid"]
                    # Set the command executed (treating this as just a "read receipt" at this point)
                    coordinator_connector.setCommandInstanceAsExecuted(
                        commandInstanceUuid=command_uuid,
                        data={"timestamp": int(time())})

                    # Make sure the vehicle is not currently on a run when a command comes in.
                    if vehicle_1_dispatched == 0:
                        # Add the route (letting SUMO calculate the path for us)
                        traci.route.add(command_uuid,
                                        ["GATE_1_IN", "DELIVERY_DROP"])

                        # Set vehicle as dispatched
                        vehicle_1_dispatched = 1

                        # Put the vehicle on the network and go
                        traci.vehicle.add(dv1_serial, command_uuid)
                        traci.vehicle.setColor(dv1_serial, [255, 0, 0])
                        print("Dispatched Vehicle!")
                        print("\ndispatch_step = " + str(step))

                        # Read traffic control commands and execute them

                        traffic_light_data = post_traffic_light_data({
                            "beacon":
                            step,
                            "vehicle_1_dispatched":
                            vehicle_1_dispatched
                        })
                        TL_command_instances = traffic_light_data[
                            "unexecutedCommands"]["device"]

                        if len(TL_command_instances) > 0:
                            for command in TL_command_instances:
                                if (command["commandTypeEnum"] ==
                                        "CONTROL_LIGHT"):
                                    command_uuid = command["uuid"]
                                    # Set the command executed (treating this as just a "read receipt" at this point)
                                    traffic_light_1_connector.setCommandInstanceAsExecuted(
                                        commandInstanceUuid=command_uuid,
                                        data={"timestamp": int(time())})

                                    traci.trafficlight.setRedYellowGreenState(
                                        "81742759", "rrrggrrr"
                                    )  #Top light at Coit and Waterview Intersection
                                    traci.trafficlight.setRedYellowGreenState(
                                        "81984600", "gggrrrrg"
                                    )  #Bottom light at Coit and Waterview Intersection
                                    #traci.trafficlight.setRedYellowGreenState("81742802", "gggg") #Need to figure out what is wrong with this light
                                    traci.trafficlight.setRedYellowGreenState(
                                        "5286561737", "gggggggg")
                                    traci.trafficlight.setRedYellowGreenState(
                                        "5286561736", "gggggggg")
                                    print("Traffic light control activated!")

    # To alleviate the tedium of simulation, we are not going to code to turn the vehicle around and return to home base
    if vehicle_1_dispatched == 1:
        fuelConsumption = traci.vehicle.getFuelConsumption(dv1_serial)
        if fuelConsumption > 0:
            totalFuelConsumed += fuelConsumption
            distance = traci.vehicle.getDistance(dv1_serial)
            fuelEconomy = distance / totalFuelConsumed
            milesPerGallon = fuelEconomy * 2.35
            print("Fuel Economy of current vehicle is " + str(milesPerGallon))

    if vehicle_1_dispatched == 1 and traci.vehicle.getRoadID(
            dv1_serial) == "DELIVERY_DROP" and vehicle_1_dispatched == 1:
        # Vehicle is at the drop edge, so report that data to Iotery
        print("Fuel Economy before posting " + str(milesPerGallon))
        post_vehicle_data({
            "edge_id": traci.vehicle.getRoadID(dv1_serial),
            "vehicle_id": dv1_serial,
            "mpg": milesPerGallon
        })
        # Set the "currently dispatched" flag to off
        vehicle_1_dispatched = 0
        print("Dropped off widgets!")
        numberOfVehiclesDispatched += 1
        sumFuelEconomy += milesPerGallon
        fleetFuelEconomy = sumFuelEconomy / numberOfVehiclesDispatched
        print("Fleet Fuel Economy is " + str(fleetFuelEconomy))

    # --- DO NOT MODIFY ---
    if step % 30 == 0:
        gen_trip_name, gen_vehicle, gen_trip = generate_traffic(step)
        traci.route.add(gen_trip_name, gen_trip)
        traci.vehicle.add(gen_vehicle, gen_trip_name)
        traci.vehicle.setColor(gen_vehicle, [255, 255, 153, 150])

    traci.simulationStep()
    step += 1
    sleep(0.1)
    # --- DO NOT MODIFY ---
traci.close()
