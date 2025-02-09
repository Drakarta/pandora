import sys
import discord
from discord import app_commands
from discord.ext.commands import Cog

from utils.config import Config
from utils.DB import Database


class Voice_Chat(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config().get_section("voice_chat")

        self.category_id = self.config.category_id
        self.create_vc_id = self.config.create_voice_channel_id
        self.waiting_room_vc_id = self.config.waiting_room_voice_channel_id
        self.vc_owner_role_id = self.config.voice_channel_owner_role_id

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS voice_channels (
                channel_id INTEGER PRIMARY KEY
            )
            """
        )

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if before.channel:
            res = self.db.execute(
                "SELECT channel_id FROM voice_channels WHERE channel_id = ?",
                (before.channel.id,),
            )

            if res and res[0][0] == before.channel.id:
                await self.handle_channel_leave(member, before.channel)

        if after.channel and after.channel.id == self.create_vc_id:
            await self.create_voice_channel(member)

    async def handle_channel_leave(self, member, channel):
        if len(channel.members) == 0:
            self.db.execute(
                "DELETE FROM voice_channels WHERE channel_id = ?", (channel.id,)
            )
            await channel.delete()
            await member.remove_roles(discord.Object(id=self.vc_owner_role_id))
        elif self.vc_owner_role_id in [role.id for role in member.roles]:
            await member.remove_roles(discord.Object(id=self.vc_owner_role_id))

            new_owner = channel.members[0]
            await channel.edit(name=f"{new_owner.display_name}'s channel")
            await new_owner.add_roles(discord.Object(id=self.vc_owner_role_id))

    async def create_voice_channel(self, member):
        category = discord.utils.get(member.guild.categories, id=self.category_id)
        if not category:
            return

        new_vc = await member.guild.create_voice_channel(
            f"{member.display_name}'s channel", category=category
        )
        self.db.execute("INSERT INTO voice_channels VALUES (?)", (new_vc.id,))
        await member.move_to(new_vc)
        await member.add_roles(discord.Object(id=self.vc_owner_role_id))

    @app_commands.command(name="channel", description="Edit your voice channel")
    @app_commands.describe(
        name="Set the name of the channel.",
        limit="The user limit of the channel. 0 = unlimited.",
        lock="Lock the channel.",
        hide="Hide the channel.",
        promote="Promote a user to voice channel owner.",
        move="Move a user into the channel from the waiting room.",
    )
    @app_commands.guilds(discord.Object(id=734455624036909126))
    async def channel(
        self,
        ctx,
        name: str = None,
        limit: int = None,
        lock: bool = None,
        hide: bool = None,
        promote: discord.Member = None,
        move: discord.Member = None,
    ):
        channel = ctx.user.voice.channel if ctx.user.voice else None
        if not channel:
            await ctx.response.send_message(
                "You are not in a voice channel.", ephemeral=True
            )
            return

        res = self.db.execute(
            "SELECT channel_id FROM voice_channels WHERE channel_id = ?", (channel.id,)
        )
        if not res:
            await ctx.response.send_message(
                "You are not in a custom voice channel.", ephemeral=True
            )
            return

        if self.vc_owner_role_id not in [role.id for role in ctx.user.roles]:
            await ctx.response.send_message(
                "You are not the owner of the voice channel.", ephemeral=True
            )
            return

        messages = []

        if name or limit is not None:
            kwargs = {}
            if name:
                messages.append(f"Channel name set to **{name}**.")
                kwargs["name"] = name
            if limit is not None:
                messages.append(f"User limit set to **{limit}**.")
                kwargs["user_limit"] = limit
            await channel.edit(**kwargs)

        if lock is not None or hide is not None:
            perms = channel.overwrites_for(ctx.guild.default_role)
            if lock is not None:
                perms.connect = not lock
                messages.append("Channel locked." if lock else "Channel unlocked.")
            if hide is not None:
                perms.view_channel = not hide
                messages.append("Channel hidden." if hide else "Channel visible.")
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)

        if promote:
            if self.vc_owner_role_id in [role.id for role in promote.roles]:
                await ctx.response.send_message(
                    "User is already a voice channel owner.", ephemeral=True
                )
                return
            if promote not in channel.members:
                await ctx.response.send_message(
                    "User is not in the voice channel.", ephemeral=True
                )
                return
            await ctx.user.remove_roles(discord.Object(id=self.vc_owner_role_id))
            await promote.add_roles(discord.Object(id=self.vc_owner_role_id))
            messages.append(
                f"Promoted **{promote.display_name}** to voice channel owner."
            )
            await channel.edit(name=f"{promote.display_name}'s channel")

        if move:
            if not move.voice or move.voice.channel.id != self.waiting_room_vc_id:
                await ctx.response.send_message(
                    "User is not in the waiting room.", ephemeral=True
                )
                return
            await move.move_to(channel)
            messages.append(f"Moved **{move.display_name}** to your channel.")

        if messages:
            await ctx.response.send_message("\n".join(messages), ephemeral=True)
        else:
            await ctx.response.send_message("No changes were made.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Voice_Chat(bot))
