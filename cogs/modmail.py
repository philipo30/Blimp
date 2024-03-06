import datetime
from datetime import datetime
import os

from discord.ext import commands
from discord.ext.commands import Context, context
from discord import utils, Embed, Colour
import discord

from config import your_guild_id


class confirm(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red, custom_id="confirm")
    async def confirm_button(self, interaction, button):
        guild = interaction.guild  # Use interaction.guild instead of self.bot.get_guild(your_guild_id)
        if guild:
            categ = utils.get(guild.categories, name="Modmail tickets")
            logs_channel = utils.get(categ.channels, topic="modmail-logs")
            closelogembed = Embed(title=f"{interaction.channel.name} is now deleted",
                                  timestamp=datetime.utcnow())
            closelogembed.set_footer(text='Text Channel Deletion',
                                     icon_url="https://cdn.discordapp.com/emojis/1139951866390794442.webp?size=128&quality=lossless")
            try:
                await interaction.channel.delete()
                await logs_channel.send(embed=closelogembed)
                if os.path.exists(f"{logs_channel.id}.md"):
                    return await logs_channel.send(f"A transcript is already being generated")
                with open(f"{logs_channel.id}.md", "a") as f:
                    f.write(f"# Transcript of {logs_channel.name}:\n\n")
                    async for message in logs_channel.history(limit=None, oldest_first=True):
                        created = datetime.strftime(message.created_at, "%m/%d/%Y at %H:%M:%S")
                        if message.edited_at:
                            edited = datetime.strftime(message.edited_at, "%m/%d/%Y at %H:%M:%S")
                            f.write(f"{message.author} on {created}: {message.clean_content} (Edited at {edited})\n")
                        else:
                            f.write(f"{message.author} on {created}: {message.clean_content}\n")
                    generated = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
                    f.write(
                        f"\n*Generated at {generated} by {self.bot.user}*\n*Date Formatting: MM/DD/YY*\n*Time Zone: UTC*")
                with open(f"{logs_channel.id}.md", "rb") as f:
                    #await  logs_channel.send(file=discord.File(f, f"{context.channel.name}.md"))
                    await logs_channel.send("test")
            except:
                await interaction.response.send_message(
                    "Channel deletion failed! Make sure I have `manage_channels` permission!", ephemeral=True)
        else:
            print("Guild not found. Check your guild ID configuration.")


class modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        self.bot.command_prefix = self.bot.config["prefix"]
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            guild = self.bot.get_guild(your_guild_id)
            categ = utils.get(guild.categories, name="Modmail tickets")
            if not categ:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                categ = await guild.create_category(name="Modmail tickets", overwrites=overwrites)

            channel = utils.get(categ.channels, topic=str(message.author.id))
            if not channel:
                channel = await categ.create_text_channel(name=f"{message.author.name}#{message.author.discriminator}",
                                                          topic=str(message.author.id))
                newmodmailembed = Embed(title="New Modmail ticket created!",
                                        description=f"{message.author.mention}",
                                        color=Colour(int("2B2D31", 16))
                                        )
                await channel.send(embed=newmodmailembed)

            embed = Embed(description=message.content, color=Colour(int("2B2D31", 16)))
            embed.set_author(name=message.author, icon_url=message.author.avatar)
            await channel.send(embed=embed)
            delivery_embed = Embed(title="Message Delivered",
                                   description="Your message has been successfully delivered.", color=Colour.green())
            await message.author.send(embed=delivery_embed)

            logs_channel = utils.get(categ.channels, topic="modmail-logs")
            if not logs_channel:
                overwrites_logs = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                logs_channel = await categ.create_text_channel(name="modmail-logs", overwrites=overwrites_logs,
                                                               topic="modmail-logs")
                embed = Embed(title="Modmail logs will be recorded here")
                await logs_channel.send(embed=embed)

        elif isinstance(message.channel, discord.TextChannel):
            if message.content.startswith(self.bot.command_prefix):
                pass
            else:
                topic = message.channel.topic
                if topic:
                    member = message.guild.get_member(int(topic))
                    if member:
                        await member.send(f'**{message.author}**: {message.content}')

    @commands.hybrid_command(name="close", description="Closes a modmail ticket.")
    async def close(self, context: Context):
        if context.channel.category.name == "Modmail tickets":
            closeembed = discord.Embed(title="Are you sure you want to close this ticket?",
                                       colour=discord.Color.red())
            await context.send(embed=closeembed, view=confirm(None), ephemeral=True)
        else:
            await context.send("This isn't a ticket!", ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(modmail(bot))
