import os
from pathlib import Path

import aiofiles

from vertebrae.config import Config


class Directory:

    def __init__(self):
        self.name = None

    async def connect(self) -> None:
        """ Construct a local file system """
        self.name = Config.find('directory', os.path.join(str(Path.home()), '.vertebrae'))
        if not os.path.exists(self.name):
            os.makedirs(self.name)

    async def read(self, filename: str):
        async with aiofiles.open(f'{self.name}/{filename}', mode='r') as f:
            return await f.read()

    async def write(self, filename: str, contents: str):
        async with aiofiles.open(f'{self.name}/{filename}', mode='w') as outfile:
            await outfile.write(contents)

    async def delete(self, filename: str):
        os.remove(f'{self.name}/{filename}')
