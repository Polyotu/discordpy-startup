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


class MyCog(commands.Cog):
    height=512
    width=512
    blank=np.zeros([width,height, 3],np.uint8)
    canvas=np.zeros([width,height, 3],np.uint8)
    fillMask=np.zeros([width+2,height+2],np.uint8)
    savedPictureName="EztakJ-VoAYSg9R.jpeg"
    standbyLog=datetime.now()
    colorSet=[
        (0,0,255),
        (0,165,255),
        (0,255,255),
        (0,128,0),
        (255,255,0),
        (255,0,0),
        (128,0,128)   
    ]
    
    def __init__(self,bot):
        self.bot=bot
        #self.bot.remove_command("help")
        
    @commands.group()
    async def ping(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('pong'+str(MyCog.standbyLog))
           
    @commands.group() 
    async def pic(self,ctx):
        """事前にディレクトリ内に保存されたほぼ真っ白画像を返す"""
        if ctx.invoked_subcommand is None:
            fileObj = discord.File(MyCog.savedPictureName)
            await ctx.send(file=fileObj)
               
    @commands.group() 
    async def pic2(self,ctx):
        """現在のキャンバスの状態を返す，初期化済みの場合真っ黒"""
        if ctx.invoked_subcommand is None:
#         global canvas
            _, num_bytes = cv2.imencode('.jpeg', MyCog.canvas)
            num_bytes = num_bytes.tobytes()
            fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
            await ctx.send(file=fileObj)

    @commands.group() 
    async def line(self,ctx):
        """キャンバスにランダムな線を1本上書きして返す"""
        if ctx.invoked_subcommand is None:
#             global canvas
#             global width
#             global height
            pointA=(random.randint(1,MyCog.width-1),random.randint(1,MyCog.height-1))
            pointB=(random.randint(1,MyCog.width-1),random.randint(1,MyCog.height-1))
            lineColor=MyCog.colorSet[random.randint(0,6)]
            MyCog.canvas=cv2.line(
                MyCog.canvas,
                pointA,
                pointB,
                lineColor,
                2
            )
            MyCog.canvas=cv2.convertScaleAbs(MyCog.canvas)
            _, num_bytes = cv2.imencode('.jpeg',MyCog.canvas)
            num_bytes = num_bytes.tobytes()
            fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
            await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
            await ctx.send(file=fileObj)
            
    @commands.group() 
    async def rect(self,ctx):
    """キャンバスにランダムな直方体を1つ上書きして返す"""
        if ctx.invoked_subcommand is None:
#             global canvas
#             global width
#             global height
            pointA=(random.randint(1,MyCog.width-1),random.randint(1,MyCog.height-1))
            pointB=(random.randint(1,MyCog.width-1),random.randint(1,MyCog.height-1))
            rectColor=MyCog.colorSet[random.randint(0,6)]
            MyCog.canvas=cv2.rectangle(
                MyCog.canvas,
                pointA,
                pointB,
                rectColor,
                2
            )
            MyCog.canvas=cv2.convertScaleAbs(MyCog.canvas)
            _, num_bytes = cv2.imencode('.jpeg',MyCog.canvas)
            num_bytes = num_bytes.tobytes()
            fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
            await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
            await ctx.send(file=fileObj)
            
    @commands.group() 
    async def fill(self,ctx):
    """ランダムな点を起点に塗りつぶし"""
        if ctx.invoked_subcommand is None:
#             global canvas
#             global fillMask
#             global width
#             global height
            point=(random.randint(1,MyCog.width-1),random.randint(1,MyCog.height-1))
            fillColor=MyCog.colorSet[random.randint(0,6)]
            retval,MyCog.canvas,mask,rect = cv2.floodFill(image=MyCog.canvas, mask=MyCog.fillMask, seedPoint=point, newVal=fillColor,flags=4)
            MyCog.canvas=cv2.convertScaleAbs(MyCog.canvas)
            _, num_bytes = cv2.imencode('.jpeg',MyCog.canvas)
            num_bytes = num_bytes.tobytes()
            fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
            await ctx.send("point:"+str(point))
            await ctx.send(file=fileObj)
            MyCog.fillMask=np.zeros([MyCog.width+2,MyCog.height+2],np.uint8)
    
    @commands.group() 
    async def clear(self,ctx):
    """キャンバスを初期化して返す"""
        if ctx.invoked_subcommand is None:
#             global canvas
            MyCog.canvas=copy.deepcopy(MyCog.blank)
            MyCog.canvas=cv2.convertScaleAbs(MyCog.canvas)
            _, num_bytes = cv2.imencode('.jpeg',MyCog.canvas)
            num_bytes = num_bytes.tobytes()
            fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
            await ctx.send(file=fileObj)
    
def setup(bot):
    return bot.add_cog(MyCog(bot))

