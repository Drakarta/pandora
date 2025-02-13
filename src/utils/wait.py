import asyncio
import datetime

import pytz

from utils.config import Config


class Wait:
    def __init__(self):
        self.config = Config().get_section("main")

        self.timezone = pytz.timezone(self.config.timezone)

    async def wait_until_time(self, hour: int, minute: int = 0):
        now = datetime.datetime.now(tz=self.timezone)
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if now >= target_time:
            target_time += datetime.timedelta(days=1)

        sleep_seconds = (target_time - now).total_seconds()
        print(
            f"Sleeping for {sleep_seconds / 3600:.2f} hours until {hour:02d}:{minute:02d}."
        )

        await asyncio.sleep(sleep_seconds)
