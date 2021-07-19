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
import asyncio


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
    
    #国名の辞書
    #一つの国は一つの辞書を持つ
    #国の持っている辞書には，プレイヤーIDのplayer,兵のリストforceがある
    #forceは各要素が各兵力の辞書になっている
    #各兵力の辞書には，属性attr，所在地reegionがある
    country={
        "イギリス":{"player":None,"force":[{"attr":"army","region":"リヴァプール"},{"attr":"navy","region":"エディンバラ"},{"attr":"navy","region":"ロンドン"}]},
        "ドイツ":{"player":None,"force":[{"attr":"army","region":"ベルリン"},{"attr":"army","region":"ミュンヘン"},{"attr":"navy","region":"キール"}]},
        "ロシア":{"player":None,"force":[{"attr":"army","region":"モスクワ"},{"attr":"army","region":"ワルシャワ"},{"attr":"navy","region":"セヴァストポリ"},{"attr":"navy","region":"サンクトペテルブルク南岸"}]},
        "オスマン・トルコ":{"player":None,"force":[{"attr":"army","region":"コンスタンティノープル"},{"attr":"army","region":"スミルナ"},{"attr":"navy","region":"アンカラ"}]},
        "オーストリア・ハンガリー":{"player":None,"force":[{"attr":"army","region":"ウィーン"},{"attr":"army","region":"ブダペスト"},{"attr":"navy","region":"トリエステ"}]},
        "イタリア":{"player":None,"force":[{"attr":"army","region":"ローマ"},{"attr":"army","region":"ヴェニス"},{"attr":"navy","region":"ナポリ"}]},
        "フランス":{"player":None,"force":[{"attr":"army","region":"パリ"},{"attr":"army","region":"マルセイユ"},{"attr":"navy","region":"ブレスト"}]}
    }
    
    #地域の辞書
    #一つの地域は一つ辞書をもつ
    #地域の持っている辞書には，属性(陸か海か)attr,拠点の有無base,移動可能地域のリストdestinationがある
    region={
        "アルバニア":{"attr":"land","base":False,"destination":["ギリシャ","セルビア","トリエステ","アドリア海","イオニア海"]},
        "アンカラ":{"attr":"land","base":True,"destination":["アルメニア","黒海","コンスタンティノープル","スミルナ"]},#1
        "アヴュリア":{"attr":"land","base":False,"destination":["アドリア海","イオニア海","ヴェニス","ローマ","ナポリ"]},
        "アルメニア":{"attr":"land","base":False,"destination":["セヴァストポリ","黒海","アンカラ","スミルナ","シリア"]},
        "ベルギー":{"attr":"land","base":True,"destination":["オランダ","ルール","ブルゴーニュ","ピカルディ","イギリス海峡","北海"]},#2
        "ベルリン":{"attr":"land","base":True,"destination":["プロシア","シレジア","ミュンヘン","キール","バルト海"]},#3
        "ボヘミア":{"attr":"land","base":False,"destination":["ガリシア","シレジア","ミュンヘン","チロル","ウィーン"]},
        "ブレスト":{"attr":"land","base":True,"destination":["ピカルディ","パリ","ガスコーニュ","中大西洋","イギリス海峡"]},#4
        "ブダペスト":{"attr":"land","base":True,"destination":["ルーマニア","ガリシア","ウィーン","トリエステ","セルビア"]},#5
        "ブルガリア":{"attr":"land","base":True,"destination":[]},#6
        "ブルガリア東岸":{"attr":"land","base":True,"destination":[]},#6
        "ブルガリア南岸":{"attr":"land","base":True,"destination":[]},#6
        "ブルゴーニュ":{"attr":"land","base":False,"destination":[]},
        "クライド":{"attr":"land","base":False,"destination":[]},
        "コンスタンティノープル":{"attr":"land","base":True,"destination":[]},#7
        "デンマーク":{"attr":"land","base":True,"destination":[]},#8
        "エディンバラ":{"attr":"land","base":True,"destination":[]},
        "フィンランド":{"attr":"land","base":False,"destination":[]},
        "ガリシア":{"attr":"land","base":False,"destination":[]},
        "ガスコーニュ":{"attr":"land","base":False,"destination":[]},
        "ギリシャ":{"attr":"land","base":True,"destination":[]},#9
        "オランダ":{"attr":"land","base":True,"destination":[]},#10
        "キール":{"attr":"land","base":True,"destination":[]},#11
        "リヴォニア":{"attr":"land","base":False,"destination":[]},
        "ロンドン":{"attr":"land","base":True,"destination":[]},#12
        "リヴァプール":{"attr":"land","base":True,"destination":[]},#13
        "マルセイユ":{"attr":"land","base":True,"destination":[]},#14
        "モスクワ":{"attr":"land","base":True,"destination":[]},#15
        "ミュンヘン":{"attr":"land","base":True,"destination":[]},#16
        "北アフリカ":{"attr":"land","base":False,"destination":[]},
        "ナポリ":{"attr":"land","base":True,"destination":[]},
        "ノルウェー":{"attr":"land","base":True,"destination":[]},#17
        "パリ":{"attr":"land","base":True,"destination":[]},#18
        "ピカルディ":{"attr":"land","base":False,"destination":[]},
        "ピエモント":{"attr":"land","base":False,"destination":[]},
        "ポルトガル":{"attr":"land","base":True,"destination":[]},#19
        "プロシア":{"attr":"land","base":False,"destination":[]},
        "ローマ":{"attr":"land","base":True,"destination":[]},#20
        "ルール":{"attr":"land","base":False,"destination":[]},
        "ルーマニア":{"attr":"land","base":True,"destination":[]},#21
        "セルビア":{"attr":"land","base":True,"destination":[]},#22
        "セヴァストポリ":{"attr":"land","base":True,"destination":[]},#23
        "シレジア":{"attr":"land","base":False,"destination":[]},
        "スミルナ":{"attr":"land","base":True,"destination":[]},#24
        "スペイン":{"attr":"land","base":True,"destination":[]},#25
        "スペイン":{"attr":"land","base":True,"destination":[]},#25
        "スペイン":{"attr":"land","base":True,"destination":[]},#25
        "サンクトペテルブルク":{"attr":"land","base":True,"destination":[]},#26
        "サンクトペテルブルク":{"attr":"land","base":True,"destination":[]},#26
        "サンクトペテルブルク":{"attr":"land","base":True,"destination":[]},#26
        "スウェーデン":{"attr":"land","base":True,"destination":[]},#27
        "シリア":{"attr":"land","base":False,"destination":[]},
        "トリエステ":{"attr":"land","base":True,"destination":[]},#28
        "チュニス":{"attr":"land","base":True,"destination":[]},#29
        "トスカーナ":{"attr":"land","base":False,"destination":[]},
        "チロル":{"attr":"land","base":False,"destination":[]},
        "ウクライナ":{"attr":"land","base":False,"destination":[]},
        "ヴェニス":{"attr":"land","base":True,"destination":[]},#30
        "ウィーン":{"attr":"land","base":True,"destination":[]},#31
        "ウェールズ":{"attr":"land","base":False,"destination":[]},
        "ワルシャワ":{"attr":"land","base":True,"destination":[]},#32
        "ヨークシャー":{"attr":"land","base":False,"destination":[]},
        "北大西洋":{"attr":"sea","base":False,"destination":[]},
        "アイリッシュ海":{"attr":"sea","base":False,"destination":[]},
        "中大西洋":{"attr":"sea","base":False,"destination":[]},
        "西地中海":{"attr":"sea","base":False,"destination":[]},
        "リヨン湾":{"attr":"sea","base":False,"destination":[]},
        "ティレニア海":{"attr":"sea","base":False,"destination":[]},
        "イオニア海":{"attr":"sea","base":False,"destination":[]},
        "アドリア海":{"attr":"sea","base":False,"destination":[]},
        "エーゲ海":{"attr":"sea","base":False,"destination":[]},
        "東地中海":{"attr":"sea","base":False,"destination":[]},
        "黒海":{"attr":"sea","base":False,"destination":[]},
        "ノルウェー海":{"attr":"sea","base":False,"destination":[]},
        "イギリス海峡":{"attr":"sea","base":False,"destination":[]},
        "北海":{"attr":"sea","base":False,"destination":[]},
        "ヘルゴランド湾":{"attr":"sea","base":False,"destination":[]},
        "スカゲラク":{"attr":"sea","base":False,"destination":[]},
        "バルト海":{"attr":"sea","base":False,"destination":[]},
        "ボスニア海":{"attr":"sea","base":False,"destination":[]},
        "西地中海":{"attr":"sea","base":False,"destination":[]}
    }
    def __init__(self,bot):
        self.bot=bot
        #self.bot.remove_command("help")
        
    @commands.command()#group()
    async def ping(self,ctx):
#         if ctx.invoked_subcommand is None:
        await ctx.send('pong'+str(self.standbyLog))
    
#     @commands.command()#group()
#     async def status(self,ctx):
#         """国の初期ステータスをランダムに返す"""
# #         if ctx.invoked_subcommand is None:
#         name,val=random.choice(list(self.country.items()))
#         await ctx.send(str(name)+":"+str(val))
           
#     @commands.command()#group() 
#     async def pic(self,ctx):
#         """事前にディレクトリ内に保存されたほぼ真っ白画像を返す"""
# #         if ctx.invoked_subcommand is None:
#         fileObj = discord.File(self.savedPictureName)
#         await ctx.send(file=fileObj)
    @commands.command()#group() 
    async def clear(self,ctx):
    """キャンバスを初期化して返す"""
#         if ctx.invoked_subcommand is None:
#             global canvas
#         self.canvas=copy.deepcopy(self.blank)
#         self.canvas=cv2.convertScaleAbs(self.canvas)
        _, num_bytes = cv2.imencode('.jpeg',self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send(file=fileObj)
        
#     @commands.command()#group() 
#     async def pic2(self,ctx):
#         """現在のキャンバスの状態を返す，初期化済みの場合真っ黒"""
# #         if ctx.invoked_subcommand is None:
# #         global canvas
#         _, num_bytes = cv2.imencode('.jpeg', self.canvas)
#         num_bytes = num_bytes.tobytes()
#         fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#         await ctx.send(file=fileObj)

#     @commands.command()#group() 
#     async def line(self,ctx):
#         """キャンバスにランダムな線を1本上書きして返す"""
# #         if ctx.invoked_subcommand is None:
# #             global canvas
# #             global width
# #             global height
#         pointA=(random.randint(1,self.width-1),random.randint(1,self.height-1))
#         pointB=(random.randint(1,self.width-1),random.randint(1,self.height-1))
#         lineColor=self.colorSet[random.randint(0,6)]
#         self.canvas=cv2.line(
#             self.canvas,
#             pointA,
#             pointB,
#             lineColor,
#             2
#         )
#         self.canvas=cv2.convertScaleAbs(self.canvas)
#         _, num_bytes = cv2.imencode('.jpeg',self.canvas)
#         num_bytes = num_bytes.tobytes()
#         fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#         await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
#         await ctx.send(file=fileObj)
            
#     @commands.command()#group() 
#     async def rect(self,ctx):
#     """キャンバスにランダムな直方体を1つ上書きして返す"""
# #         if ctx.invoked_subcommand is None:
# #             global canvas
# #             global width
# #             global height
#         pointA=(random.randint(1,self.width-1),random.randint(1,self.height-1))
#         pointB=(random.randint(1,self.width-1),random.randint(1,self.height-1))
#         rectColor=self.colorSet[random.randint(0,6)]
#         self.canvas=cv2.rectangle(
#             self.canvas,
#             pointA,
#             pointB,
#             rectColor,
#             2
#         )
#         self.canvas=cv2.convertScaleAbs(self.canvas)
#         _, num_bytes = cv2.imencode('.jpeg',self.canvas)
#         num_bytes = num_bytes.tobytes()
#         fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#         await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
#         await ctx.send(file=fileObj)
            
#     @commands.command()#group() 
#     async def fill(self,ctx):
#     """ランダムな点を起点に塗りつぶし"""
# #         if ctx.invoked_subcommand is None:
# #             global canvas
# #             global fillMask
# #             global width
# #             global height
#         point=(random.randint(1,self.width-1),random.randint(1,self.height-1))
#         fillColor=self.colorSet[random.randint(0,6)]
#         retval,self.canvas,mask,rect = cv2.floodFill(image=self.canvas, mask=self.fillMask, seedPoint=point, newVal=fillColor,flags=4)
#         self.canvas=cv2.convertScaleAbs(self.canvas)
#         _, num_bytes = cv2.imencode('.jpeg',self.canvas)
#         num_bytes = num_bytes.tobytes()
#         fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
#         await ctx.send("point:"+str(point))
#         await ctx.send(file=fileObj)
#         self.fillMask=np.zeros([self.width+2,self.height+2],np.uint8)
    
    
        
def setup(bot):
    return bot.add_cog(MyCog(bot))

