![Vertebrae](https://user-images.githubusercontent.com/49954156/198859134-4f6d1c8f-a874-437f-bb75-2aa16e59f1f3.svg)

# Vertebrae

An application framework for building async Python micro services. 

Vertebrae is a security-focused, all purpose backbone for any Python API. It focuses on one core principle: reducing the lines of code in your application will enable you to write more consistent, more secure code.

> The rule of thumb is that every 1,000 lines of code has 15+ unknown bugs inside. The less code you have, the more stable and secure you can make it. 

Vertebrae helps reduce clutter by supplying three core components:

1. Routes: API handlers that supply stubs for accepting input via REST.
2. Databases: Async connection pooling to popular databases of each primary type: relational, file and cache.
3. Services: Connective tissue that creates an internal mesh network for your code.

## Install

```bash
pip install vertebrae
```

Read our [Vertebrae Framework introduction](https://feed.prelude.org/p/vertebrae) for a walk through.

## Quick start

Copy the [sample](sample) application and use it as a template for your own projects.

### How it works

Create a Vertebrae Server and attach Applications (APIs) to it with defined Vertebrae Routes:

```python
from app.routes.core_routes import CoreRoutes
from app.services.chat import ChatService
from vertebrae.config import Config
from vertebrae.core import Server, Application


if __name__ == '__main__':
    Config.load(Config.strip(env='conf/env.yml'))
    server = Server(
        applications=[
            Application(port=8079, routes=[CoreRoutes()]),
        ],
        services=[
            ChatService(name='chat')
        ])
    server.run()
```

Next, add route classes to accept API requests:

```python
from aiohttp import web

from app.authentication import allowed
from vertebrae.core import Route
from vertebrae.service import Service


class CoreRoutes:

    def routes(self) -> [Route]:
        return [
            Route(method='GET', route='/chat', handle=self._get_messages),
            Route(method='POST', route='/chat', handle=self._save_message),
        ]

    @allowed
    async def _get_messages(self, data: dict) -> web.json_response:
        messages = await Service.find('chat').get_msgs()
        return web.json_response(messages)

    @allowed
    async def _save_message(self, data: dict) -> web.Response:
        await Service.find('chat').save_msg(msg=data.get('text'))
        return web.Response(status=200, text='Message saved!')
```

Finally, add service classes that contain your business logic:

```python
from vertebrae.service import Service


class ChatService(Service):
    """ Talk through a Redis queue """

    def __init__(self, name):
        super().__init__(name)
        self.cache = self.db('cache')

    async def save_msg(self, msg: str) -> None:
        """ Save a message to the Redis queue """
        self.log.debug('Saving new message')
        await self.cache.set('voicemail', msg)

    async def get_msgs(self) -> [str]:
        """ Retrieve a message file the Redis queue """
        self.log.debug(f'Retrieving messages')
        messages = await self.cache.get_del('voicemail')
        return messages

```

## Advanced

### Vertebrae Core

The core module (vertebrae.core) contains the Server and Application classes, which are required to start any app
backed by this framework. Additionally, the core module contains the following functions:

- ```create_logger(name)```: use this to create a logger instance from anywhere in your own application. Note that Vertebrae services have default loggers already.
- ```strip_request(request)```: strip data off API request objects regardless of which method (GET/POST/PUT/DELETE) was called.

Here is an example that uses both. 

Imagine you have an API route that looks like this:

```python
def routes(self) -> [Route]:
    return [Route(method='POST', route='/account', handle=self._post_account)]
        
@allowed
async def _post_account(self, data: dict):
    pass
```

You can create the following ```allowed``` decorator to add authentication to this API route. In this case, we are checking if the token in the header 
matches the token in the Config module. Any data passed in the request (POST data, query parameters, etc) is passed into the handler via the ```data``` parameter. Otherwise, a 403 is returned to the caller.

```python
from functools import wraps
from aiohttp import web

from vertebrae.config import Config
from vertebrae.core import create_log, strip_request

log = create_log('api')

def allowed(func):
    @wraps(func)
    async def helper(*args, **params):
        if args[1].headers.get('token') != Config.find('token'):
            log.error('[API] Unauthorized request')
            return web.Response(status=403)

        params['data'] = await strip_request(request=args[1])
        return await func(args[0], **params)
    return helper
```

### Databases

Vertebrae supports the following databases, which are accessible from any service class:

- relational (Postgres)
- cache (Redis)
- directory (local file system)
- s3 (AWS S3 service)

To enable any, ensure your Config module is injected with the appropriate connection details. 

> Note that S3 requires a standard ~/.aws/credentials file to be accessible as well. 

Here is a complete listing:

```yaml
postgres:
  database: frequency
  user: postgres
  password: ~
  host: localhost
  port: 5432
redis:
  host: localhost
directory: /home/ubuntu
aws:
  region: us-west-1
```

### Detect 

Prelude is beta testing a new continuous security testing service called Detect. This service is currently configured
inside Vertebrae as an option - however it is not enabled (nor is it possible to enable at this time). A future version
of this framework will make Detect available.
