import os
from discord.ext.commands import Cog
from discord.ext import commands

class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Command tree synced.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.bot.unload_extension(cog_name)
                except commands.ExtensionNotLoaded:
                    pass
                finally:
                    await self.bot.load_extension(cog_name)
                    print(f"Reloaded {filename}")
        await ctx.send("Cogs reloaded.")
        

async def setup(bot):
    await bot.add_cog(Admin(bot))
