import logging

import aiopg
import aioredis

from vertebrae.config import Config


class Store:
    """ Handlers to both the cache and relational data stores used by this application """

    def __init__(self):
        self.cache = None
        self.pg_pool = None

    async def start(self) -> None:
        """ Initialize the databases """
        redis_url = Config.find('redis').get('host')
        self.cache = aioredis.from_url(url=f'redis://{redis_url}', port=6379, db=0, decode_responses=True)
        self.pg_pool = await aiopg.create_pool(f"dbname={Config.find('database')['database']} "
                                               f"user={Config.find('database')['user']} "
                                               f"password={Config.find('database')['password']} "
                                               f"host={Config.find('database')['host']} "
                                               f"port={Config.find('database')['port']} ",
                                               minsize=0, maxsize=5, timeout=10.0)
        await self.apply_schema()

    async def apply_schema(self) -> None:
        """ Ensure relational DB matches local schema """
        with open('conf/schema.sql', 'r') as sql:
            await self.execute(sql.read())

    async def execute(self, statement: str, params=(), return_id=False):
        """ Run statement retrieving either nothing or the row ID """
        try:
            async with self.pg_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(statement, params)
                    if return_id:
                        return (await cur.fetchone())[0]
        except Exception as e:
            logging.exception(e)

    async def fetch_all(self, query: str, params=()):
        """ Find all matches for a query """
        try:
            async with self.pg_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    return await cur.fetchall()
        except Exception as e:
            logging.exception(e)

    async def fetch_one(self, query, params=()):
        """ Find a single database entry """
        try:
            async with self.pg_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    return await cur.fetchone()
        except Exception as e:
            logging.error(e)
