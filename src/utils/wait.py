import asyncio
import datetime

import pytz

from utils.config import Config


class Wait:
    @staticmethod
    async def wait_until_time(hour: int, minute: int = 0):
        config = Config().get_section("main")

        timezone = pytz.timezone(config.timezone)
        now = datetime.datetime.now(tz=timezone)
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if now >= target_time:
            target_time += datetime.timedelta(days=1)

        sleep_seconds = (target_time - now).total_seconds()

        await asyncio.sleep(sleep_seconds)
