from lib.utils import determine_inventory_availability_for_widgets, determine_inventory_availability_for_later, get_parts
from flask import Flask, jsonify, request
import os
import requests
from iotery_python_server_sdk import Iotery
from lib.supply_chain_url import supply_chain_url
from lib.make_order import make_order

print(supply_chain_url)

app = Flask(__name__)
##PORT = os.getenv("PORT")

##if PORT == None:
PORT = 5000

# Replace these with your own Iotery teams uuids
iotery = Iotery(
    "ZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnpkV0lpT2lKbU0yUm1NamxsTUMxbU16QXdMVEV4WldFdE9XUm1NQzFrTWpnek5qRXdOall6WldNaUxDSnBZWFFpT2pFMU9UazJPVGsyTURBc0ltVjRjQ0k2TkRjMU5UUTFPVFl3TUgwLnJ0aTJEUDROaUdaQU9waTdOeXI3T2kzWF91bi1WbTJNVUVRejZxOVB6czg="
)
vehicle_1_device_uuid = "76986a42-09c5-11eb-9df0-d283610663ec"
coordinator_device_uuid = "52f7ff6c-09c5-11eb-9df0-d283610663ec"
dispatch_vehicle_command_uuid = "fc81668a-09c5-11eb-9df0-d283610663ec"

traffic_light_device_uuid = "2e910367-189e-11eb-9df0-d283610663ec"
control_light_command_uuid = "d3eeff51-189e-11eb-9df0-d283610663ec"
##total_vehicles_dispatched = 0


# Coordinator beacon route for Webhook
@app.route("/teams/<teamID>/coordinator", methods=["POST"])
def receive_coordinator_data(teamID):

    # Get the body from the Iotery Webhook reported from the embedded domain
    body = request.json
    webhook_device_uuid = body["metadata"]["deviceUuid"]

    if webhook_device_uuid == coordinator_device_uuid:

        # Get up to date information from the supply chain system
        info = requests.get(supply_chain_url + "/teams/" + teamID +
                            "/info").json()
        widget_demand = info["demand"]
        vehicle_1_dispatched = body["in"]["packets"][0]["data"][
            "vehicle_1_dispatched"]

        # Determine if an order is ready for delivery or if there will be
        can_fulfill_now, number_to_fulfill_now = determine_inventory_availability_for_widgets(
            info["inventory"])

        can_fulfill_later, number_to_fulfill_later = determine_inventory_availability_for_later(
            info["inventory"])

        # Don't have enough widgets to fulfill an on-demand order?  Then we need to make an order for parts!
        if number_to_fulfill_now < widget_demand or (
                can_fulfill_now == False and can_fulfill_later == False):
            make_order(teamID, widget_demand)
            print("Order made before dispatch")

        # If there is demand, and the vehicle is available to be dispached, send the command
        if widget_demand > 0 \
                and vehicle_1_dispatched == 0 \
                and can_fulfill_now:

            print("\nTesting Testing\n")
            # if the coordinator receives a demand request from supply chain, and a vehicle has not already been dispatched to address it, then command a vehicle to go!
            res = iotery.createDeviceCommandInstance(
                deviceUuid=coordinator_device_uuid,
                data={"commandTypeUuid": dispatch_vehicle_command_uuid})
            ##total_vehicles_dispatched += 1
            if info["inventory"]:
                for part in info["inventory"]:
                    if part["name"] == "HTC core":
                        if part["availability"]["now"] - info["demand"] < 25:
                            #make_order(teamID, 25)
                            make_order(teamID, 25-(part["availability"]["now"] - info["demand"]) )
                            print("Order made after dispatch")

            # once the command for vehicle dispatch is created, light control command is also triggered to make sure the vehicle encounters zero red lights
            res = iotery.createDeviceCommandInstance(
                deviceUuid=traffic_light_device_uuid,
                data={"commandTypeUuid": control_light_command_uuid})

    # reply to Iotery that we got everything ok
    return jsonify({"status": "ok"})


# Vehicle Route for Webhook
@app.route("/teams/<teamID>/vehicles", methods=["POST"])
def process_vehicle_data(teamID):
    body = request.json
    webhook_device_uuid = body["metadata"]["deviceUuid"]
    print("post recieved")

    # Make sure that it is the device we want
    if webhook_device_uuid == vehicle_1_device_uuid:

        webhook_data_vehicle_id = body["in"]["packets"][0]["data"][
            "vehicle_id"]

        # Get information on demand
        info = requests.get(supply_chain_url + "/teams/" + teamID +
                            "/info").json()
        widget_demand = info["demand"]

        can_fulfill_now, number_to_fulfill_now = determine_inventory_availability_for_widgets(
            info["inventory"])

        # If we can fulfill, then do it
        if can_fulfill_now:
            res = requests.post(supply_chain_url + "/teams/" + teamID +
                                "/fulfill",
                                json={
                                    "unitsFulfilled": widget_demand,
                                    "vehicleId": webhook_data_vehicle_id
                                })
            response = res.json()
            if "message" in response:
                # Catch any supply chain service error messages and print them
                print(response["message"])
            else:
                print("Fulfilled " + str(info["demand"]) + " widgets")

    # Tell Iotery everything is OK
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=PORT, host="0.0.0.0")
