# Supply Chain Simulation

This repository contains a basic implementation of one possible solution to the widget fulfillment problem defined in the project outline.

There are a number of (obvious) optimizations that can be made, in addition to missing one primary regulatory requirement that is critical to the winning the UTD contract. Be sure to include it!

This is just one naive architecture and implementation - you are challenged to do much better by improving this implementation or redoing with your own unique architecture.

## Setup

There are two folders:

1. `embedded` - An implementation of the embedded domain (dispatch coordinator and dispatch vehicle)
2. `cloud` - An implementation of a VAS for your operations center that communicates with the [supply chain platform](https://supply-chain-system.netlify.com/teams/team-id)

Make sure to review carefully, and create your own Iotery team and fill in the appropriate places (`uuid`s, credentials, and API key).

### Running

To run, make sure to set your `SUMO_HOME` environment variable appropriately.

In addition, make sure to set your Iotery `TEAM_ID` and `API_KEY` similar to your `SUMO_HOME`:

MacOS/Linux:

```
export TEAM_ID=your-team-id
export API_KEY=your-api-key
```

Windows:

```
setx TEAM_ID "your-team-id"
setx API_KEY "your-api-key"
```

In two different terminals for each of the `cloud` and `embedded` folders, create your virtual environments (each has it's own), install the requirements (`pip install -r requirements.txt`), and run each individually.

### Embedded

In the `embedded` folder, run `simulate.py` to start your network.

### Cloud

In the `cloud` folder, run `app.py` to start your VAS

Keep in mind, this will be running locally. For Iotery to interact with your VAS through webhooks, you will either need to deploy to heroku, or you will need to use a tool like [`ngrok`](https://ngrok.com/) and point it to your VAS locally:

```
ngrok http 5000
```

> This example is assuming your VAS is running on port 5000
