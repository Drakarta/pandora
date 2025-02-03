import sys
import discord
from discord.ext.commands import Cog

from utils.config import Config


class Voice_Chat(Cog):
    def __init__(self, bot):
        self.bot = bot

        config_file = "./config/voice_chat_config.toml"
        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        self.config = Config(config_file)

        self.category_id = self.config.category_id
        self.create_vc_id = self.config.create_voice_channel_id
        self.ignore_vc_ids = self.config.ignore_voice_channel_ids
        self.vc_owner_role_id = self.config.voice_channel_owner_role_id

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if before.channel and before.channel.id not in self.ignore_vc_ids:
            await self.handle_channel_leave(member, before.channel)

        if after.channel and after.channel.id == self.create_vc_id:
            await self.create_private_vc(member)

    async def handle_channel_leave(self, member, channel):
        if len(channel.members) == 0:
            await channel.delete()
            await member.remove_roles(discord.Object(id=self.vc_owner_role_id))
        elif self.vc_owner_role_id in [role.id for role in member.roles]:
            await member.remove_roles(discord.Object(id=self.vc_owner_role_id))
            new_owner = channel.members[0]
            await new_owner.add_roles(discord.Object(id=self.vc_owner_role_id))

    async def create_private_vc(self, member):
        category = discord.utils.get(member.guild.categories, id=self.category_id)
        if not category:
            return

        new_vc = await member.guild.create_voice_channel(
            name=f"{member.name}'s Channel", category=category
        )
        await member.move_to(new_vc)
        await member.add_roles(discord.Object(id=self.vc_owner_role_id))


async def setup(bot):
    await bot.add_cog(Voice_Chat(bot))
