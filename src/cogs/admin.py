import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
from typing import Literal, Optional

from utils.DB import Database


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS channels(
                guild_id INT PRIMARY KEY,
                main_channel_id INT DEFAULT NULL
            )
            """
        )

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS data(
                key TEXT PRIMARY KEY,
                value TEXT DEFAULT NULL
            )
            """
        )

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object] = None,
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        guilds = guilds or []

        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        COGS = [path[:-3] for path in os.listdir("./cogs") if path[-3:] == ".py"]
        for cog in COGS:
            if cog.startswith("_"):
                continue
            await self.load_extension(f"cogs.{cog}")
            print(f"reloaded: {cog}")
        print("all cogs reloaded.")

    # @commands.command()
    # @commands.is_owner()
    # async def servers(self, ctx):
    #     server_list = []
    #     async for server in self.bot.fetch_guilds(limit=None):
    #         server_list.append(f"{server.id} - {server.name}")

    #     server = "\n".join(server_list)
    #     await ctx.send(f"```{server}```")

    # @commands.command()
    # @commands.is_owner()
    # async def leaveserver(self, ctx, guild_id: int):
    #     guild = self.bot.get_guild(guild_id)

    #     if guild is None:
    #         await ctx.send(f"I am not in a server with ID: {guild_id}.")
    #         return

    #     await guild.leave()
    #     await ctx.send(f"Left the server: {guild.name} (ID: {guild.id}).")

    @commands.command()
    @commands.is_owner()
    async def setmainchannel(self, ctx):
        self.db.execute(
            "INSERT OR REPLACE INTO main_channel (guild_id, main_channel_id) VALUES (?, ?)",
            (ctx.guild.id, ctx.channel.id),
        )
        await ctx.send(f"Main channel set to this channel.")

    @commands.command()
    @commands.is_owner()
    async def setmusicchannel(self, ctx):
        self.db.execute(
            "INSERT OR REPLACE INTO music_channel (guild_id, music_channel_id) VALUES (?, ?)",
            (ctx.guild.id, ctx.channel.id),
        )
        await ctx.send(f"Music channel set to this channel.")

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.response.send_message(f"pong! ({latency}ms)")


async def setup(bot):
    await bot.add_cog(Admin(bot))
