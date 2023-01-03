"""
Contains all Elements for the delete Action of EmbedUI View.
"""

import discord
import typing


class EmbedUiButtonDelete(discord.ui.Button):
    """
    Delete Button for Action Delete.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="DELETE", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes delete in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.delete(interaction)


class EmbedUiButtonDeleteConfirm(discord.ui.Button):
    """
    Delete conformation Button for Action Delete.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="CONFIRM DELETION", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes delete_confirmation in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.delete_confirmation(interaction)


class EmbedUiModalDelete(discord.ui.Modal):
    """
    Modal to modify the Embed
    """

    def __init__(self):
        childs = [
            discord.ui.InputText(label="ID (must be unique)", placeholder="Please enter a valid ID. ONLY INTEGER. "
                                                                          "Prioritised!", required=False),
            discord.ui.InputText(label="Name (must be unique)", placeholder="Please enter a valid Name.")
        ]
        super().__init__(title="Delete an Embed.")
        for child in childs:
            self.add_item(child)
        self.timeout = 300.0
        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction:
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """

        self.stop()
