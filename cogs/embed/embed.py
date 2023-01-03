"""
Subcog for all dev embed commands.
"""

import discord
from ui import views
from discord.ext import commands


class ManageEmbed(discord.Cog):
    """
    SlashCommands:
        manage_embed -> starts ui to manage embeds
    """

    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot

    @commands.slash_command()
    async def manage_embed(self, ctx: discord.ApplicationContext):
        """
        Starts the UI for an Embed generation/modification/deletion.
        Takes embed identifier as optional Argument to load a startup embed.

        :param ctx: discord.ApplicationContext -> The Application Context for this Command
        :return:
        """

        view = views.EmbedUi(self.bot, ctx)
        await ctx.respond(view=view)
        await view.start()


def setup(bot: discord.Bot):
    bot.add_cog(ManageEmbed(bot))
