import argparse
import logging
import queue

from lightbroker import ServerApplication, AgentApplication
from flask import request


#############################################################################
# PARSER configuration in order to be ready to execute as a python module  ##
#############################################################################
parser = argparse.ArgumentParser(description="Broker pub/sub application")
parser.add_argument(
    "--server",
    action="store_true",
    help="Get broker role"
)
parser.add_argument(
    "--agent",
    action="store_true",
    help="Get broker role"
)
parser.add_argument(
    "--agent-server",
        type=str,
        help="Agent's server url"
)
arguments = parser.parse_args()

#############################################################################
# BOOTSTRAP initialization of the VCS instance  #############################
#############################################################################
server, agent = None, None

if arguments.server and arguments.agent:
    Exception("That's not allowed! Please run with '--server' or '--agent' only.")

if arguments.server:

    server = ServerApplication()

    @server.route("/broker/api/channels")
    def channels():
        return server.to_json(server.environment, 200)

    @server.route("/broker/api/channels/<environment>/<topic>/publish")
    def publish(environment, topic):
        for sub, ch in server.environment["channels"][environment][topic].items():
            ch.put(request.args.get("message"))
        return server.to_json({"status": "OK", "message": "Message publish successfully"}, 200)

    @server.route("/broker/api/channels/<environment>/<topic>/subscribe")
    def subscribe(environment, topic):
        name, size = request.args.get("name"), request.args.get("size")
        server.set_subscriber(name, environment, topic, size)
        return server.to_json({"status": "OK", "message": f"Subscription completed to the topic '{topic}' in environment '{environment}'"}, 200)

    @server.route("/broker/api/channels/<environment>/<topic>/get")
    def get(environment, topic):
        subscriber_name = request.args.get("name")
        try:
            message = f'{server.environment["channels"][environment][topic][subscriber_name].get(block=False)}'
        except queue.Empty:
            message = None
        return server.to_json({"status": "OK", "message": message}, 200)

    server.run(host="0.0.0.0", port=5555)

if arguments.agent:
    protocol, server_url = "http", arguments.agent_server
    agent = AgentApplication({
            "server_url": f"{protocol}://{server_url}:5555",
            "interval": 10
        })

    @agent.route("/agent/api/subscriptions")
    def subscriptions():
        return agent.to_json(agent.environment, 200)

    @agent.route("/agent/api/subscribe")
    def subscribe():
        name = request.args.get("name")
        environment = request.args.get("environment")
        topic = request.args.get("topic")
        agent.subscribe(name, environment, topic)
        return agent.to_json(agent.environment, 200)

    @agent.route("/agent/api/subscriptions/stop")
    def stop():
        for key, value in agent.environment["subscriptions"].items():
            value.stop()
        return agent.to_json(agent.environment, 200)

    agent.run(port=5556)
