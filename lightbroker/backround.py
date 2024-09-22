import io
import requests
import threading
import _thread
import time

from abc import abstractmethod, ABC


class BackgroundThread(threading.Thread, ABC):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def _stopped(self) -> bool:
        return self._stop_event.is_set()

    @abstractmethod
    def startup(self) -> None:
        """
        Method that is called before the thread starts.
        Initialize all necessary resources here.
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def shutdown(self) -> None:
        """
        Method that is called shortly after stop() method was called.
        Use it to clean up all resources before thread stops.
        :return: None
        """
        raise NotImplementedError()

    @abstractmethod
    def handle(self) -> None:
        """
        Method that should contain business logic of the thread.
        Will be executed in the loop until stop() method is called.
        Must not block for a long time.
        :return: None
        """
        raise NotImplementedError()

    def run(self) -> None:
        """
        This method will be executed in a separate thread
        when start() method is called.
        :return: None
        """
        self.startup()
        while not self._stopped():
            self.handle()
        self.shutdown()


class SubscriberThread(BackgroundThread):

    def __init__(self, name, environment, topic, agent_config):
        super().__init__()
        self.name = name
        self.environment = environment
        self.topic = topic
        self.agent_config = agent_config
        self.messages = []

    def startup(self) -> None:
        print(f'{self.__class__.__name__} started')

    def shutdown(self) -> None:
        print(f'{self.__class__.__name__} {self.name} stopped')

    def handle(self) -> None:
        time.sleep(self.agent_config['interval'])
        endpoint = f"{self.agent_config['base_url']}/broker/api/channels/{self.environment}/{self.topic}/get"
        message = requests.get(endpoint, params={"name": self.name}).json()
        print(self.name, message)
        

    def to_dict(self):
        data = {}
        for k, v in self.__dict__.items():
            if not callable(v) and not isinstance(v, io.TextIOWrapper):
                if isinstance(v, threading.Event):
                    data[k] = v.is_set()
                else:
                    data[k] = v
        del data["_tstate_lock"]
        return data

class BackgroundThreadFactory:
    @staticmethod
    def create(thread_type: str, kwargs: dict) -> BackgroundThread:
        if thread_type == 'subscriber':
            return SubscriberThread(**kwargs)
        raise NotImplementedError('Specified thread type is not implemented.')
