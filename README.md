# light-broker [![GitHub tag](https://img.shields.io/github/tag/bigmauri/light-broker.svg)](https://GitHub.com/bigmauri/light-broker/tags/) [![GitHub commits](https://img.shields.io/github/commits-since/bigmauri/light-broker/v0.0.1.svg)](https://GitHub.com/bigmauri/light-broker/commit/)

___
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)


This repository contains a Python application that can be run as either a server or an agent. It uses Flask to expose RESTful APIs for managing channels and subscribers, and it implements a lightweight broker and agent system.

## Features

- **Server Mode**: 
  - Create and manage channels.
  - Publish messages to specific topics.
  - Retrieve messages from channels.

- **Agent Mode**: 
  - Manage subscribers who can consume messages from the server.
  - Start and stop subscribers.

## Requirements

- Python 3.x
- Flask

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/your-repository.git
    cd your-repository
    ```

2. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

You can run this application in either server mode or agent mode, but not both simultaneously.


### Running in Server Mode

To start the application as a server, use the `--server` flag:

```bash
python -m lightbroker --server
```

The server will start at `http://127.0.0.1:5050` with the following endpoints:

- `GET /api/channels` Returns the current channel configurations.
- `GET /api/channels/<environment>/<topic>/publish` Publishes a message to a specific channel.
  - Query Parameters
    - `message` The message to be published.
- `GET /api/channels/<environment>/<topic>/get` Retrieves a message for a specific subscriber.
  - Query Parameters
    - `name` The name of the subscriber.


### Running in Agent Mode

To start the application as a agent, use the `--agent` flag:

```bash
python -m lightbroker --agent
```

The server will start at `http://127.0.0.1:5060` with the following endpoints:

- `GET /api/subscribers` Returns the subscribers configurations.
- `GET /api/subscribers/stop` Stops all subscribers.


### Running in Agent Mode

- If you try to run with both `--server` and `--agent` flags, the application will raise an exception.

---
Enjoy your Python <3!
