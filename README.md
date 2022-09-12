# Vertebrae

An async application framework for Python microservices.

## Get started

Start by loading your application properties into the ```Config``` object.
Next, create a server object containing ```applications``` and ```services```.
An application is an API that serves a list of routes at a specified port. A service is a standalone
Python class that contains business logic.

```python
from vertebrae.config import Config
from vertebrae.core import Server, Application

if __name__ == '__main__':
    Config.load(Config.strip(env='conf/env.yml'))
    server = Server(
        applications=[
            Application(port=8081, routes=[MyRoutes()])
        ],
        services=[
            BasicService(),
            NotifyService()
        ])
    server.run()
```

### Example: Config

A YML file full of properties gets loaded into the ```Config``` object. The mandatory schema is below, however you
can add your own custom properties to this file and reference them via ```Config.find(property)``` anywhere in your app.

```yaml
database:
  database: frequency
  user: postgres
  password: ~
  host: localhost
  port: 5432
redis:
  host: localhost
```

### Example: Service

Each service must create a logger. Optionally, they can attach a handler to the database.

```python
from vertebrae.service import Service

class BasicService(Service):
    """ General functionality for this app """

    def __init__(self):
        self.log = self.logger('basic')
        self.database = self.db()

    def get_account(self, request):
        pass
```

### Example: Route

A route class must contain a ```routes``` function which returns a list of ```Route``` objects.
These represent your API handlers. Note how services can be engaged throughout your application.

```python
from vertebrae.core import Route
from vertebrae.service import Service

class UniversalRoutes:

    def routes(self) -> [Route]:
        return [
            Route(method='GET', route='/account', handle=self._get_account)
        ]

    async def _get_account(self, request: web.Request) -> web.json_response:
        resp = await Service.service('basic').get_account(request)
        return web.json_response(resp)
```