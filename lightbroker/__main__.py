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
arguments = parser.parse_args()

#############################################################################
# BOOTSTRAP initialization of the VCS instance  #############################
#############################################################################
server, agent = None, None

if arguments.server and arguments.agent:
    Exception("That's not allowed! Please run with '--server' or '--agent' only.")

if arguments.server:

    server = ServerApplication()

    @server.route("/api/channels")
    def channels():
        return server.to_json(server.environment, 200)

    @server.route("/api/channels/<environment>/<topic>/publish")
    def publish(environment, topic):
        for sub, ch in server.environment["channels"][environment][topic].items():
            ch.put(request.args.get("message"))
        return server.to_json({"status": "OK", "message": "Message publish successfully"}, 200)

    @server.route("/api/channels/<environment>/<topic>/get")
    def get(environment, topic):
        subscriber_name = request.args.get("name")
        try:
            message = f"{server.environment["channels"][environment][topic][subscriber_name].get(block=False)}"
        except queue.Empty:
            message = None
        return server.to_json({"status": "OK", "message": message}, 200)

    server.run(port=5555)

if arguments.agent:

    agent = AgentApplication()

    @agent.route("/api/subscribers")
    def subscribers():
        return agent.to_json(agent.environment, 200)

    @agent.route("/api/subscribers/stop")
    def stop():
        for key, value in agent.environment["subscribers"].items():
            value.stop()
            # if value.is_alive():
            #     value.join() # probably this is not necessary in my case, i need just to send a call 
        return agent.to_json(agent.environment, 200)

    agent.run(port=5556)
