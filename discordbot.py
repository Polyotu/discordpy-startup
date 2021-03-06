from discord.ext import commands
import discord
import os
import traceback
import numpy as np
import cv2
import io
import random
import copy
from datetime import datetime

INITIAL_EXTENSIONS = [
    'cogs.cog',
]

class MyBot(commands.Bot):
    def __init__(self,command_prefix,intents):
        super().__init__(command_prefix,case_insensitive=True,intents=intents)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('-------')
    
# #     @bot.event
#     async def on_command_error(ctx, error):
#         orig_error = getattr(error, "original", error)
#         error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
#         await ctx.send(error_msg)

if __name__ == '__main__':
    intents=discord.Intents.all()
    bot = MyBot(command_prefix='##',intents=intents)
    bot.run(os.environ['DISCORD_BOT_TOKEN'])

# from discord.ext import commands
# import discord
# import os
# import traceback
# import numpy as np
# import cv2
# import io
# import random
# import copy
# from datetime import datetime

# bot = commands.Bot(command_prefix='##')
# token = os.environ['DISCORD_BOT_TOKEN']
# defaultChannel=os.environ['DISCORD_DEFAULT_CHANNEL']

# height=500
# width=500
# blank=np.zeros([width,height, 3],np.uint8)
# canvas=np.zeros([width,height, 3],np.uint8)
# fillMask=np.zeros([width+2,height+2],np.uint8)

# savedPictureName="EztakJ-VoAYSg9R.jpeg"

# # intents = discord.Intents.all()
# # client = discord.Client(intents=intents)
# standbyLog=datetime.now()

# colorSet=[
#     (0,0,255),
#     (0,165,255),
#     (0,255,255),
#     (0,128,0),
#     (255,255,0),
#     (255,0,0),
#     (128,0,128)   
# ]

# @bot.event
# async def on_command_error(ctx, error):
#     orig_error = getattr(error, "original", error)
#     error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
#     await ctx.send(error_msg)

# @bot.event
# async def on_ready():
#     global standbyLog
#     garv = bot.get_channel(defaultChannel)
#     standbyLog=datetime.now()
#     log=str(standbyLog)
#     await garv.send(log+"loggedin")
    
# @bot.command()
# async def ping(ctx):
#     """pongって応答するだけ"""
#     await ctx.send('pong'+str(standbyLog))

# @bot.command()
# async def pic(ctx):
#     """事前にディレクトリ内に保存されたほぼ真っ白画像を返す"""
#     fileObj = discord.File(savedPictureName)
#     await ctx.send(file=fileObj)
    
# @bot.command()
# async def pic2(ctx):
#     """現在のキャンバスの状態を返す，初期化済みの場合真っ黒"""
#     global canvas
#     _, num_bytes = cv2.imencode('.jpeg', canvas)
#     num_bytes = num_bytes.tobytes()
#     fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#     await ctx.send(file=fileObj)
    
# @bot.command()
# async def line(ctx):
#     """キャンバスにランダムな線を1本上書きして返す"""
#     global canvas
#     global width
#     global height
#     pointA=(random.randint(1,width-1),random.randint(1,height-1))
#     pointB=(random.randint(1,width-1),random.randint(1,height-1))
#     lineColor=colorSet[random.randint(0,6)]
#     canvas=cv2.line(
#         canvas,
#         pointA,
#         pointB,
#         lineColor,
#         2
#     )
#     canvas=cv2.convertScaleAbs(canvas)
#     _, num_bytes = cv2.imencode('.jpeg',canvas)
#     num_bytes = num_bytes.tobytes()
#     fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#     await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
#     await ctx.send(file=fileObj)
    
# @bot.command()
# async def rect(ctx):
#     """キャンバスにランダムな直方体を1つ上書きして返す"""
#     global canvas
#     global width
#     global height
#     pointA=(random.randint(1,width-1),random.randint(1,height-1))
#     pointB=(random.randint(1,width-1),random.randint(1,height-1))
#     rectColor=colorSet[random.randint(0,6)]
#     canvas=cv2.rectangle(
#         canvas,
#         pointA,
#         pointB,
#         rectColor,
#         2
#     )
#     canvas=cv2.convertScaleAbs(canvas)
#     _, num_bytes = cv2.imencode('.jpeg',canvas)
#     num_bytes = num_bytes.tobytes()
#     fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#     await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
#     await ctx.send(file=fileObj)
    
# @bot.command()
# async def clear(ctx):
#     """キャンバスを初期化して返す"""
#     global canvas
#     canvas=copy.deepcopy(blank)
#     canvas=cv2.convertScaleAbs(canvas)
#     _, num_bytes = cv2.imencode('.jpeg',canvas)
#     num_bytes = num_bytes.tobytes()
#     fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#     await ctx.send(file=fileObj)
    
# @bot.command()
# async def fill(ctx):
#     """ランダムな点を起点に塗りつぶし"""
#     global canvas
#     global fillMask
#     global width
#     global height
#     point=(random.randint(1,width-1),random.randint(1,height-1))
#     fillColor=colorSet[random.randint(0,6)]
#     retval,canvas,mask,rect = cv2.floodFill(image=canvas, mask=fillMask, seedPoint=point, newVal=fillColor,flags=4)
#     canvas=cv2.convertScaleAbs(canvas)
#     _, num_bytes = cv2.imencode('.jpeg',canvas)
#     num_bytes = num_bytes.tobytes()
#     fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#     await ctx.send("point:"+str(point))
#     await ctx.send(file=fileObj)
#     fillMask=np.zeros([width+2,height+2],np.uint8)

# bot.run(token)
