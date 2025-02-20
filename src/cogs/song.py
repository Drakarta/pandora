import discord
from discord.ext import tasks
from discord.ext.commands import Cog
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from utils.config import Config
from utils.DB import Database
from utils.wait import Wait


class Song(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.api_keys = Config().get_section("api_keys")
        self.config = Config().get_section("song")

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=self.api_keys.spotify_client,
                client_secret=self.api_keys.spotify_token,
            )
        )

        self.db = Database()

        self.send_song.start()

    @tasks.loop(hours=24)
    async def send_song(self):
        result = self.db.execute("SELECT value FROM data WHERE key = 'song_number'")
        song_number = int(result[0][0]) if result else 0

        playlist = self.sp.playlist_items(
            self.config.playlist_id,
            limit=1,
            offset=song_number,
            fields="items(track(name, artists(name), external_urls(spotify)))",
        )
        song = playlist["items"][0]["track"]

        channel = self.bot.get_channel(self.config.channel_id)
        message = await channel.send(
            f"# [{song['name']} - {song['artists'][0]['name']}]({song['external_urls']['spotify']})"
        )
        await message.publish()

        self.db.execute(
            "INSERT OR REPLACE INTO data (key, value) VALUES ('song_number', ?)",
            (str(song_number + 1),),
        )

    @send_song.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        await Wait.wait_until_time(5, 0)


async def setup(bot):
    await bot.add_cog(Song(bot), guilds=[discord.Object(id=734455624036909126)])
