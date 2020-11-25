import requests
from lib.utils import get_parts
from random import random
import math
from .supply_chain_url import supply_chain_url


def make_order(teamID, demand):
    # Makes an order for widget parts from the supply chain service
    parts = get_parts()

    # order some quantity of all parts to make widgets
    order = {"parts": []}
    for p in parts:
        order["parts"].append({
            "partUuid": p["uuid"],
            "quantity": p["requiredForWidget"] * demand
        })

    # Order the parts!
    res = requests.post(supply_chain_url + "/teams/" + teamID + "/orders",
                        json=order)

    print("Order made!")
    return res.json()
