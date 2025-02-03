import discord


class ImpersonateWebhook:
    def __init__(self, bot, channel_id, name):
        self.bot = bot
        self.channel_id = channel_id
        self.name = name
        self.channel = self.bot.get_channel(self.channel_id)

        if not self.channel:
            raise ValueError(f"Unable to find channel <{channel_id}>")

    async def _get_or_create_webhook(self) -> discord.Webhook:
        existing_webhooks: list[discord.Webhook] = await self.channel.webhooks()

        for webhook in existing_webhooks:
            if webhook.name == f"{self.name}-{self.channel.id}":
                return webhook

        return await self.channel.create_webhook(name=f"{self.name}-{self.channel.id}")

    async def impersonate_message(self, user_id: int, message: str):
        webhook = await self._get_or_create_webhook()
        user = await self.channel.guild.fetch_member(user_id)

        payload = {
            "content": message,
            "username": user.display_name,
            "avatar_url": (user.display_avatar.url if user.display_avatar else None),
        }

        await webhook.send(**payload)
