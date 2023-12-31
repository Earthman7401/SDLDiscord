"""
Contains the cog for server configuration commands and a setup function to load the extension.
"""
import json

import discord
from discord.ext import commands

DEFAULT_PREFIX = '$'


class Configs(commands.Cog, name = 'Config Commands'):
    """
    Commands for configuring the bot for the discord server.
    These commands should only be accessible to moderators or members with the administrator permission.
    """
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client

    def cog_check(self, ctx: commands.Context) -> bool:
        """
        Checks if user has permission to use commands in this cog.

        Args:
            ctx (commands.Context): The commands.Context provided by command invocation.

        Returns:
            bool: Whether the user meets the requirements to use the commands.
        """
        with open('/app/data/mod_roles.json', 'r', encoding = 'UTF-8') as infile:
            mod_roles = json.load(infile)

            # get the intersection of mod_roles and ctx.author.roles
            if ctx.guild.id in mod_roles:
                intersection = [role for role in ctx.author.roles if str(role.id) in mod_roles[str(ctx.guild.id)]]
            else:
                intersection = []
            return len(intersection) > 0 or ctx.author.guild_permissions.administrator

    @commands.hybrid_command(name = 'prefix')
    async def change_prefix(self, ctx: commands.Context, new_prefix: str) -> None:
        """
        Changes the server-specific prefix for the discord server this is called in.

        Args:
            ctx (commands.Context): The commands.Context provided by command invocation.
            new_prefix (str): The new prefix to set for the discord server.
        """
        response_message = ''
        try:
            with open('/app/data/prefixes.json', 'r+', encoding = 'UTF-8') as file:
                prefixes = json.load(file)
                prefixes[str(ctx.guild.id)] = new_prefix

                # overwrite file with new data
                file.seek(0)
                file.truncate()
                json.dump(prefixes, file)
        except IOError:
            response_message = 'Exception when updating prefix'
        else:
            response_message = f'Prefix successfully set to {new_prefix}'

        if ctx.interaction is not None:
            await ctx.interaction.response.send_message(response_message)
        else:
            await ctx.send(response_message)

    @commands.hybrid_command(name = 'addmodrole')
    async def add_mod_role(self, ctx: commands.Context) -> None:
        """
        Adds a role to the list of moderator roles for the discord server this is called in.
        Creates a dropdown list that lets the user pick from all roles in the server.

        Args:
            ctx (commands.Context): The commands.Context provided by command invocation.
        """
        selection = discord.ui.RoleSelect()
        view = discord.ui.View()

        async def callback(interaction):
            try:
                with open('/app/data/mod_roles.json', 'r+', encoding = 'UTF-8') as file:
                    role_list = json.load(file)

                    # create list if it doesn't exist
                    if str(interaction.guild_id) not in role_list:
                        role_list[str(interaction.guild_id)] = []

                    if str(selection.values[0].id) not in role_list[str(interaction.guild_id)]:
                        role_list[str(interaction.guild_id)].append(str(selection.values[0].id))
                        await interaction.response.send_message(f'Successfully added {selection.values[0].name} to mod roles')
                    else:
                        await interaction.response.send_message(f'{selection.values[0].name} already added')

                    # overwrite file with new data
                    file.seek(0)
                    file.truncate()
                    json.dump(role_list, file)
            except IOError:
                await interaction.response.send_message('Exception when updating mod roles')

        selection.callback = callback
        view.add_item(selection)

        if ctx.interaction is not None:
            await ctx.interaction.response.send_message('Choose a role to add to the list of mod roles', view = view)
        else:
            await ctx.send('Choose a role to add to the list of mod roles', view = view)

    @commands.hybrid_command(name = 'removemodrole')
    async def remove_mod_role(self, ctx: commands.Context) -> None:
        """
        Removes a role from the list of moderator roles for the discord server this is called in.
        Creates a dropdown list that lets the user pick from all roles in the server.

        Args:
            ctx (commands.Context): The commands.Context provided by command invocation.
        """
        selection = discord.ui.RoleSelect()
        view = discord.ui.View()

        async def callback(interaction):
            try:
                with open('/app/data/mod_roles.json', 'r+', encoding = 'UTF-8') as file:
                    role_list = json.load(file)

                    if str(interaction.guild_id) not in role_list or role_list[str(interaction.guild_id)] == []:
                        await interaction.response.send_message('No mod roles set')

                    if str(selection.values[0].id) in role_list[str(interaction.guild_id)]:
                        role_list[str(interaction.guild_id)].remove(str(selection.values[0].id))
                        await interaction.response.send_message(f'Successfully removed {selection.values[0].name} from mod roles')
                    else:
                        await interaction.response.send_message(f'{selection.values[0].name} not found in mod roles')

                    # overwrite file with new data
                    file.seek(0)
                    file.truncate()
                    json.dump(role_list, file)
            except IOError:
                await interaction.response.send_message('exception when updating mod roles')

        selection.callback = callback
        view.add_item(selection)

        if ctx.interaction is not None:
            await ctx.interaction.response.send_message('Choose a role to remove from the list of mod roles', view = view)
        else:
            await ctx.send('Choose a role to add to the list of mod roles', view = view)

    @commands.hybrid_command(name = 'modroles')
    async def mod_roles(self, ctx: commands.Context) -> None:
        """
        Shows the list of moderator roles for the discord server.

        Args:
            ctx (commands.Context): The commands.Context provided by command invocation.
        """
        embed = discord.Embed()

        with open('/app/data/mod_roles.json', 'r', encoding = 'UTF-8') as infile:
            role_list = json.load(infile)

            # get mention strings of roles, separated by newline
            if str(ctx.guild.id) not in role_list:
                role_mentions = ''
            else:
                role_mentions = '\n'.join([role.mention for role in [discord.utils.get(ctx.guild.roles, id = int(id)) for id in role_list[str(ctx.guild.id)]]])
            embed.add_field(name = 'Roles', value = role_mentions)
        await ctx.send(embed = embed, allowed_mentions = discord.AllowedMentions.all())

async def setup(client):
    """
    Loads the cog Configs into the bot.

    This is automatically called by commands.Bot.load_extension() and **is not meant to be called directly**.

    Args:
        client (commands.Bot): The bot to load the cog into.
    """
    await client.add_cog(Configs(client))
