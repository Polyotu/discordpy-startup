from discord.ext import commands,tasks
import discord
import datetime
from datetime import datetime
import subprocess
import sys
import os
import math
import asyncio
from io import BytesIO


class MyCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        #self.bot.remove_command("help")

    
def setup(bot):
    return bot.add_cog(MyCog(bot))

