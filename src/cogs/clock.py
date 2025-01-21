import sys
import asyncio
from discord.ext.commands import Cog
from discord.ext import tasks
import datetime
import pytz

from utils.config import Config

class Clock(Cog):
    def __init__(self, bot):
        self.bot = bot

        config_file = "./config/clock_config.toml"
        if len(sys.argv) > 1:
            config_file = sys.argv[1]

        self.config = Config(config_file)
        self.timezone = pytz.timezone(self.config.timezone)
        self.channel_id = self.config.channel_id
        self.clock.start()
    
    @tasks.loop(minutes=10)
    async def clock(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"Failed to find channel with ID {self.channel_id}")
            return
        current_time = datetime.datetime.now(tz=self.timezone)
        formatted_minutes = "{:02}".format((current_time.minute // 10) * 10)
        await channel.edit(
            name=f"Time: {current_time.strftime('%H')}:{formatted_minutes} [{current_time.tzname()}]"
        )

    @clock.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.now()
        delay_seconds = (10 - (current_time.minute % 10)) * 60 - current_time.second
        await asyncio.sleep(delay_seconds)

async def setup(bot):
    await bot.add_cog(Clock(bot))
