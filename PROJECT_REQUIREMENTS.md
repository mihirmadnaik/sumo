# SYSE6301 Project

The project write up can be found [here](https://docs.google.com/document/d/1KXryRDfHmPh8N9lsGOwFi8HcBOLJGGFKHjxYrk0wzSg/edit?usp=sharing).

To view the dashboard to keep track of your metrics, visit https://supply-chain-system.netlify.com/teams/your-team-id (replacing `your-team-id` with your provided `Team ID` from your team's Iotery account).

## Supply Chain (Ordering) System Dashboard API

There are a number of different APIs that will allow your value added systems to communicate with the ordering system to provide full automation.

You should consider using [Postman](https://getpostman.com) to try out the APIs before implementing them in your VAS architecture.

#### Example python code to interact with the API.

Here is a helpful tidbit of code (that you did in your homework!) that will help show how you can write your python code in your VAS to interact with the supply chain system API.

Example `GET` operation:

```python
import requests

TEAM_ID = "1234"
res = requests.get("https://supply-chain-system.herokuapp.com/teams/" + TEAM_ID + "/info")

data = res.json()

print(data)

```

Example `POST` operation:

```python
import requests

TEAM_ID = "1234"
order_data = {"my": "order data"}
res = requests.get("https://supply-chain-system.herokuapp.com/teams/" + TEAM_ID + "/orders", headers={"Content-Type":"application/json"} json=order_data)

data = res.json()

print(data)

```

#### Getting the Ordering System Information

To get the ordering system information for your run, simply do a RESTful `GET` in one of your value added systems:

```
GET https://supply-chain-system.herokuapp.com/teams/your-team-id/info
```

and will return:

```json
{
    "inventory": [
        {
            "uuid": "44a39e2a-d71d-11e9-83b2-2ad4acdd5304",
            "name": "Bakralite jumper plug",
            "timeToManufacture": 0,
            "throughput": 30,
            "reliability": 92,
            "requiredForWidget": 5,
            "cost": 87,
            "currentBuildableWidgets": 40,
            "totalCost": 17400,
            "availability": {
                "now": 100,
                "later": 0
            }
        },
        ...
    ],
    "orders": [
        {
            "uuid": "8460efb7-696d-430b-98f0-0d1d1bd74287",
            "team": "BJ",
            "availableAt": 1569082281,
            "cost": 12460,
            "placedAt": 1569082281,
            "parts": [
                {
                    "uuid": "7e805d61-b480-4b26-bbda-9c2bf42bcc4f",
                    "quantity": 50,
                    "quantityUsed": 0,
                    "availableAt": 1569082281,
                    "part": {
                        "uuid": "44a39e2a-d71d-11e9-83b2-2ad4acdd5304",
                        "name": "Bakralite jumper plug",
                        "timeToManufacture": 0,
                        "throughput": 30,
                        "reliability": 92,
                        "requiredForWidget": 5,
                        "cost": 87
                    }
                },
               ...
            ]
        },
        ...
    ],
    "demand": 35,
    "fulfilled": {
        "totalUnitsFulfilled": 20,
        "fulfilled": [
            {
                "uuid": "3474d7b8-dc8b-11e9-83b2-2ad4acdd5304",
                "unitsFulfilled": 5,
                "timestamp": 1569082605
            },
           ...
        ]
    },
    "fleetFuelEconomy": 3.4,
    "dataUsage": {
        "dataUsed": 7.904,
        "unit": "kB"
    },
    "numberOfVehicles": 1
}
```

### Getting Information about all the parts

To get information about the parts of the system:

```
GET https://supply-chain-system.herokuapp.com/parts
```

and will return:

```json
[
    {
        "uuid": "14a36ad6-d71d-11e9-83b2-2ad4acdd5304",
        "name": "CRJ200 Gravitometer",
        "timeToManufacture": 20,
        "throughput": 10,
        "reliability": 98,
        "requiredForWidget": 2,
        "cost": 20
    },
    {
        "uuid": "24a37ddc-d71d-11e9-83b2-2ad4acdd5304",
        "name": "Core 2 VX squaredrive",
        "timeToManufacture": 10,
        "throughput": 100,
        "reliability": 92,
        "requiredForWidget": 1,
        "cost": 45
    },
    ...
]
```

### Placing an Order

To place an order, make sure to include all the parts you need:

```
POST https://supply-chain-system.herokuapp.com/teams/your-team-id/orders

{
    "parts": [
        {
        	"name": "CRJ200 Gravitometer",
            "partUuid": "14a36ad6-d71d-11e9-83b2-2ad4acdd5304",
            "quantity": 20,
            "requiredForWidget":2
        },
        {
        	"name": "Core 2 VX squaredrive",
            "partUuid": "24a37ddc-d71d-11e9-83b2-2ad4acdd5304",
            "quantity": 10,
            "requiredForWidget":1
        },
        ...
}
```

which will return

```
{
    "uuid": "f7f5d4bd-d6ed-4bfb-a9fc-fd565c1aad62",
    "team": "your-team-id",
    "availableAt": 1569268630,
    "cost": 12460,
    "placedAt": 1569268630,
    "parts": [
        {
            "uuid": "b0f5ec67-fdf3-4ec3-8768-6ca6ebec6098",
            "quantity": 10,
            "quantityUsed": 0,
            "availableAt": 1569268630,
            "part": {
                "uuid": "34a38eee-d71d-11e9-83b2-2ad4acdd5304",
                "name": "HTC core",
                "timeToManufacture": 0,
                "throughput": 1,
                "reliability": 92,
                "requiredForWidget": 1,
                "cost": 39
            }
        },
        {
            "uuid": "806debd5-50b8-4297-9707-7d110ca8f3de",
            "quantity": 20,
            "quantityUsed": 0,
            "availableAt": 1569268630,
            "part": {
                "uuid": "14a36ad6-d71d-11e9-83b2-2ad4acdd5304",
                "name": "CRJ200 Gravitometer",
                "timeToManufacture": 0,
                "throughput": 10,
                "reliability": 98,
                "requiredForWidget": 2,
                "cost": 20
            }
        },
        ...
    ]
}
```

### Marking an order fulfilled

When your delivery vehicle makes its final stop at the delivery location, your vehicle should notify a VAS through Iotery that it has arrived and is unloading (fulfilling) the widget demand:

```
POST https://supply-chain-system.herokuapp.com/teams/your-team-id/fulfill

{
	"unitsFulfilled": 5,
	"vehicleId": "deliveryVehicle1"
}

```

and will get a response of

```json
[
    {
        "uuid": "44a39e2a-d71d-11e9-83b2-2ad4acdd5304",
        "name": "Bakralite jumper plug",
        "timeToManufacture": 0,
        "throughput": 30,
        "reliability": 92,
        "requiredForWidget": 5,
        "cost": 87,
        "currentBuildableWidgets": 30,
        "totalCost": 13050,
        "availability": {
            "now": 50,
            "later": 0
        }
    },
    ...
]
```

### Staying Compliant

In order to maintain compliance, your system systems must report fleet vehicle fuel economy. This can be accomplished by creating a webhook in your team's Iotery dashboard [https://iotery.io/webhooks](https://iotery.io/webhooks). Create a `POST` webhook by selecting the `Data Post` Action type. In the `URL` field, enter: the URL `https://supply-chain-system.herokuapp.com/teams/your-team-id/fuel-economy`. Once this is set, simply add a data type called `MPG` (as the `ENUM`) to your vehicle device type, and whenever you report `mpg` as a data element in a data post, Iotery will automatically notify the ordering system of the fuel economy and track it along with your other system metrics.

Doing this will also allow you to stay compliant by reporting your data usage.
