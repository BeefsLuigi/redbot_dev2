from redbot.core import commands
import discord
import asyncio


class MyCog(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    #@commands.group(invoke_without_command=True, require_var_positional=True)
    async def mycog(self, ctx):
        """This does stuff!"""
        # Your code will go here
        await ctx.send("I can do stuff!")

        #fart

        #dsasdfasfas
        #dfasdfaksldjblnbab

    @mycog.command(name="test1")
    async def test1(self, ctx, *, args):
        """test1"""

        await ctx.send("test 1 successful...")
        pass