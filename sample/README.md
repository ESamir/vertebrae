# Chatter Bot

Chatter Bot is a simple example of a Vertebrae-backed application. Use this as a template for your own projects. 

It is a simple queue system, which allows you to save messages to a queue and retrieve them later.

It includes:

- server.py: the entry point to the code
- authentication.py: protection for the API
- routes: all API route definitions
- services: all business logic
- conf/env.yml: an application-wide configuration file

## Quick start

Download this directory and follow the installation steps:

Start by installing Redis. Then install the pip requirements and start the micro service:

```bash
pip install -r requirements.txt
python server.py
```

Your new web server will start on port 8079. 

Add messages to your queue:
```bash
curl -X POST "localhost:8079/chat" -H 'Content-Type: application/json' -H "token: abc123" -d '{"text":"hi, there"}'
```

Retrieve messages from your queue:
```bash
curl -X GET "localhost:8079/chat" -H 'Content-Type: application/json' -H "token: abc123"
```
