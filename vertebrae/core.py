import asyncio
import logging
import os
import socket
from collections import namedtuple
from logging.handlers import WatchedFileHandler

from aiohttp import web

from vertebrae.service import Service

Route = namedtuple('Route', 'method route handle')


class Server:

    def __init__(self, services, applications):
        self.setup_logger(path=os.getenv('logfile'))
        Service.logger('vertebrae').info(
            f'{socket.gethostname()} serving {len(applications)} apps with {len(services)} services'
        )

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        for app in applications:
            self.loop.run_until_complete(app.start())
        for service in services:
            Service.enroll(service.log.name, service)

    def run(self):
        try:
            self.loop.run_until_complete(Service.initialize())
            self.loop.run_forever()
        except KeyboardInterrupt:
            logging.info('Keyboard interrupt received')

    @staticmethod
    def setup_logger(path):
        logging.basicConfig(
            level='DEBUG',
            format='%(asctime)s - %(levelname)-5s (%(name)s) %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[WatchedFileHandler(filename=path)] if path else None
        )
        for logger_name in logging.root.manager.loggerDict.keys():
            logging.getLogger(logger_name).setLevel(logging.ERROR)


class Application:

    def __init__(self, port, routes):
        self.port = port
        self.application = web.Application(client_max_size=4096)

        for collection in routes:
            for route in collection.routes():
                self.application.router.add_route(route.method, route.route, route.handle)

    async def start(self):
        runner = web.AppRunner(self.application)
        await runner.setup()
        await web.TCPSite(runner=runner, port=self.port).start()
