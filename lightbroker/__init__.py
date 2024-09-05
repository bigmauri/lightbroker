import asyncio
import concurrent.futures
import json
import io
import queue
import requests
import threading
import time

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

    def __init__(self):
        super().__init__(__name__)
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
        super().__init__()
        self._setup()

    def _setup(self):
        self._ENVIRONMENT["channels"] = {}
        for ch in self._APPLICATION_CONFIGURATION["channels"]:
            if ch["environment"] not in self._ENVIRONMENT["channels"]:
                self._ENVIRONMENT["channels"][ch["environment"]] = {}
            if ch["topic"] not in self._ENVIRONMENT["channels"][ch["environment"]]:
                self._ENVIRONMENT["channels"][ch["environment"]][ch["topic"]] = {}
                self._ENVIRONMENT["channels"][ch["environment"]][ch["topic"]]["default"] = queue.LifoQueue(self._APPLICATION_CONFIGURATION["__meta__"]["server"]["default_queue_size"])
        for subscriber in self._APPLICATION_CONFIGURATION["subscribers"]:
            qs = [d for d in self._APPLICATION_CONFIGURATION["channels"] if d["environment"] == subscriber["environment"] and d["topic"] == subscriber["topic"]].pop()
            self._ENVIRONMENT["channels"][subscriber["environment"]][subscriber["topic"]][subscriber["name"]] = queue.LifoQueue(qs["queue_size"])


class AgentApplication(Application):

    def __init__(self):
        super().__init__()
        self._setup()

    def _setup(self):
        self._ENVIRONMENT["subscribers"] = {}
        for sub in self._APPLICATION_CONFIGURATION["subscribers"]:
            sub["agent_config"] = self._APPLICATION_CONFIGURATION["__meta__"]["agent"]
            s = BackgroundThreadFactory.create('subscriber', sub)
            self._ENVIRONMENT["subscribers"][f"{sub["name"]}-{id(s)}"] = s
            s.start()

    # def _sync(self):
    #     for sub in self._ENVIRONMENT["subscribers"].values():
    #         sub.start()

