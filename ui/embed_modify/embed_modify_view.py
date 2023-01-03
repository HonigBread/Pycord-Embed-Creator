"""
File Contains Embed View for modifying/create/delete Embeds.
"""

import copy
import os.path
import typing
import asyncio
import shutil

# Import all Components:
from ui.embed_modify.view_components import close_action, create_action, edit_embed, select_menu_action, retry_view, \
    get_image, modify_action, delete_action
import discord
import re
import datetime
from urllib.parse import urlparse

class EmbedUi(discord.ui.View):
    """
    View for embed modifications.
    """

    def __init__(self, bot: discord.Bot, application_ctx: discord.ApplicationContext):
        """
        Init for embed_ui. Starts the process and adds all buttons / Selects.

        :param bot: discord.Bot -> The current Discord bot
        """

        # The ApplicationContext of the original Slash Command
        self.ctx: discord.ApplicationContext = application_ctx
        # Select for the Action the User wants to perform.
        self.select_action:  select_menu_action.EmbedUiSelect = select_menu_action.EmbedUiSelect()
        super().__init__(self.select_action)
        # Init Class Variables
        self.bot = bot
        self.current_embed: discord.Embed = discord.Embed() # Stores the current embed to modify
        self.embed_message: typing.Optional[discord.Message] = None # Stores the current message which displays the current embed
        self.current_db_embed_data: dict = {} # The Database data of the embed (id and name)
        # Default Embeds which get displayed if the Action is selected.
        self.default_embed: discord.Embed = discord.Embed(title="Embed UI", description="Please Select select your "
                                                                                        "Action:")
        self.default_close_embed: discord.Embed = discord.Embed(title="Embed UI - Close",
                                                                description="This Closes the current Embed UI.")
        self.default_create_embed: discord.Embed = discord.Embed(title="Embed UI - Create",
                                                                 description="This Creates a new Embed. \n"
                                                                             "After you clicked the create Button a "
                                                                             "Modal will open, you have to put an "
                                                                             "unique Name and ID, then submit it. "
                                                                             "\nYou will then see a empty Embed. "
                                                                             "You can fill it with data by clicking "
                                                                             "the Buttons in Row 3. \nYou can add "
                                                                             "Fields with the Select Menu in row 4. "
                                                                             "\nDO NOT FORGET TO SAVE BEFORE CHANGING "
                                                                             "ACTION")
        self.default_modify_embed: discord.Embed = discord.Embed(title="Embed UI - Modify",
                                                                 description="This Modifys an old Embed. \n"
                                                                             "After you clicked the modify Button a "
                                                                             "Modal will open, you have to put an "
                                                                             "Name or ID, then submit it. "
                                                                             "\nYou will then see the old Embed. "
                                                                             "You can modify it with data by clicking "
                                                                             "the Buttons in Row 3. \nYou can add "
                                                                             "Fields with the Select Menu in row 4. "
                                                                             "\nDO NOT FORGET TO SAVE BEFORE CHANGING "
                                                                             "ACTION")
        self.default_delete_embed: discord.Embed = discord.Embed(title="Embed UI - Delete",
                                                                 description="This Deletes an old Embed. \n"
                                                                             "After you clicked the delete Button a "
                                                                             "Modal will open, you have to put an "
                                                                             "Name or ID, then submit it. \n"
                                                                             "You will then see the old Embed. \n"
                                                                             "After you press Delte confirm, the embed"
                                                                             "gets deleted.")
        # cached Images
        self.chached_images = []

    # Methods

    async def start(self) -> None:
        """
        This should be called right after the Message with this View was send.

        :return:
        """

        await self.message.edit(embed=self.default_embed)

    async def action_change(self) -> None:
        """
        This Function will be executed if the user selects an Action. Should not be called manually.
        Debendend on the selected Action it runs the corresponding Function.

        :return:
        """

        await self.delete_chached_images()
        action = self.select_action.values[0]
        match action:
            case "Close":
                await self.action_close()
            case "Create":
                await self.action_create()
            case "Modify":
                await self.action_modify()
            case "Delete":
                await self.action_delete()

    async def set_edit_embed_view(self) -> None:
        """
        Adds all Items to edit an Embed. Removes every other Item, except for the Action select.
        Edits the current message with the new View.

        :return:
        """

        await self.remove_except_action_select()
        self.add_item(edit_embed.ButtonEmbedEdit())
        self.add_item(edit_embed.ButtonAuthorEdit())
        self.add_item(edit_embed.ButtonFooterEdit())
        self.add_item(edit_embed.ButtonImageEdit())
        self.add_item(edit_embed.ButtonThumbnailEdit())
        self.add_item(edit_embed.SelectFieldEdit(len(self.current_embed.fields)))
        self.add_item(edit_embed.ButtonEmbedSave())
        self.add_item(edit_embed.ButtonEmbedSaveRename())
        await self.message.edit(view=self)

    async def set_edit_field_view(self, current_field_index: int) -> None:
        """
        Adds all Items to edit a Field of an Embed. Removes every Item in the 4. row. Adds all Items for the Field
        modification and the save embed Button.
        Edits the current message with the new View.

        :param current_field_index: int -> The index of the current Field.
        :return:
        """

        await self.remove_row(4)
        self.add_item(edit_embed.ButtonFieldEdit(current_field_index))
        default_inlane: bool = self.current_embed.fields[current_field_index].inline
        self.add_item(edit_embed.ButtonFieldInline(current_field_index, default_value=default_inlane))
        self.add_item(edit_embed.ButtonFieldRemove(current_field_index))
        self.add_item(edit_embed.ButtonEmbedSave())
        self.add_item(edit_embed.ButtonEmbedSaveRename())
        await self.message.edit(view=self)

    async def remove_except_action_select(self) -> None:
        """
        Removes every row except of the first.
        Does not edit the message.

        :return:
        """

        delete_list: list[discord.ui.Item] = [child for child in self.children if child.row != 0]
        for child in delete_list:
            self.remove_item(child)

    async def remove_row(self, row: int) -> None:
        """
        Removes all components in a row.
        Does not edit the message.

        :return:
        """

        delete_list: list[discord.ui.Item] = [child for child in self.children if child.row == row]
        for child in delete_list:
            self.remove_item(child)

    async def send_embed(self, embed: discord.Embed, interaction: discord.Interaction) \
            -> typing.Optional[discord.Message]:
        """
        Sends the current embed and delets the old embed message if one exists.
        If the sending of the new embed does not work the old embed message does not get deleted.

        :param embed: discord.Embed -> The embed which should be sent.
        :param interaction: discord.Interaction -> The Interaction with whom it should be sent (uses followup).
        :return: Optional[discord.Message] -> None if sending the Message failed else gives sent message.
        """

        files: list[discord.File] = [] # List of all files send with the embed.
        # Get author Image
        if embed.author is not None and type(embed.author.icon_url) is str and len(embed.author.icon_url) > 0:
            file_name: str = embed.author.icon_url[13:] # File are send via attachment://FILE_NAME
            if os.path.isfile(f"./daten/pictures/{file_name}"): # If any file does not exist None is returned
                files.append(discord.File(f"./daten/pictures/{file_name}", filename=file_name))
            elif os.path.isfile(f"./daten/saved_pictures/{file_name}"):
                files.append(discord.File(f"./daten/saved_pictures/{file_name}", filename=file_name))
            else:
                return None
        # Get footer Image
        if embed.footer is not None and type(embed.footer.icon_url) is str and len(embed.footer.icon_url) > 0:
            file_name: str = embed.footer.icon_url[13:]
            if os.path.isfile(f"./daten/pictures/{file_name}"):
                files.append(discord.File(f"./daten/pictures/{file_name}", filename=file_name))
            elif os.path.isfile(f"./daten/saved_pictures/{file_name}"):
                files.append(discord.File(f"./daten/saved_pictures/{file_name}", filename=file_name))
            else:
                return None
        # Get embed Image
        if type(embed.image.url) is str:
            file_name: str = embed.image.url[13:]
            if os.path.isfile(f"./daten/pictures/{file_name}"):
                files.append(discord.File(f"./daten/pictures/{file_name}", filename=file_name))
            elif os.path.isfile(f"./daten/saved_pictures/{file_name}"):
                files.append(discord.File(f"./daten/saved_pictures/{file_name}", filename=file_name))
            else:
                return None
        # Get embed Thumbnail
        if type(embed.thumbnail.url) is str:
            file_name: str = embed.thumbnail.url[13:]
            if os.path.isfile(f"./daten/pictures/{file_name}"):
                files.append(discord.File(f"./daten/pictures/{file_name}", filename=file_name))
            elif os.path.isfile(f"./daten/saved_pictures/{file_name}"):
                files.append(discord.File(f"./daten/saved_pictures/{file_name}", filename=file_name))
            else:
                return None
        # Try Sending the embed.
        try:
            message: discord.Message = await interaction.followup.send(embed=embed, files=files)
        except discord.errors.HTTPException:
            return None
        # Sending was Succesfull -> Deleting old embed Message
        if self.embed_message is not None:
            await self.embed_message.delete()
        self.current_embed = embed
        return message

    async def delete_image(self, icon_url: str) -> None:
        """
        Deletes an Image.

        :param icon_url: str -> The complete icon url - will be stripped inside the function
        :return:
        """

        # Deletes the image in the database
        if type(icon_url) is str:
            if os.path.isfile(f"./daten/pictures/{icon_url[13:]}"):
                os.remove(f"./daten/pictures/{icon_url[13:]}")
        if type(icon_url) is str:
            if icon_url[13:] in self.chached_images:
                self.chached_images.remove(icon_url[13:])

    async def delete_chached_images(self) -> None:
        """
        Deletes all Files in ./daten/pictures

        :return:
        """

        for file in self.chached_images:
            try:
                os.remove(f"./daten/pictures/{file}")
            except FileNotFoundError:
                pass
        self.chached_images = []

    # Actions

    async def action_close(self) -> None:
        """
        Will be executed if the action close is selected.
        Adds the close Button, on press this will delete the original message.
        It will delete the embed message, if one exists already.
        Edits the message, with the new View and the default close embed.

        :return:
        """

        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        await self.remove_except_action_select()
        self.add_item(close_action.EmbedUiButtonClose())
        await self.message.edit(embed=self.default_close_embed, view=self)

    async def action_create(self) -> None:
        """
        Will be executed if the action create is selected.
        Adds the create Button, on press this will ask for id and name, these have to be unique in the database.
        After the creation it automatically goes into edit embed mode.
        It will delete the embed message, if one exists already.
        Edits the message, with the new View and the default create embed.

        :return:
        """

        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        await self.remove_except_action_select()
        self.add_item(create_action.EmbedUiButtonCreate())
        await self.message.edit(embed=self.default_create_embed, view=self)

    async def action_modify(self) -> None:
        """
        Will be executed if the action modify is selected.
        Adds the modify Button, on press this will ask for id or name, these have to be in the database. ID will be
        prioritiesd.
        After loading, it automatically goes into edit embed mode.
        It will delete the embed message, if one exists already.
        Edits the message, with the new View and the default delete embed.

        :return:
        """

        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        await self.remove_except_action_select()
        self.add_item(modify_action.EmbedUiButtonModify())
        await self.message.edit(embed=self.default_modify_embed, view=self)


    async def action_delete(self) -> None:
        """
        Will be executed if the action delete is selected.
        Adds the delete Button, on press this will ask for id or name, these have to be in the database. ID will be
        prioritiesd.
        After loading, it sends the embed and asks to confirm the deletion.
        It will delete the embed message, if one exists already.
        Edits the message, with the new View and the default modify embed.

        :return:
        """

        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        await self.remove_except_action_select()
        self.add_item(delete_action.EmbedUiButtonDelete())
        await self.message.edit(embed=self.default_delete_embed, view=self)

    # Button Responses

    # Close
    async def close(self) -> None:
        """
        Gets executed on button close press.
        Closes the EmbedUI.
        Deletes the original message and the embed message if one exists.

        :return:
        """

        await self.message.edit(view=None)
        await self.message.delete()
        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        self.stop()

    # Create
    async def create(self, interaction: discord.Interaction) -> None:
        """
        Gets executed on button create press.
        Sends a Modal which asks the database data for the embed. These will be checked to be unique.
        If they are correct, the embed will be saved in the database as a new embed with the default value.
        After that the edit embed mode gets activated with the created embed.

        :param interaction: discord.Interaction -> The current Interaction. No Followup.
        :return:
        """

        # User input via Modal - ID and Name
        modal = create_action.EmbedUiModalCreate()
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validation - Has to be unique in the Database
        embed_name: str = modal.children[1].value
        try:
            # Check if ID is int
            embed_id: int = int(modal.children[0].value)
        except ValueError:
            await modal.interaction.response.send_message("ID is not Integer!", ephemeral=True)
            return
        # TODO: Check if id exists in Database -> If not exist_embed_id should be None
        exist_embed_id: typing.Optional[dict]
        if exist_embed_id is not None:
            await modal.interaction.response.send_message("Embed id already exists.", ephemeral=True)
            return
        # TODO: Check if name exists in Database -> If not exist_embed_name should be None
        exist_embed_name: typing.Optional[dict]
        if exist_embed_name is not None:
            await modal.interaction.response.send_message("Embed name already exists.", ephemeral=True)
            return
        # Set current db embed data -> Gets used when saving the embed after editing.
        self.current_db_embed_data = {"id": embed_id, "name": embed_name}
        # Set default Embed
        embed = discord.Embed(description="Default")
        # Create Embed in Database
        # TODO: Create Embed in Database (id=embed_id, name=embed_name, value=embed.to_dict())
        # Send the new embed with the Button Press Interaction.
        self.embed_message = await self.send_embed(embed, interaction)
        # Set the View to edit embed Mode.
        await self.set_edit_embed_view()
        await modal.interaction.response.defer()

    # Modify
    async def modify(self, interaction: discord.Interaction) -> None:
        """
        Gets executed on button modify press.
        Sends a Modal which asks the database data for the embed. These will be checked to be existing.
        If they are correct, the embed will be loaded and send.
        After that the edit embed mode gets activated with the created embed.

        :param interaction: discord.Interaction -> The current Interaction. No Followup.
        :return:
        """

        # User input via Modal - ID and Name
        modal = modify_action.EmbedUiModalModify()
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validation
        embed_name: str = modal.children[1].value
        embed_id: typing.Optional[str] = modal.children[0].value
        if len(embed_id) > 0:
            try:
                # Check if ID is int
                embed_id: int = int(modal.children[0].value)
            except ValueError:
                await modal.interaction.response.send_message("ID is not Integer!", ephemeral=True)
                return
        else:
            embed_id = None
        # Get embed from Database - ID will be prioritized.
        if embed_id is None:
            # TODO: Get Embed data via name -> None if it does not exist
            embed_data: typing.Optional[dict]
        else:
            # TODO: Get Embed data via id -> None if it does not exist
            embed_data: typing.Optional[dict]

        # Check if embed exists
        if embed_data is None:
            await modal.interaction.response.send_message("Embed does not exists.", ephemeral=True)
            return
        await modal.interaction.response.defer()
        embed: discord.Embed = discord.Embed.from_dict(embed_data["value"])
        # Set current db embed data -> Gets used when saving the embed after editing.
        self.current_db_embed_data = {"id": embed_id, "name": embed_name}
        # Send the new embed with the Button Press Interaction.
        self.embed_message = await self.send_embed(embed, interaction)
        # Saftey check if embed could not be sent. Should be correctly in databse thought.
        if self.embed_message is None:
            await modal.interaction.followup.send("Embed could not be sent.", ephemeral=True)
            return
        # Set the View to edit embed Mode.
        await self.set_edit_embed_view()

    # Delete
    async def delete(self, interaction: discord.Interaction) -> None:
        """
        Gets executed on button delete press.
        Sends a Modal which asks the database data for the embed. These will be checked to be existing.
        If they are correct, the embed will be loaded and send.
        After that the delete button will be deleted and a delet_confirm Button will be added to the View.

        :param interaction: discord.Interaction -> The current Interaction. No Followup.
        :return:
        """

        # User input via Modal - ID and Name
        modal = delete_action.EmbedUiModalDelete()
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validation
        embed_name: str = modal.children[1].value
        embed_id: typing.Optional[int] = None
        if len(modal.children[0].value) > 0:
            try:
                # Check if ID is int
                embed_id = int(modal.children[0].value)
            except ValueError:
                await modal.interaction.response.send_message("ID is not Integer!", ephemeral=True)
                return
        # Get embed from Database - ID will be prioritized.
        if embed_id is None:
            # TODO: Get Embed data via name -> None if it does not exist
            embed_data: typing.Optional[dict]
        else:
            # TODO: Get Embed data via id -> None if it does not exist
            embed_data: typing.Optional[dict]
        # Check if embed exists
        if embed_data is None:
            await modal.interaction.response.send_message("Embed does not exists.", ephemeral=True)
            return
        embed: discord.Embed = discord.Embed.from_dict(embed_data["value"])
        # Set current db embed data -> Gets used when saving the embed after editing.
        self.current_db_embed_data = {"id": embed_id, "name": embed_name}
        await modal.interaction.response.defer()
        # Send the new embed with the Button Press Interaction.
        self.embed_message = await self.send_embed(embed, interaction)
        # Saftey check if embed could not be sent. Should be correctly in databse thought.
        if self.embed_message is None:
            await modal.interaction.followup.send("Embed could not be sent.", ephemeral=True)
            return
        # Remove Delete Button and add delete confirm Button
        await self.remove_except_action_select()
        self.add_item(delete_action.EmbedUiButtonDeleteConfirm())
        await self.message.edit(view=self)

    async def delete_confirmation(self, interaction: discord.Interaction) -> None:
        """
        Deletes the embed in the database which corresponds to the current embed data.
        Deletes conformation Button and adds regular delete Button.
        Removes current embed Message.

        :param interaction: discord.Interaction -> The Interaction to response to with the conformation. No Followup.
        :return:
        """

        # TODO: Delete the Embed in your database (id=self.current_db_embed_data["id"], name=self.current_db_embed_data["name"])
        if type(self.current_embed.image.url) is str:
            if os.path.isfile(f"./daten/saved_pictures/{self.current_embed.image.url[13:]}"):
                os.remove(f"./daten/saved_pictures/{self.current_embed.image.url[13:]}")
        if type(self.current_embed.thumbnail.url) is str:
            if os.path.isfile(f"./daten/saved_pictures/{self.current_embed.thumbnail.url}"):
                os.remove(f"./daten/saved_pictures/{self.current_embed.thumbnail.url}")
        if type(self.current_embed.author.icon_url) is str:
            if os.path.isfile(f"./daten/saved_pictures/{self.current_embed.author.icon_url}"):
                os.remove(f"./daten/saved_pictures/{self.current_embed.author.icon_url}")
        if type(self.current_embed.footer.icon_url) is str:
            if os.path.isfile(f"./daten/saved_pictures/{self.current_embed.footer.icon_url}"):
                os.remove(f"./daten/saved_pictures/{self.current_embed.footer.icon_url}")
        if self.embed_message is not None:
            await self.embed_message.delete()
            self.embed_message = None
        await self.remove_except_action_select()
        self.add_item(delete_action.EmbedUiButtonDelete())
        await self.message.edit(view=self)
        await interaction.response.send_message(f"Embed deleted with data: {self.current_db_embed_data}",
                                                ephemeral=True)

    # Edit Embed

    async def edit_embed(self, interaction: discord.Interaction, default_data: dict = None, wrong_data: list = None) \
            -> None:
        """
        Modifies title, description, color, timestamp and url.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param default_data: dict -> A dictonary with the default data that should be in the Modal before user opening
        it. Default None, the data from the current_embed will be used.
        :param wrong_data: list -> A list of fields that should be displayed as wrong. Default None, no errors will be
        displayed.
        :return:
        """

        # Set default Values
        if default_data is None:
            default_data: dict = {"title": self.current_embed.title, "description": self.current_embed.description,
                                  "url": self.current_embed.url}
        if wrong_data is None:
            wrong_data = []
        # Filter default value for only strings. Color and Timestamp are not stored as str and have to be converted
        filterd_default_data: dict = {key: value for key, value in default_data.items() if type(value) is str}
        if type(self.current_embed.color) is discord.Color:
            filterd_default_data["color"] = str(self.current_embed.color)
        if type(self.current_embed.timestamp) is datetime.datetime:
            filterd_default_data["timestamp"] = self.current_embed.timestamp.isoformat()
        # Ask user for data that should be changed
        modal: edit_embed.ModalEmbedEdit = edit_embed.ModalEmbedEdit(filterd_default_data, wrong_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Return if modal has timeout
        if modal.interaction is None:
            return
        # Input Check
        # The data that should be checked. Title and description are already checked by the Modal.
        check_data: dict = {"color": modal.children[2].value, "timestamp": modal.children[3].value,
                            "url": modal.children[4].value}
        wrong_embed_data: list = await self.check_main_embed_data(check_data) # List with fields that are wrong.
        error_message: typing.Optional[str] = None # The error Message that will be displayed to the user.
        if len(wrong_embed_data) == 0:
            # If no errors were found try to send the embed
            # Deepcopy so the current_embed stays old even if the new embed has errors.
            modify_embed: discord.Embed = copy.deepcopy(self.current_embed)
            modify_embed.title = modal.children[0].value
            modify_embed.description = modal.children[1].value
            if modal.children[2].value != "":
                modify_embed.color = discord.Color(int(hex(int(str(modal.children[2].value)[1:], 16)), 0))
            if modal.children[3].value != "":
                modify_embed.timestamp = datetime.datetime.fromisoformat(modal.children[3].value)
            else:
                modify_embed.timestamp = discord.Embed.Empty
            modify_embed.url = modal.children[4].value
            # Try to send the embed. None if sending had an Error.
            msg: typing.Optional[discord.Message] = await self.send_embed(modify_embed, interaction)
            if msg is None:
                # Add all Options to wrong data - No Information about the reason why the sending had an Error.
                wrong_embed_data = ["title", "description", "color", "timestamp", "url"]
                error_message = "Something went wrong while trying to send the embed!"
            else:
                # Sending was sucessfull, set the current embed and message to the new values. Defer the Interaction.
                self.current_embed = modify_embed
                self.embed_message = msg
                await modal.interaction.response.defer()
                return
        else:
            # Errors were found in the User Input checking. Constructing the Error Message.
            error_message = "Error:\n"
            if "color" in wrong_embed_data:
                error_message += "Color does not have the correct Format.\n"
            if "timestamp" in wrong_embed_data:
                error_message += "Timestamp does not have the correct Format.\n"
            if "url" in wrong_embed_data:
                error_message += "URL does not have the correct Format or is not reachable."
        # Set old data to give as default data to the Retry View.
        old_data: dict = {"title": modal.children[0].value, "description": modal.children[1].value,
                          "color": modal.children[2].value, "timestamp": modal.children[3].value,
                          "url": modal.children[4].value}
        # Send Retry View - This will call this function in the proccess
        retry_type: retry_view.ReplyType = retry_view.ReplyType.normal_edit
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(old_data, retry_type, self, wrong_embed_data)
        await modal.interaction.response.send_message(error_message, view=retry_edit)

    async def edit_author(self, interaction: discord.Interaction, default_data: dict = None, wrong_data: list = None) \
            -> None:
        """
        Modifies the author with asking for image.
        Asks for Author name, Author url with Modal.
        After that asks the User to send an Image as icon.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. NOT FOLLOWUP!
        :param default_data: dict -> A dictonary with the default data that should be in the Modal before user opening
        it. Default None, the data from the current_embed will be used.
        :param wrong_data: list -> A list of fields that should be displayed as wrong. Default None, no errors will be
        displayed.
        :return:
        """

        # Set default Values
        if default_data is None:
            default_data = {"name": self.default_embed.author.name, "url": self.default_embed.author.url,
                            "icon_url": self.default_embed.author.icon_url}
        if wrong_data is None:
            wrong_data = []
        # Ask user for data that should be changed
        modal: edit_embed.ModalAuthorEdit = edit_embed.ModalAuthorEdit(default_data, wrong_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Return if Modal has timeouted
        if modal.interaction is None:
            return
        # If No Value was provided the author gets removed
        if modal.children[0].value == "" and modal.children[1].value == "":
            self.current_embed.remove_author()
            if self.embed_message is not None:
                await self.embed_message.delete()
            await modal.interaction.response.defer()
            self.embed_message = await self.send_embed(self.current_embed, interaction)
            return
        # Get Image via the Image View
        image_view: get_image.GetImageView = get_image.GetImageView(self.bot, interaction.user)
        await modal.interaction.response.send_message("Please send the Image you want in this Channel", view=image_view)
        # Wait for image to finish or for timeout
        await asyncio.wait([image_view.start(), image_view.wait()], return_when=asyncio.FIRST_COMPLETED)
        # Check Data enterd via the modal.
        check_data: dict = {"name": modal.children[0].value, "url": modal.children[1].value}
        wrong_author_data: list = await self.check_author_embed_data(check_data)
        error_message: typing.Optional[str] = None
        if len(wrong_author_data) == 0:
            # No errors were found in the Input Check
            modify_embed: discord.Embed = copy.deepcopy(self.current_embed)
            match image_view.image:
                case None:
                    # No Image was given - Using old Image
                    icon_path = modify_embed.author.icon_url
                case "delete":
                    # Image should be deleted
                    icon_path = discord.Embed.Empty
                    await self.delete_image(modify_embed.author.icon_url)
                case _:
                    # New Image
                    await self.delete_image(modify_embed.author.icon_url)
                    icon_path = f"attachment://{image_view.image}"
                    self.chached_images.append(image_view.image)
            # Set Author
            modify_embed.set_author(name=modal.children[0].value, url=modal.children[1].value, icon_url=icon_path)
            # Send message
            message: discord.Message = await self.send_embed(modify_embed, modal.interaction)
            # Check if sending was succesfull
            if message is None:
                wrong_author_data = ["name", "url"]
                error_message = "Something went wrong while trying to send the embed!"
            else:
                self.current_embed = modify_embed
                self.embed_message = message
                return
        else:
            # Errors were found constructing error Message
            error_message = "ERROR:\n"
            if "name" in wrong_author_data:
                error_message += "Name is not valid\n"
            if "url" in wrong_author_data:
                error_message += "URL is not valid"
        # Sending Retry Message
        retry_type: retry_view.ReplyType = retry_view.ReplyType.author_edit
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(check_data, retry_type, self, wrong_author_data)
        message: discord.Message = await modal.interaction.followup.send(error_message, view=retry_edit)
        retry_edit.message = message

    async def edit_footer(self, interaction: discord.Interaction, default_data: dict = None, wrong_data: list = None) \
            -> None:
        """
        Modifies the footer with asking for image.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param default_data: dict -> A dictonary with the default data that should be in the Modal before user opening
        it. Default None, the data from the current_embed will be used.
        :param wrong_data: list -> A list of fields that should be displayed as wrong. Default None, no errors will be
        displayed.
        :return:
        """

        # Set default Values
        if default_data is None:
            default_data = {"name": self.default_embed.author.name, "icon_url": self.default_embed.author.icon_url}
        if wrong_data is None:
            wrong_data = []
        # Ask user for data that should be changed
        modal: edit_embed.ModalFooterEdit = edit_embed.ModalFooterEdit(default_data, wrong_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Return if Modal has timeouted
        if modal.interaction is None:
            return
        # If No Value was provided the footer gets removed
        if modal.children[0].value == "":
            self.current_embed.remove_footer()
            if self.embed_message is not None:
                await self.embed_message.delete()
            await modal.interaction.response.defer()
            self.embed_message = await self.send_embed(self.current_embed, interaction)
            return
        # Get Image via the Image View
        image_view: get_image.GetImageView = get_image.GetImageView(self.bot, interaction.user)
        await modal.interaction.response.send_message("Please send the Image you want in this Channel", view=image_view)
        # Wait for image to finish or for timeout
        await asyncio.wait([image_view.start(), image_view.wait()], return_when=asyncio.FIRST_COMPLETED)
        # Check Data enterd via the modal.
        check_data: dict = {"text": modal.children[0].value}
        wrong_footer_data: list = await self.check_footer_embed_data(check_data)
        error_message: typing.Optional[str] = None
        if len(wrong_footer_data) == 0:
            # No errors were found in the Input Check
            modify_embed: discord.Embed = copy.deepcopy(self.current_embed)
            match image_view.image:
                case None:
                    # No Image was given - Using old Image
                    icon_path = modify_embed.footer.icon_url
                case "delete":
                    # Image gets deleted
                    icon_path = discord.Embed.Empty
                    await self.delete_image(modify_embed.footer.icon_url)
                case _:
                    # New Image
                    await self.delete_image(modify_embed.footer.icon_url)
                    icon_path = f"attachment://{image_view.image}"
                    self.chached_images.append(image_view.image)
            # Set Footer
            modify_embed.set_footer(text=modal.children[0].value, icon_url=icon_path)
            # Send Message
            msg: discord.Message = await self.send_embed(modify_embed, modal.interaction)
            # Check if sending was succesfull
            if msg is None:
                wrong_footer_data = ["text"]
                error_message = "Something went wrong while trying to send the embed!"
            else:
                self.current_embed = modify_embed
                self.embed_message = msg
                return
        else:
            # Errors were found constructing error Message
            error_message = "ERROR:\n"
            if "name" in wrong_footer_data:
                error_message += "Text is not valid\n"
        # Sending Retry Message
        retry_type: retry_view.ReplyType = retry_view.ReplyType.footer_edit
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(check_data, retry_type, self, wrong_footer_data)
        msg: discord.Message = await modal.interaction.followup.send(error_message, view=retry_edit)
        retry_edit.message = msg

    async def edit_image(self, interaction: discord.Interaction) -> None:
        """
        Asks for an Image for the Embed.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup!
        :return:
        """

        # Get Image View
        image_view: get_image.GetImageView = get_image.GetImageView(self.bot, interaction.user)
        await interaction.response.send_message("Please send the Image you want in this Channel", view=image_view)
        # Wait for Timeout or View to finish
        await asyncio.wait([image_view.start(), image_view.wait()], return_when=asyncio.FIRST_COMPLETED)
        error_message: typing.Optional[str] = None
        modify_embed: discord.Embed = copy.deepcopy(self.current_embed)
        match image_view.image:
            case None:
                # Old Image stays.
                pass
            case "delete":
                # Image gets deleted
                await self.delete_image(modify_embed.image.url)
                modify_embed.remove_image()
            case _:
                # New Image was given
                await self.delete_image(modify_embed.image.url)
                icon_path = f"attachment://{image_view.image}"
                modify_embed.set_image(url=icon_path)
                self.chached_images.append(image_view.image)
        # Try to send the embed.
        msg: discord.Message = await self.send_embed(modify_embed, interaction)
        # Check if sending was successfull and construct Error Message.
        if msg is None:
            error_message = "Something went wrong while trying to send the embed!"
        else:
            self.embed_message = msg
            self.current_embed = modify_embed
            return
        # Send Retry View
        retry_type: retry_view.ReplyType = retry_view.ReplyType.footer_edit
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(None, retry_type, self, [])
        msg: discord.Message = await interaction.followup.send(error_message, view=retry_edit)
        retry_edit.message = msg

    async def edit_thumbnail(self, interaction: discord.Interaction) -> None:
        """
        Asks for a Thumbnail.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :return:
        """

        # Get Image View
        image_view: get_image.GetImageView = get_image.GetImageView(self.bot, interaction.user)
        await interaction.response.send_message("Please send the Image you want in this Channel", view=image_view)
        # Wait for View to finish or timeout
        await asyncio.wait([image_view.start(), image_view.wait()], return_when=asyncio.FIRST_COMPLETED)
        error_message: typing.Optional[str] = None
        modify_embed: discord.Embed = copy.deepcopy(self.current_embed)
        match image_view.image:
            case None:
                # Old Image stays
                pass
            case "delete":
                # Image gets deleted
                await self.delete_image(modify_embed.thumbnail.url)
                modify_embed.remove_thumbnail()
            case _:
                # New Image was given
                await self.delete_image(modify_embed.thumbnail.url)
                icon_path = f"attachment://{image_view.image}"
                modify_embed.set_thumbnail(url=icon_path)
                self.chached_images.append(image_view.image)
        # Try to send the Embed
        msg: discord.Message = await self.send_embed(modify_embed, interaction)
        # Check if sending the Embed was succesfull and construct Error Message.
        if msg is None:
            error_message = "Something went wrong while trying to send the embed!"
        else:
            self.current_embed = modify_embed
            self.embed_message = msg
            return
        # Send Retry View
        retry_type: retry_view.ReplyType = retry_view.ReplyType.footer_edit
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(None, retry_type, self, [])
        msg: discord.Message = await interaction.followup.send(error_message, view=retry_edit)
        retry_edit.message = msg

    async def modify_field(self, interaction: discord.Interaction, current_field_index: int, default_data: dict = None,
                           wrong_data: list = None) -> None:
        """
        Modifies the currently selected Field.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param current_field_index: int -> The current Field for the Modification.
        :param default_data: dict -> A dictonary with the default data that should be in the Modal before user opening
        it. Default None, the data from the current_embed will be used.
        :param wrong_data: list -> A list of fields that should be displayed as wrong. Default None, no errors will be
        displayed.
        :return:
        """

        # Set default Variables
        if default_data is None:
            default_data = {"name": self.current_embed.fields[current_field_index].name,
                            "value": self.current_embed.fields[current_field_index].value}
        if wrong_data is None:
            wrong_data = []
        # Ask User Input with Modal
        modal: edit_embed.ModalFieldEdit = edit_embed.ModalFieldEdit(default_data, wrong_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Return if Modal Timeouts
        if modal.interaction is None:
            return
        # Modify Field
        copy_embed: discord.Embed = copy.deepcopy(self.current_embed)
        copy_embed.set_field_at(index=current_field_index, name=modal.children[0].value, value=modal.children[1].value,
                                inline=self.current_embed.fields[current_field_index].inline)
        # Try to send the embed
        msg: discord.Message = await self.send_embed(copy_embed, interaction)
        wrong_embed_data: list = []
        error_message: typing.Optional[str] = None
        # Check if Embed got send succesfully
        if msg is None:
            # Sending the Embed failed - Constructing Error Message
            wrong_embed_data = ["name", "value"]
            error_message = "Something went wrong while trying to send the embed!"
        else:
            # Set new embed + embed message
            self.embed_message = msg
            await modal.interaction.response.defer()
            await self.message.edit(view=self)
            return
        # Sending retry view
        old_data: dict = {"name": modal.children[0].value, "value": modal.children[1].value, "index": current_field_index}
        retry_type: retry_view.ReplyType = retry_view.ReplyType.modify_field
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(old_data, retry_type, self, wrong_embed_data)
        await modal.interaction.response.send_message(error_message, view=retry_edit)

    async def modify_inline_field(self, interaction: discord.Interaction, current_field_index: int, inlane_value: bool)\
            -> None:
        """
        Modiefies the current embed inline parameter.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param current_field_index: int -> The current Field for the Modification.
        :param inlane_value: bool -> The value to change the inline to.
        :return:
        """

        # Storing old value of the field
        name = self.current_embed.fields[current_field_index].name
        value = self.current_embed.fields[current_field_index].value
        # Set new Value of field
        self.current_embed.set_field_at(index=current_field_index, name=name, value=value, inline=inlane_value)
        # Defer Interaction and send new message
        await interaction.response.defer()
        self.embed_message = await self.send_embed(self.current_embed, interaction)
        # Editing Message so the changed Button gets displayed
        await self.message.edit(view=self)

    async def remove_field(self, interaction: discord.Interaction, current_field_index: int) -> None:
        """
        Removes the Field.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param current_field_index: int -> The current Field for the Modification.
        :return:
        """

        # Remove The field
        self.current_embed.remove_field(index=current_field_index)
        # Defer interaction and send the new Embed
        await interaction.response.defer()
        self.embed_message = await self.send_embed(self.current_embed, interaction)
        # Reseting the SelectFieldEdit to not show the deleted field anymore
        await self.remove_row(3)
        self.add_item(edit_embed.SelectFieldEdit(len(self.current_embed.fields)))
        # Removing the delete Button
        await self.remove_row(4)
        self.add_item(edit_embed.ButtonEmbedSave())
        self.add_item(edit_embed.ButtonEmbedSaveRename())
        # Edit the Message to show the new View
        await self.message.edit(view=self)

    async def add_field(self, interaction: discord.Interaction, default_data: dict = None) -> None:
        """
        Adds a Field to the embed.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :param default_data: dict -> The Default data if the creation failed.
        :return:
        """

        # Set default Parameter
        if default_data is None:
            default_data = {}
        # Modal to ask User
        modal: edit_embed.ModalFieldEdit = edit_embed.ModalFieldEdit(default_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Return if Modal Timeouts
        if modal.interaction is None:
            return
        # Add the new Field
        copy_embed: discord.Embed = copy.deepcopy(self.current_embed)
        copy_embed.add_field(name=modal.children[0].value, value=modal.children[1].value)
        # Send Message
        msg: discord.Message = await self.send_embed(copy_embed, interaction)
        wrong_embed_data: list = []
        error_message: typing.Optional[str] = None
        if msg is None:
            # Message could not be sent
            wrong_embed_data = ["name", "value"]
            error_message = "Something went wrong while trying to send the embed!"
        else:
            # Succesfully send set all current variables to new value and defer Interaction
            self.embed_message = msg
            await modal.interaction.response.defer()
            self.current_embed = copy_embed
            # Set the Mode to Edit
            await self.set_edit_embed_view()
            await self.set_edit_field_view(len(self.current_embed.fields) - 1)
            return
        # Sending failed Retry View
        old_data: dict = {"name": modal.children[0], "value": modal.children[1]}
        retry_type: retry_view.ReplyType = retry_view.ReplyType.add_field
        retry_edit: retry_view.RetryEditView = retry_view.RetryEditView(old_data, retry_type, self, wrong_embed_data)
        await modal.interaction.response.send_message(error_message, view=retry_edit)

    async def save_embed(self, interaction: discord.Interaction) -> None:
        """
        Saves the current Embed.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :return:
        """

        # Loding old Embed data
        # TODO: Load the old Embed data from Database
        old_embed_data: dict
        old_embed: discord.Embed = discord.Embed.from_dict(old_embed_data)

        # Saving the Embed in database
        # TODO: Save the embed in the Database -> result should be None if error
        result: typing.Optional[dict]
        # Checking if the save was succesfull
        if result is None:
            await interaction.response.send_message("Something went wrong while trying to save the embed.",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("Succesfully saved the Embed!", ephemeral=True)
            # Saving pictures
            if type(self.current_embed.image.url) is str:
                await self.save_image(self.current_embed.image.url)
            if type(self.current_embed.thumbnail.url) is str:
                await self.save_image(self.current_embed.thumbnail.url)
            if type(self.current_embed.author.icon_url) is str:
                await self.save_image(self.current_embed.author.icon_url)
            if type(self.current_embed.footer.icon_url) is str:
                await self.save_image(self.current_embed.footer.icon_url)
            # Deleting Pictures
            if old_embed.image.url != self.current_embed.image.url:
                if type(old_embed.image.url) is str:
                    if os.path.isfile(f"./daten/saved_pictures/{old_embed.image.url[13:]}"):
                        os.remove(f"./daten/saved_pictures/{old_embed.image.url[13:]}")
            if old_embed.thumbnail.url != self.current_embed.thumbnail.url:
                if type(old_embed.image.url) is str:
                    if os.path.isfile(f"./daten/saved_pictures/{old_embed.thumbnail.url[13:]}"):
                        os.remove(f"./daten/saved_pictures/{old_embed.thumbnail.url[13:]}")
            if old_embed.author.icon_url != self.current_embed.author.icon_url:
                if type(old_embed.image.url) is str:
                    if os.path.isfile(f"./daten/saved_pictures/{old_embed.author.icon_url[13:]}"):
                        os.remove(f"./daten/saved_pictures/{old_embed.author.icon_url[13:]}")
            if old_embed.footer.icon_url != self.current_embed.footer.icon_url:
                if type(old_embed.image.url) is str:
                    if os.path.isfile(f"./daten/saved_pictures/{old_embed.footer.icon_url[13:]}"):
                        os.remove(f"./daten/saved_pictures/{old_embed.footer.icon_url[13:]}")

    async def save_rename_embed(self, interaction: discord.Interaction) -> None:
        """
        Saves the current Embed.

        :param interaction: discord.Interaction -> The current Interaction the modal will be sent to. No Followup.
        :return:
        """

        # Loding old Embed data
        # TODO: Load the old Embed data from Database
        old_embed_data: dict
        old_embed: discord.Embed = discord.Embed.from_dict(old_embed_data)
        # User input via Modal - ID and Name
        modal = edit_embed.EmbedUiModalRename(self.current_db_embed_data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validation - Has to be unique in the Database
        embed_name: str = modal.children[1].value
        try:
            # Check if ID is int
            embed_id: int = int(modal.children[0].value)
        except ValueError:
            await modal.interaction.response.send_message("ID is not Integer!", ephemeral=True)
            return
        # TODO: Check if id exists in Database -> If not exist_embed_id should be None
        exist_embed_id: typing.Optional[dict]
        if exist_embed_id is not None:
            await modal.interaction.response.send_message("Embed id already exists.", ephemeral=True)
            return
        # TODO: Check if name exists in Database -> If not exist_embed_name should be None
        exist_embed_name: typing.Optional[dict]
        if exist_embed_name is not None:
            await modal.interaction.response.send_message("Embed name already exists.", ephemeral=True)
            return

        # Saving the Embed in database
        # TODO: Save the embed in the Database -> result should be None if error
        result: typing.Optional[dict]
        # Checking if the save was succesfull
        if result is None:
            await modal.interaction.response.send_message("Something went wrong while trying to save the embed.",
                                                    ephemeral=True)
        else:
            await modal.interaction.response.send_message("Succesfully saved the Embed!", ephemeral=True)
            # TODO: Delete the embed in the Database (id=self.current_db_embed_data["id"], name=self.current_db_embed_data["name"])
            self.current_db_embed_data["id"] = embed_id
            self.current_db_embed_data["name"] = embed_name
            # Saving pictures
            if type(self.current_embed.image.url) is str:
                await self.save_image(self.current_embed.image.url)
            if type(self.current_embed.thumbnail.url) is str:
                await self.save_image(self.current_embed.thumbnail.url)
            if type(self.current_embed.author.icon_url) is str:
                await self.save_image(self.current_embed.author.icon_url)
            if type(self.current_embed.footer.icon_url) is str:
                await self.save_image(self.current_embed.footer.icon_url)
            # Deleting Pictures
            if old_embed.image.url != self.current_embed.image.url:
                if os.path.isfile(f"./daten/saved_pictures/{old_embed.image.url[13:]}"):
                    os.remove(f"./daten/saved_pictures/{old_embed.image.url[13:]}")
            if old_embed.thumbnail.url != self.current_embed.thumbnail.url:
                if os.path.isfile(f"./daten/saved_pictures/{old_embed.thumbnail.url[13:]}"):
                    os.remove(f"./daten/saved_pictures/{old_embed.thumbnail.url[13:]}")
            if old_embed.author.icon_url != self.current_embed.author.icon_url:
                if os.path.isfile(f"./daten/saved_pictures/{old_embed.author.icon_url[13:]}"):
                    os.remove(f"./daten/saved_pictures/{old_embed.author.icon_url[13:]}")
            if old_embed.footer.icon_url != self.current_embed.footer.icon_url:
                if os.path.isfile(f"./daten/saved_pictures/{old_embed.footer.icon_url[13:]}"):
                    os.remove(f"./daten/saved_pictures/{old_embed.footer.icon_url[13:]}")

    # Checks

    @staticmethod
    async def check_main_embed_data(data: dict) -> list:
        """
        Checks if the data provided fits the requirements to add it to an embed, specifically for main embed data.

        :param data: dict -> The data that should be checked.
        :return: list -> Returns a list of fields with errors, if the list is empty no error was found.
        """

        # A list of all wrong fields
        false_data: list = []
        # Matches the Color value to be a Hexadecimal Color Code
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", data["color"]) and data["color"] != "":
            false_data.append("color")
        # Checks if the timestamp is a valid iso format
        if data["timestamp"] != "":
            try:
                timestamp: datetime = datetime.datetime.fromisoformat(data["timestamp"])
            except ValueError:
                false_data.append("timestamp")
        # Checks if the url has the right sheme - Does not check if the url is reachable
        if data["url"] != "":
            url_parse = urlparse(data["url"])
            if url_parse.scheme not in ["http", "https"]:
                false_data.append("url")
        return false_data

    @staticmethod
    async def check_author_embed_data(data: dict) -> list:
        """
        Checks if the data provided fits the requirements to add it to an embed, specifically for author data.

        :param data: dict -> The data that should be checked.
        :return: list -> Returns a list of fields with errors, if the list is empty no error was found.
        """

        # A list of all wrong fields
        false_data: list = []
        # Checks if the url has the right sheme
        if data["url"] != "":
            url_parse = urlparse(data["url"])
            if url_parse.scheme != "https":
                false_data.append("url")
        return false_data

    @staticmethod
    async def check_footer_embed_data(data: dict) -> list:
        """
        Checks if the data provided fits the requirements to add it to an embed, specifically for author data.
        Currently only returns an empty list - could be used to add checks.

        :param data: dict -> The data that should be checked.
        :return: list -> Returns a list of fields with errors, if the list is empty no error was found.
        """
        false_data: list = []
        return false_data

    @staticmethod
    async def save_image(icon_url: str) -> None:
        """
        Saves the Image in saved_pictures.

        :param icon_url:
        :return:
        """

        if type(icon_url) is str:
            if os.path.isfile(f"./daten/pictures/{icon_url[13:]}"):
                shutil.move(f"./daten/pictures/{icon_url[13:]}", f"./daten/saved_pictures/{icon_url[13:]}")
