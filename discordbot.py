from discord.ext import commands
import discord
import os
import traceback
import numpy as np
import cv2
import io
import random
import copy

bot = commands.Bot(command_prefix='##')
token = os.environ['DISCORD_BOT_TOKEN']

height=500
width=500
blank=np.zeros([width,height, 3])
canvas=np.zeros([width,height, 3])

savedPictureName="EztakJ-VoAYSg9R.jpeg"

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    """pongって応答するだけ"""
    await ctx.send('pong 13:53')

@bot.command()
async def pic(ctx):
    """事前にディレクトリ内に保存されたほぼ真っ白画像を返す"""
    fileObj = discord.File(savedPictureName)
    await ctx.send(file=fileObj)
    
@bot.command()
async def pic2(ctx):
    """現在のキャンバスの状態を返す，初期化済みの場合真っ黒"""
    global canvas
    _, num_bytes = cv2.imencode('.jpeg', canvas)
    num_bytes = num_bytes.tobytes()
    fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
    await ctx.send(file=fileObj)
    
@bot.command()
async def line(ctx):
    """キャンバスにランダムな線を1本上書きして返す"""
    global canvas
    global width
    global height
    pointA=(random.randint(1,width-1),random.randint(1,height-1))
    pointB=(random.randint(1,width-1),random.randint(1,height-1))
    lineColor=(random.randint(0,1)*255,random.randint(0,1)*255,random.randint(0,1)*255)
    canvas=cv2.line(
        canvas,
        pointA,
        pointB,
        lineColor,
        2
    )
    _, num_bytes = cv2.imencode('.jpeg',canvas)
    num_bytes = num_bytes.tobytes()
    fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
    await ctx.send("pointA:"+String(pointA)+" pointB:"+String(pointB))
    await ctx.send(file=fileObj)
    
@bot.command()
async def rect(ctx):
    """キャンバスにランダムな直方体を1つ上書きして返す"""
    global canvas
    global width
    global height
    pointA=(random.randint(1,width-1),random.randint(1,height-1))
    pointB=(random.randint(1,width-1),random.randint(1,height-1))
    canvas=cv2.rectangle(
        canvas,
        pointA,
        pointB,
        (255,255,255),
        2
    )
    _, num_bytes = cv2.imencode('.jpeg',canvas)
    num_bytes = num_bytes.tobytes()
    fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
    await ctx.send(file=fileObj)
    
@bot.command()
async def clear(ctx):
    """キャンバスを初期化して返す"""
    global canvas
    canvas=copy.deepcopy(blank)
    _, num_bytes = cv2.imencode('.jpeg',canvas)
#     canvas=copy.deepcopy(clearedCanvas)
    num_bytes = num_bytes.tobytes()
    fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
    await ctx.send(file=fileObj)

bot.run(token)
