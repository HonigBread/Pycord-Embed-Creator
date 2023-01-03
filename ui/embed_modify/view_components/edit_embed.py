"""
All Components to modify an Embed.
"""

import discord
import typing


# Normal Edit
class ButtonEmbedEdit(discord.ui.Button):
    """
    Button to edit the main components of an embed.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Embed", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback of button Press. Checks if the author is the same as the original then executes edit_embed of the
        original embed.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.edit_embed(interaction)


class ModalEmbedEdit(discord.ui.Modal):
    """
    Modal to input title, description, color, timestamp and url.
    """

    def __init__(self, default_data: dict, wrong_data: list = None):
        # Set Default
        if wrong_data is None:
            wrong_data = []
        super().__init__(title="Edit Embed", timeout=300)
        # Add all Input Text
        self.add_item(discord.ui.InputText(label="Title", placeholder="Enter the Title",
                                           value=default_data.get("title", ""), max_length=256, required=False))
        self.add_item(discord.ui.InputText(label="Description", placeholder="Enter the description",
                                           value=default_data.get("description", ""), max_length=4000,
                                           required=False, style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Color", placeholder="Enter a Hexcode (with #)",
                                           value=default_data.get("color", ""), min_length=7, max_length=7,
                                           required=False))
        self.add_item(discord.ui.InputText(label="Timestamp",
                                           placeholder="Enter a date with Format YYYY-MM-DDThh:mm:ss",
                                           value=default_data.get("timestamp", ""), required=False))
        self.add_item(discord.ui.InputText(label="URL", placeholder="Enter a valid URL",
                                           value=default_data.get("url", ""), required=False))
        # Check wrong_data
        if "title" in wrong_data:
            self.children[0].label = "Title: Error sending the Embed."
        if "description" in wrong_data:
            self.children[1].label = "Description: Error sending the Embed."
        if "color" in wrong_data:
            self.children[2].label = "Color: Enter a valid Hex code."
        if "timestamp" in wrong_data:
            self.children[3].label = "Timestamp: Enter a valid ISO Date."
        if "url" in wrong_data:
            self.children[4].label = "URL: Enter a valid http/https url."

        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """

        self.stop()

# Author Edit


class ButtonAuthorEdit(discord.ui.Button):
    """
    Button to edit the author components of an embed.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Author", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes edit_author in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.edit_author(interaction)


class ModalAuthorEdit(discord.ui.Modal):
    """
    Modal to input author name and author link.
    """

    def __init__(self, default_data: dict, wrong_data: list = None):
        if wrong_data is None:
            wrong_data = []
        super().__init__(title="Edit Embed", timeout=300)
        self.add_item(discord.ui.InputText(label="Name", placeholder="Enter the Name",
                                           value=default_data.get("name", ""), max_length=256, required=False))
        self.add_item(discord.ui.InputText(label="URL", placeholder="Enter a valid URL",
                                           value=default_data.get("url", ""), required=False))
        # Check wrong_data
        if "name" in wrong_data:
            self.children[0].label = "Name: Error sending the Embed."
        if "url" in wrong_data:
            self.children[1].label = "Description: Wrong URL Format."

        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """

        self.stop()

# Footer Edit


class ButtonFooterEdit(discord.ui.Button):
    """
    Button to edit the footer components of an embed.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Footer", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes edit_footer in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.edit_footer(interaction)


class ModalFooterEdit(discord.ui.Modal):
    """
    Modal to input footer text.
    """

    def __init__(self, default_data: dict, wrong_data: list = None):
        if wrong_data is None:
            wrong_data = []
        super().__init__(title="Edit Embed", timeout=300)
        self.add_item(discord.ui.InputText(label="Text", placeholder="Enter the Text",
                                           value=default_data.get("text", ""), max_length=2000, required=False,
                                           style=discord.InputTextStyle.long))
        # Check wrong_data
        if "text" in wrong_data:
            self.children[0].label = "Text: Error sending the Embed."

        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """

        self.stop()

# Image Edit


class ButtonImageEdit(discord.ui.Button):
    """
    Button to edit the Image components of an embed.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Image", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes edit_image in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.edit_image(interaction)

# Thumbnail Edit


class ButtonThumbnailEdit(discord.ui.Button):
    """
    Button to edit the Thumbnail components of an embed.
    """

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Thumbnail", row=1)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes edit_thumbnail in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.edit_thumbnail(interaction)

# Fields Edit


class SelectFieldEdit(discord.ui.Select):
    """
    Select to select the Field that should be modified / added.
    """

    def __init__(self, amount: int):
        options: list[discord.SelectOption] = []
        for index in range(amount):
            options.append(discord.SelectOption(label=f"Select Field {index}.",
                                                description="Selects the Field for further modifications.",
                                                value=str(index)))
        if amount < 25:
            options.append(discord.SelectOption(label="Add Field",
                                                description="Select this to add another Field to the Embed.",
                                                value="add"))
        super().__init__(placeholder="Choose a Field", min_values=0, max_values=1, options=options, row=3)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Gets executed when someone selects a field or add. When Add gets selected add_field will be executed,
        if another field got selected edit_field_mode will be executed.

        :param interaction: discord.Interaction -> The Interaction comming from the select Menu.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            if self.values[0] == "add":
                await self.view.add_field(interaction)
            else:
                await self.view.set_edit_field_view(int(self.values[0]))
                await interaction.response.defer()


class ButtonFieldEdit(discord.ui.Button):
    """
    Button to open the Modal to edit the Message.
    """

    def __init__(self, field_index: int):
        super().__init__(style=discord.ButtonStyle.primary, label="Edit Field", row=4)
        self.field_index = field_index

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes modify_field in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.modify_field(interaction, self.field_index)


class ButtonFieldRemove(discord.ui.Button):
    """
    Button to remove the Field.
    """

    def __init__(self, field_index: int):
        super().__init__(style=discord.ButtonStyle.danger, label="Remove Field", row=4)
        self.field_index = field_index

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes remove_field in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.remove_field(interaction, self.field_index)


class ButtonFieldInline(discord.ui.Button):
    """
    Button to change the Inline Parameter of the Field.
    """

    def __init__(self, field_index: int, default_value: bool = True):
        self.inline = default_value
        self.field_index: int = field_index
        if default_value is False:
            super().__init__(style=discord.ButtonStyle.danger, label="Inline: False", row=4)
        else:
            super().__init__(style=discord.ButtonStyle.green, label="Inline: True", row=4)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Executed on Button Press. Will change its state and then call modify_inline_field of the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button Press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.change_state()
            await self.view.modify_inline_field(interaction, self.field_index, self.inline)

    async def change_state(self) -> None:
        """
        Changes the State of the Button.

        :return:
        """

        self.inline = not self.inline
        if self.inline is True:
            self.label = "Inline: True"
            self.style = discord.ButtonStyle.success
        else:
            self.label = "Inline: False"
            self.style = discord.ButtonStyle.danger


class ModalFieldEdit(discord.ui.Modal):
    """
    Modal to edit the Field data
    """

    def __init__(self, default_data: dict, wrong_data: list = None):
        if wrong_data is None:
            wrong_data = []
        super().__init__(title="Edit Field", timeout=300)
        self.add_item(discord.ui.InputText(label="Name", placeholder="Enter the Name",
                                           value=default_data.get("name", ""), max_length=256, required=True))
        self.add_item(discord.ui.InputText(label="Value", placeholder="Enter the Value",
                                           value=default_data.get("value", ""), max_length=1024, required=True,
                                           style=discord.InputTextStyle.long))
        # Check wrong_data
        if "text" in wrong_data:
            self.children[0].label = "Text: Error sending the Embed."
        if "value" in wrong_data:
            self.children[1].label = "Value: Error sending the Embed."

        self.timeout = 300.0
        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """
        
        self.stop()

# Save Embed


class ButtonEmbedSave(discord.ui.Button):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Save Embed", row=4)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes save_embed in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.save_embed(interaction)


class ButtonEmbedSaveRename(discord.ui.Button):

    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Save Rename Embed", row=4)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        Callback if the Button got pressed. This checks if the user is the same as in the original slash command
        and then executes save_rename_embed in the original view.

        :param interaction: discord.Interaction -> The Interaction comming from the Button press.
        :return:
        """

        if self.view.ctx.author.id == interaction.user.id:
            await self.view.save_rename_embed(interaction)


class EmbedUiModalRename(discord.ui.Modal):
    """
    Modal to Rename the Embed
    """

    def __init__(self, default_data: dict):

        childs = [
            discord.ui.InputText(label="ID (must be unique)", placeholder="Please enter a valid ID. ONLY INTEGER.",
                                 value=default_data.get("id", "")),
            discord.ui.InputText(label="Name (must be unique)", placeholder="Please enter a valid Name.",
                                 value=default_data.get("name", ""))
        ]
        super().__init__(title="Rename the Embed.")
        for child in childs:
            self.add_item(child)
        self.timeout = 300.0
        self.interaction: typing.Optional[discord.Interaction] = None

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        On callback sets the current interaction. This also gets used as mark if the Modal run into a timeout.
        self.interaction will be None if Timeout happend.

        :param interaction: discord.Interaction -> The Interaction of the Button
        :return:
        """

        self.interaction = interaction

    async def on_timeout(self) -> None:
        """
        Gets executet on timeout. Stops the Modal.

        :return:
        """

        self.stop()
