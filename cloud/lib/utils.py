import requests
import math
from .supply_chain_url import supply_chain_url

parts = None


def get_parts():
    if not (parts == None):
        # We are simply saving some time and caching the parts so we don't hit the supply service every single time we want the parts list
        return parts
    # Get the part listings from the supply chain system
    _res = requests.get(supply_chain_url + "/parts")
    return _res.json()


def get_part(part_uuid):
    # Just return a specific part (helper function)
    parts = get_parts()
    for p in parts:
        if p["uuid"] == part_uuid:
            return p

    raise "No Part Found with uuid " + part_uuid


def determine_inventory_availability_for_widgets(inventory):
    # Determines if there are enough widgets available in inventory to delivery
    # Returns two parameters: True/False, number of widgets available

    total_widgets_for_each_part = []

    # loop through all the parts in inventory
    for item in inventory:
        now = item["availability"]["now"]
        uuid = item["uuid"]

        # calculate if we have enough now
        p = get_part(uuid)
        number_of_widgets = now / p["requiredForWidget"]

        # If we have enough, shove the number of possible widgets made from that single part into an array
        if number_of_widgets >= 1:
            total_widgets_for_each_part.append(math.floor(number_of_widgets))
        else:
            total_widgets_for_each_part.append(0)

    # If no inventory at all
    if len(total_widgets_for_each_part) == 0:
        return False, 0

    # Find the smallest number of widgets than can be made form the parts we have in inventory
    number_of_widgets = min(total_widgets_for_each_part)

    if number_of_widgets > 0:
        return True, number_of_widgets

    return False, 0


def determine_inventory_availability_for_later(inventory):
    # Exact same thing as above, except it's to calculate parts available later
    total_widgets_for_each_part = []

    for item in inventory:
        later = item["availability"]["later"]
        uuid = item["uuid"]

        p = get_part(uuid)
        number_of_widgets = later / p["requiredForWidget"]

        if number_of_widgets >= 1:
            total_widgets_for_each_part.append(math.floor(number_of_widgets))
        else:
            total_widgets_for_each_part.append(0)

    # If no inventory at all
    if len(total_widgets_for_each_part) == 0:
        return False, 0

    number_of_widgets = min(total_widgets_for_each_part)

    if number_of_widgets > 0:
        return True, number_of_widgets

    return False, 0
