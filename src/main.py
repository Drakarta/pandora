import os
import sys

import discord
from discord import Intents, app_commands
from discord.ext.commands import Bot as BotBase

from utils.config import Config


class Bot(BotBase):
    def __init__(self):
        self.config = Config().get_section("main")
        self.config2 = Config().get_section("api_keys")

        super().__init__(
            command_prefix=self.config.prefix,
            owner_id=self.config.owner_id,
            intents=Intents.all(),
            description=self.config.description,
            case_insensitive=True,
        )

    async def setup_hook(self):
        COGS = [path[:-3] for path in os.listdir("./cogs") if path[-3:] == ".py"]
        for cog in COGS:
            if cog.startswith("_"):
                continue
            await self.load_extension(f"cogs.{cog}")
            print(f"loaded: {cog}")
        print("all cogs loaded, setup complete")

    def run(self, **kwargs):
        print("running bot...")
        super().run(self.config2.discord_token, reconnect=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.CustomActivity(name="*yawwwwn* I'm awake now."),
        )


def main():
    Bot().run()


if __name__ == "__main__":
    main()
