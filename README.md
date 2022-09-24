# Vertebrae

An application framework for building async Python microservices. Use this to add consistency between your API code bases.
You get an API, a mesh network of services, and database connection pooling.

## Install

```bash
pip install vertebrae
```

Read our Vertebrae Framework introduction for a complete tutorial.

## How it works

1. Create a Vertebrae Server and attach Applications (APIs) to it with defined Vertebrae Routes.
2. (optionally) Supply connection details to one of the available databases. Vertebrae will create async connection pools to them.
3. Convert your classes to Vertebrae Services. This creates a mesh network between them. Each service gets a handler to your databases.

## Advanced

### Vertebrae Core

The core module (vertebrae.core) contains the Server and Application classes, which are required to start any app
backed by this framework. Additionally, the core module contains the following functions:

- ```create_logger(name)```: use this to create a logger instance from anywhere in your own application. Note that Vertebrae services have default loggers already.
- ```strip_request(request)```: strip data off API request objects regardless of which method (GET/POST/PUT/DELETE) was called.

Here is an example that uses both. This decorator can be used on any API handler to verify if the token in the header 
matches the token in the Config module. Any data passed in the request (POST data, query parameters, etc) is passed 
into the handler in the ```data``` parameter.

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
        return await func(*args, **params)
    return helper
```

For completeness, here is the handler:
```python
@allowed
async def _route_handler_1(self, request: web.Request, data: dict):
    pass
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

### Client side apps

You can attach a website GUI to your Vertebrae Server by simply creating a ```client``` directory in
the root of your project containing all your static resources (css, javascript, images, etc.). The only special
directory must be a ```client/templates``` directory containing your HTML file(s).

With that in place, your HTML files can reference resources at ```/client```, such as:

```angular2html
<script src="/client/js/main.js"></script>
```

Finally, you must add Vertebrae Routes for each HTML page you want to display. 

Below is an example routes class that returns the index.html file found at ```client/templates/index.html```.

```python
from aiohttp import web
from aiohttp_jinja2 import template
from vertebrae.core import Route

class WebRoutes:

    def routes(self) -> [Route]:
        return [
            Route('GET', '/', self._get_index)
        ]

    @template('index.html')
    async def _get_index(self, request: web.Request) -> dict:
        return dict(hello='world')
```

### Detect 

Vertebrae Server includes hooks to Detect, a continuous security testing service that runs inside your own code. Detect launches a probe - or security thread - inside your application process space. The probe periodically runs tests to flush out security risks proactively.

To enable Detect, set the following environment variables before starting your Vertebrae Server:
```
os.environ['PRELUDE_ACCOUNT_ID'] = '<YOUR DETECT ACCOUNT>'
os.environ['PRELUDE_ACCOUNT_TOKEN'] = '<YOUR DETECT TOKEN>'
```

Want to run Detect in a non-Vertebrae application? Check out the [SDKs](https://github.com/preludeorg/detect-clients).
