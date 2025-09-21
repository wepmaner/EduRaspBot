import asyncio
import logging
from datetime import datetime, timedelta

import db_manager as db
import utils
from create_bot import bot, dp
from EduAPI.methods import *
from handlers import callback_query, command

import config
logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, config.log_level),
)
logger = logging.getLogger("main")
logger.info("Program start")
logging.basicConfig(level=logging.INFO)


async def cache_update():
    while True:
        logger.info("Load rasp")
        try:
            await listYear()
            utils.cache["EduAlive"] = True
        except EduDown:
            utils.cache["last_update"] += 60 if utils.cache["EduAlive"] else 2

            utils.cache["EduAlive"] = False
            logger.info("Server edu down")
            await asyncio.sleep(120)
            continue
        tasks = []
        sql = f"SELECT DISTINCT number_1, teacher FROM users;"
        pool = db.get_pool()
        async with pool.acquire() as con:
            async with con.cursor() as cur:
                await cur.execute(sql)
                users = await cur.fetchall()
        try:
            tasks = [utils.get_rasp(*user) for user in users]
            await asyncio.gather(*tasks)
        except EduDown:
            pass

        logger.info("Load successfully")
        await asyncio.sleep(config.cache_update_interval)


async def main():
    await db.connect()
    dp.include_router(command.router)
    dp.include_router(callback_query.router)
    tasks = [cache_update(), dp.start_polling(bot)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
