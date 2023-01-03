"""
Beinhält die View für die Retry Message
"""

import discord
import enum
import typing

class ReplyType(enum.Enum):
    """
    Enum for type of edit that should be retried.
    """

    normal_edit = 0
    author_edit = 1
    footer_edit = 2
    image_edit = 3
    thumbnail_edit = 4
    add_field = 5
    modify_field = 6


class RetryEditButton(discord.ui.Button):
    """
    Button to retry the Edit.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Retry")


class RetryEditView(discord.ui.View):
    """
    View to retry the Edit for the Embed.
    """

    def __init__(self, old_data: typing.Optional[dict], retry_type: ReplyType, original_view: discord.ui.View, wrong_data: list):
        super().__init__(timeout=300)
        self.old_data: dict = old_data
        self.retry_type: ReplyType = retry_type
        self.original_view: discord.ui.View = original_view
        self.wrong_data: list = wrong_data
        retry_button: RetryEditButton = RetryEditButton()
        retry_button.callback = self.button_press
        self.add_item(retry_button)

    async def button_press(self, interaction: discord.Interaction) -> None:
        """
        Gets execuded when the retry Button gets pressed.
        Deletes the Message and activates the Edit process with the old data.

        :param interaction: The Interaction from the Button Press.
        :return:
        """

        await self.message.delete()
        match self.retry_type:
            case ReplyType.normal_edit:
                await self.original_view.edit_embed(interaction, self.old_data, self.wrong_data)
            case ReplyType.author_edit:
                await self.original_view.edit_author(interaction, self.old_data, self.wrong_data)
            case ReplyType.footer_edit:
                await self.original_view.edit_footer(interaction, self.old_data, self.wrong_data)
            case ReplyType.image_edit:
                await self.original_view.edit_image(interaction)
            case ReplyType.thumbnail_edit:
                await self.original_view.edit_thumbnail(interaction)
            case ReplyType.add_field:
                await self.original_view.add_field(interaction)
            case ReplyType.modify_field:
                await self.original_view.modify_field(interaction, self.old_data["index"], self.old_data)

    async def on_timeout(self) -> None:
        """
        Deletes the Message on timeout and stops the View.

        :return:
        """

        await self.message.delete()
        self.stop()
