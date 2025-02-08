import os
import sys

import discord
from discord import Intents, app_commands
from discord.ext.commands import Bot as BotBase

from utils.config import Config


class Bot(BotBase):
    def __init__(self):
        config_file = "./config/config.toml"
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        self.config = Config(config_file)

        self.activity = self.config.activity

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
            await self.load_extension(f"cogs.{cog}")
            print(f"loaded: {cog}")
        print("all cogs loaded, setup complete")

    def run(self, **kwargs):
        print("running bot...")
        super().run(self.config.api_tokens["discord"], reconnect=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.CustomActivity(name=self.activity),
        )


def main():
    Bot().run()


if __name__ == "__main__":
    main()
