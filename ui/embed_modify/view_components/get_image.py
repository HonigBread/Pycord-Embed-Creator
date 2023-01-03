"""
Beinhält alle Komponenten um ein Image vom User zu erfragen.
"""

import discord
import typing
import asyncio
from asyncio import exceptions
import requests
import uuid
import functools
import shutil
import imghdr
import os


class StopButton(discord.ui.Button):
    """
    Button to stop wating for an Image
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="STOP")


class DeleteButton(discord.ui.Button):
    """
    Button to delete the Image
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Delete current Image.")


class GetImageView(discord.ui.View):
    """
    View to get an Image.
    """

    def __init__(self, bot: discord.Bot, user: typing.Union[discord.Member, discord.User]):
        super().__init__(timeout=900)
        stop_button: StopButton = StopButton()
        stop_button.callback = self.stop_press
        delete_button: DeleteButton = DeleteButton()
        delete_button.callback = self.delete_press
        self.add_item(stop_button)
        self.add_item(delete_button)
        self.channel: typing.Optional[discord.channel.TextChannel] = None
        self.bot = bot
        self.user: typing.Union[discord.Member, discord.User] = user
        self.image: typing.Optional[str] = None

    async def start(self, channel: discord.channel.TextChannel = None) -> None:
        """
        This should be executed right after the message got send. This waits for the Image from the User.

        :param channel: discord.channel.TextChannel -> The Channel which should be waited in. Default messag Channel.
        :return:
        """

        # Set Default channel
        if channel is None:
            channel = self.message.channel
        self.channel = channel
        # Loop to catch wrong types and give the User another try
        while self.image is None:
            # Try getting the Image, calls on_timeout if user is taking to long
            try:
                message: discord.Message = await self.bot.wait_for("message", check=self.check_message, timeout=300.0)
            except exceptions.TimeoutError:
                await self.on_timeout()
                return
            # Always uses the first Attachment
            attachment: discord.Attachment = message.attachments[0]
            # Downloading the Image
            loop = asyncio.get_event_loop()
            image_get = loop.run_in_executor(None, functools.partial(requests.get, attachment.url, stream=True))
            image = await image_get
            # Error if the Image could not be Downloaded
            if image.status_code != 200:
                await self.message.edit("Image could not be Downloaded, please check your file and try again.")
                continue
            # Creating unique name to store the Picture
            picture_id: uuid.UUID = uuid.uuid4()
            with open(f"./daten/pictures/{picture_id.int}", "wb") as save_file:
                shutil.copyfileobj(image.raw, save_file)
            # Checks the Image type
            image_type: typing.Optional[str] = imghdr.what(f"./daten/pictures/{picture_id.int}")
            if image_type is None:
                # The File was not an Image - Delete and retry for User
                await self.message.edit("File is not an Image, please check your file and try again.")
                os.remove(f"./daten/pictures/{picture_id.int}")
                continue
            # Image got succesfully checked, renaming to support windows Type endings
            image_name: str = f"{picture_id.int}.{image_type}"
            source = os.path.join("./daten/pictures", f"{picture_id.int}")
            destination = os.path.join("./daten/pictures", image_name)
            os.rename(source, destination)
            # Set correct Image Name
            self.image = image_name
        # Delete all Messages for the Picture getting - To keep the proccess clean in the Chat.
        try:
            await self.message.delete()
        except discord.errors.NotFound:
            pass
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass
        self.stop()

    def check_message(self, message: discord.Message) -> bool:
        """
        Checks if the Message has attachments and if the user is the same as the one used to start the Embed Edit.

        :param message: discord.Message -> The Message that should be checked.
        :return: bool -> False if something was wrong
        """

        if message.author.id != self.user.id:
            return False
        if message.channel.id != self.channel.id:
            return False
        if len(message.attachments) == 0:
            return False
        return True

    async def stop_press(self, interaction: discord.Interaction) -> None:
        """
        Executed on Press at Stop. This Stops the Image getting proccess and uses the old if one existed.

        :param interaction: discord.Interaction -> The Interaction from the Button.
        :return:
        """

        await self.message.delete()
        self.stop()
        await interaction.response.defer()

    async def delete_press(self, interaction: discord.Interaction) -> None:
        """
        Executed on Press at delete. This deletes the Image and does the Embed does not have this Image anymore.

        :param interaction: discord.Interaction -> The Interaction from the Button.
        :return:
        """

        await self.message.delete()
        self.image = "delete"
        self.stop()
        await interaction.response.defer()

    async def on_timeout(self) -> None:
        """
        On timeout this deletes the Message. And Stops the View.

        :return:
        """
        try:
            await self.message.delete()
        except discord.errors.NotFound:
            pass
        self.stop()
