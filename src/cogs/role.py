import sys
import discord
from discord import app_commands
from discord.ext.commands import Cog
import re

from utils.DB import Database
from utils.config import Config


class Role(Cog):
    def __init__(self, bot):
        self.bot = bot

        config_file = "./config/roles_config.toml"
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        self.config = Config(config_file)

        self.role_divider_id = self.config.role_divider_id
        self.color_regex = re.compile(
            r"^(?:0x#?[0-9A-Fa-f]{6}|\#[0-9A-Fa-f]{6}|0x[0-9A-Fa-f]{6}|rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\))$"
        )

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS user(
                user_id INT PRIMARY KEY, 
                role_id INT DEFAULT NULL
            )
            """
        )

    @app_commands.command(name="role", description="Create or update your custom role.")
    @app_commands.describe(
        name="Set the name of your role.",
        color="Set the color of your role. Hex or RGB format.",
    )
    @app_commands.guilds(discord.Object(id=734455624036909126))
    async def role(self, ctx, name: str = None, color: str = None):
        if not name and not color:
            await ctx.response.send_message(
                "You must provide a name or color.", ephemeral=True
            )
            return

        if color and not self.color_regex.match(color):
            await ctx.response.send_message("Invalid color format.", ephemeral=True)
            return

        res = self.db.execute(
            "SELECT role_id FROM user WHERE user_id = ?", (ctx.user.id,)
        )
        if not res:
            await self.create_custom_role(ctx, name, color)

        else:
            await self.edit_custom_role(ctx, name, color, res)

    async def create_custom_role(self, ctx, name, color):
        kwargs = {}
        if name:
            kwargs["name"] = name
        if color:
            kwargs["color"] = discord.Color.from_str(color)
        role = await ctx.guild.create_role(**kwargs)
        role_divider = discord.utils.get(ctx.guild.roles, id=self.role_divider_id)
        await role.edit(position=role_divider.position - 1)
        self.db.execute(
            "INSERT INTO user (user_id, role_id) VALUES (?, ?)",
            (ctx.user.id, role.id),
        )
        await ctx.user.add_roles(role)
        await ctx.response.send_message(
            f"Your role {role.mention} has been created.", ephemeral=True
        )

    async def edit_custom_role(self, ctx, name, color, res):
        role = discord.utils.get(ctx.guild.roles, id=res[0][0])
        kwargs = {}
        if name:
            kwargs["name"] = name
        if color:
            kwargs["color"] = discord.Color.from_str(color)
        await role.edit(**kwargs)
        await ctx.response.send_message(
            f"Your role {role.mention} has been updated.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Role(bot))
