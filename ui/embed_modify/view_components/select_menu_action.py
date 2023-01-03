"""
Contains the Select Menu for Actions in the EmbedUI View.
"""

import discord


class EmbedUiSelect(discord.ui.Select):
    """
    Inherent: discord.ui.Select

    Select Menü für embed_ui
    """

    def __init__(self):
        # Default Options
        options = [
            discord.SelectOption(
                label="Close", description="Close this Embed. This will not save the changes."
            ),
            discord.SelectOption(
                label="Create", description="Creates a new Embed."
            ),
            discord.SelectOption(
                label="Modify", description="Modifys an Embed."
            ),
            discord.SelectOption(
                label="Delete", description="Deletes an Embed."
            )
        ]
        # Init super
        super().__init__(placeholder="Choose an Action", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Select got changed. This checks if the user is the same as in the original slash command
        and then executes action_change in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        await interaction.response.defer()
        if self.view.ctx.author.id == interaction.user.id:
            await self.view.action_change()
