import os
from pathlib import Path

import aiofiles

from vertebrae.config import Config


class Directory:

    def __init__(self, log):
        self.log = log
        self.name = None

    async def connect(self) -> None:
        """ Construct a local file system """
        self.name = Config.find('directory', os.path.join(str(Path.home()), '.vertebrae'))
        Path(self.name).mkdir(parents=True, exist_ok=True)

    @staticmethod
    async def read(filename: str):
        async with aiofiles.open(filename, mode='r') as f:
            return await f.read()

    @staticmethod
    async def walk(bucket: str, prefix='*'):
        for path in Path(bucket).glob(f'{prefix}*'):
            async with aiofiles.open(path, mode='r') as _:
                yield os.path.basename(path)

    @staticmethod
    async def write(filename: str, contents: str):
        directory = Path(filename).parent
        Path(directory).mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(filename, mode='w') as outfile:
            await outfile.write(contents)

    @staticmethod
    async def delete(filename: str):
        os.remove(filename)
