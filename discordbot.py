from discord.ext import commands
import discord
import os
import traceback
import numpy as np
import cv2
import io

bot = commands.Bot(command_prefix='$dip')
token = os.environ['DISCORD_BOT_TOKEN']

blankPicture=np.zeros([1000,1000, 3])

savedPictureName="EztakJ-VoAYSg9R.jpeg"

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def pic(ctx):
    fileObj = discord.File(savedPictureName)
    await ctx.send(file=fileObj)
    
@bot.command()
async def pic2(ctx):
    fileObj = discord.File(io.BytesIO(blankPicture),filename="blank.png")
    await ctx.send(file=fileObj)

bot.run(token)
