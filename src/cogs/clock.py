import asyncio
from discord.ext import tasks
from discord.ext.commands import Cog
import datetime
import pytz

from utils.config import Config


class Clock(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config().get_section("clock")
        self.config2 = Config().get_section("main")

        self.timezone = pytz.timezone(self.config2.timezone)
        self.channel_id = self.config.channel_id

        if not self.channel_id:
            print("Clock Cog: Missing 'channel_id' in config.")
            return

        self.clock.start()

    @tasks.loop(minutes=10)
    async def clock(self):
        try:
            channel = await self.bot.fetch_channel(self.channel_id)
            if not channel:
                print(f"Clock Cog: Failed to find channel with ID {self.channel_id}")
                return

            current_time = datetime.datetime.now(tz=self.timezone)
            formatted_time = current_time.strftime("%H:%M")[:-1] + "0"
            await channel.edit(name=f"Time: {formatted_time} [{current_time.tzname()}]")

        except Exception as e:
            print(f"Clock Cog: Error updating channel name - {e}")

    @clock.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.now()
        delay_seconds = (10 - (current_time.minute % 10)) * 60 - current_time.second
        await asyncio.sleep(delay_seconds)


async def setup(bot):
    await bot.add_cog(Clock(bot))
