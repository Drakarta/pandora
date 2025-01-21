from discord.ext.commands import Cog
import random
import json

from utils.impersonate_webhook import ImpersonateWebhook

class Yoeri(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.data = self.load_json("./config/yoeri.json")
        # self.allowed_guild_id = self.data["guild_id"]
        self.allowed_guild_id = 734455624036909126
        self.yoeri_id = self.data["user_id"]
        self.quotes = self.data["quotes"]

    def load_json(self, path: str):
        with open(path, "r") as file:
            data = json.load(file)
        return data

    @Cog.listener("on_message")
    async def yoeri(self, message):
        if message.author.bot:
            return

        if message.guild.id != self.allowed_guild_id:
            return
        
        if message.author.id == self.yoeri_id:
            return
        
        if random.random() < 0.05:
            random_quote = random.choice(self.quotes)
            webhook = ImpersonateWebhook(self.bot, message.channel.id, "yoeri-hook")
            await webhook.impersonate_message(345956404202307595, random_quote)

async def setup(bot):
    await bot.add_cog(Yoeri(bot))
