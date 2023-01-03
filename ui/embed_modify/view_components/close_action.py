"""
All Components for the Close Action of EmbedUI View.
"""

import discord


class EmbedUiButtonClose(discord.ui.Button):
    """
    Close button für Action Close
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="CLOSE", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes close in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await interaction.response.defer()
            await self.view.close()
