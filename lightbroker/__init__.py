import asyncio
import concurrent.futures
import json
import io
import queue
import requests
import threading
import time
import os

from lightbroker.backround import BackgroundThreadFactory, SubscriberThread
from flask import Flask, jsonify, request


class AppEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, queue.Queue):
            return list(obj.queue)
        if isinstance(obj, SubscriberThread):
            return obj.to_dict()
        return super().default(obj)

class Application(Flask):

    _APPLICATION_CONFIGURATION_PATH = "config.json"
    _APPLICATION_CONFIGURATION = {}
    _ENVIRONMENT = {}

    def __init__(self, name, template_folder=None, static_folder=None):
        super().__init__(name, template_folder=template_folder, static_folder=static_folder)
        self._load_configuration()

    @property
    def environment(self): return self._ENVIRONMENT

    def _load_configuration(self):
        with open(self._APPLICATION_CONFIGURATION_PATH, "r") as _config:
            self._APPLICATION_CONFIGURATION = json.load(_config)

    def to_json(self, content, code):
        return json.dumps(content, cls=AppEncoder), code, {"Content-Type": "application/json"}


class ServerApplication(Application):

    def __init__(self):
        super().__init__(__name__)
        self._setup()

    def _setup(self):
        self._ENVIRONMENT["channels"] = {}
        for ch in self._APPLICATION_CONFIGURATION["channels"]:
            if ch["environment"] not in self._ENVIRONMENT["channels"]:
                self._ENVIRONMENT["channels"][ch["environment"]] = {}
            if ch["topic"] not in self._ENVIRONMENT["channels"][ch["environment"]]:
                self._ENVIRONMENT["channels"][ch["environment"]][ch["topic"]] = {}
                self._ENVIRONMENT["channels"][ch["environment"]][ch["topic"]]["default"] = queue.LifoQueue(self._APPLICATION_CONFIGURATION["__meta__"]["server"]["default_queue_size"])

    def set_subscriber(self, name, environment, topic, size=20):
        self._ENVIRONMENT["channels"][environment][topic][name] = queue.LifoQueue(int(size))

class AgentApplication(Application):

    def __init__(self, config):
        self.__CONFIG = config
        super().__init__(
            __name__,
            template_folder=os.path.join(os.getcwd(), "templates"),
            static_folder=os.path.join(os.getcwd(), "static")
            )
        self._setup()

    def _setup(self):
        self._ENVIRONMENT["subscriptions"] = {}

    def subscribe(self, name, environment, topic):
        endpoint = f"{self.__CONFIG['server_url']}/broker/api/channels/{environment}/{topic}/subscribe"
        response = requests.get(endpoint, params={"name": name, "size": 20}).json()
        s = BackgroundThreadFactory.create('subscriber', name, environment, topic, self.__CONFIG)
        self._ENVIRONMENT["subscriptions"][f'{name}-{id(s)}'] = s
        s.start()
