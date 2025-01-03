from discord.ext.commands import Cog
import random
import json

from utils.impersonate_webhook import ImpersonateWebhook

class YoeriCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_guild_id = 744191097554862171

    def load_quotes(self):
        with open("yoeri.json", "r") as file:
            data = json.load(file)
        return data["quotes"]

    @Cog.listener("on_message")
    async def yoeri(self, message):

        if message.author == self.bot.user or not message.guild:
            return

        if "yoeri" in message.content.lower():
            quotes = self.load_quotes()
            random_quote = random.choice(quotes)
            webhook = ImpersonateWebhook(self.bot, message.channel.id, "yoeri-hook")
            await webhook.impersonate_message(345956404202307595, random_quote)

        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(YoeriCog(bot))
