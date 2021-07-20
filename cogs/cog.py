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
    fieldMap=np.zeros([width,height, 3],np.uint8)
    fillMask=np.zeros([width+2,height+2],np.uint8)
#     savedPictureName="EztakJ-VoAYSg9R.jpeg"
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
        "イギリス":{"player":None,"force":[{"attr":"army","region":"リヴァプール"},{"attr":"fleet","region":"エディンバラ"},{"attr":"fleet","region":"ロンドン"}]},
        "ドイツ":{"player":None,"force":[{"attr":"army","region":"ベルリン"},{"attr":"army","region":"ミュンヘン"},{"attr":"fleet","region":"キール"}]},
        "ロシア":{"player":None,"force":[{"attr":"army","region":"モスクワ"},{"attr":"army","region":"ワルシャワ"},{"attr":"fleet","region":"セヴァストポリ"},{"attr":"fleet","region":"サンクトペテルブルク南岸"}]},
        "オスマン・トルコ":{"player":None,"force":[{"attr":"army","region":"コンスタンティノープル"},{"attr":"army","region":"スミルナ"},{"attr":"fleet","region":"アンカラ"}]},
        "オーストリア・ハンガリー":{"player":None,"force":[{"attr":"army","region":"ウィーン"},{"attr":"army","region":"ブダペスト"},{"attr":"fleet","region":"トリエステ"}]},
        "イタリア":{"player":None,"force":[{"attr":"army","region":"ローマ"},{"attr":"army","region":"ヴェニス"},{"attr":"fleet","region":"ナポリ"}]},
        "フランス":{"player":None,"force":[{"attr":"army","region":"パリ"},{"attr":"army","region":"マルセイユ"},{"attr":"fleet","region":"ブレスト"}]}
    }
    
    #地域の辞書
    #一つの地域は一つ辞書をもつ
    #地域の持っている辞書には，属性(陸か海か)attr,拠点の有無base,移動可能地域のリストarmyDestination,fleetDestintionがある
    #また，2つの海岸に分かれている地域については
    #1.地名：陸路のみ記載
    #2.地名+岸A:岸Aから出る海路のみ記載
    #海側のarmyDestinationについては，岸が2か所に分かれているもののみ，Carry処理のために地域名を記載
    #それ以外は空とする
    region={
        "アルバニア":{"attr":"land","base":False,"armyDestination":["ギリシャ","セルビア","トリエステ"],"fleetDestination":["アドリア海","イオニア海","ギリシャ","トリエステ"]},
        "アンカラ":{"attr":"land","base":True,"armyDestination":["アルメニア","コンスタンティノープル","スミルナ"],"fleetDestination":["黒海","アルメニア","コンスタンティノープル"]},#1
        "アヴュリア":{"attr":"land","base":False,"armyDestination":["ヴェニス","ローマ","ナポリ"],"fleetDestination":["アドリア海","イオニア海","ヴェニス","ナポリ"]},
        "アルメニア":{"attr":"land","base":False,"armyDestination":["セヴァストポリ","アンカラ","スミルナ","シリア"],"fleetDestination":["セヴァストポリ","アンカラ","黒海"]},
        "ベルギー":{"attr":"land","base":True,"armyDestination":["オランダ","ルール","ブルゴーニュ","ピカルディ"],"fleetDestination":["オランダ","ピカルディ","イギリス海峡","北海"]},#2
        "ベルリン":{"attr":"land","base":True,"armyDestination":["プロシア","シレジア","ミュンヘン","キール"],"fleetDestination":["プロシア","キール","バルト海"]},#3
        "ボヘミア":{"attr":"land","base":False,"armyDestination":["ガリシア","シレジア","ミュンヘン","チロル","ウィーン"],"fleetDestination":[]},
        "ブレスト":{"attr":"land","base":True,"armyDestination":["ピカルディ","パリ","ガスコーニュ"],"fleetDestination":["ピカルディ","ガスコーニュ","中大西洋","イギリス海峡"]},#4
        "ブダペスト":{"attr":"land","base":True,"armyDestination":["ルーマニア","ガリシア","ウィーン","トリエステ","セルビア"],"fleetDestination":[]},#5
        "ブルガリア":{"attr":"land","base":True,"armyDestination":["ルーマニア","セルビア","ギリシャ","コンスタンティノープル"],"fleetDestination":[]},#6
        "ブルガリア東岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":["ルーマニア","コンスタンティノープル","黒海"]},#6
        "ブルガリア南岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":["エーゲ海","コンスタンティノープル","ギリシャ"]},#6
        "ブルゴーニュ":{"attr":"land","base":False,"armyDestination":["ミュンヘン","ルール","ベルギー","ピカルディ","パリ","ガスコーニュ","マルセイユ"],"fleetDestination":[]},
        "クライド":{"attr":"land","base":False,"armyDestination":["エディンバラ","リヴァプール"],"fleetDestination":["エディンバラ","リヴァプール","北大西洋","ノルウェー海"]},
        "コンスタンティノープル":{"attr":"land","base":True,"armyDestination":["アンカラ","スミルナ","ブルガリア"],"fleetDestination":["アンカラ","スミルナ","ブルガリア東岸","ブルガリア南岸","黒海","エーゲ海"]},#7
        "デンマーク":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":[]},#8
        "エディンバラ":{"attr":"land","base":True,"armyDestination":["クライド","リヴァプール","ヨークシャー"],"fleetDestination":["クライド","ヨークシャー","北海","ノルウェー海"]},
        "フィンランド":{"attr":"land","base":False,"armyDestination":["サンクトペテルブルク","スウェーデン","ノルウェー"],"fleetDestination":["ボスニア海","サンクトペテルブルク南岸","スウェーデン"]},
        "ガリシア":{"attr":"land","base":False,"armyDestination":["ウクライナ","ワルシャワ","シレジア","ボヘミア","ウィーン","ブダペスト","ルーマニア"],"fleetDestination":[]},
        "ガスコーニュ":{"attr":"land","base":False,"armyDestination":["ブレスト","パリ","ブルゴーニュ","マルセイユ","スペイン"],"fleetDestination":["中大西洋","ブレスト","スペイン北岸"]},
        "ギリシャ":{"attr":"land","base":True,"armyDestination":["アルバニア","セルビア","ブルガリア"],"fleetDestination":["イオニア海","エーゲ海","アルバニア","ブルガリア南岸"]},#9
        "オランダ":{"attr":"land","base":True,"armyDestination":["キール","ルール","ベルギー"],"fleetDestination":["ヘルゴランド湾","北海","キール","ベルギー"]},#10
        "キール":{"attr":"land","base":True,"armyDestination":["ベルリン","ミュンヘン","ルール","オランダ"],"fleetDestination":["バルト海","ヘルゴランド湾","ベルリン","オランダ"]},#11
        "リヴォニア":{"attr":"land","base":False,"armyDestination":["サンクトペテルブルク","モスクワ","ワルシャワ","プロシア"],"fleetDestination":["ボスニア海","バルト海","サンクトペテルブルク南岸","プロシア"]},
        "ロンドン":{"attr":"land","base":True,"armyDestination":["ヨークシャー","ウェールズ"],"fleetDestination":["北海","イギリス海峡","ヨークシャー","ウェールズ"]},#12
        "リヴァプール":{"attr":"land","base":True,"armyDestination":["クライド","エディンバラ","ヨークシャー","ウェールズ"],"fleetDestination":["北大西洋","アイリッシュ海","ウェールズ","クライド"]},#13
        "マルセイユ":{"attr":"land","base":True,"armyDestination":["ピエモント","ブルゴーニュ","ガスコーニュ","スペイン"],"fleetDestination":["リヨン湾","ピエモント","スペイン南岸"]},#14
        "モスクワ":{"attr":"land","base":True,"armyDestination":["サンクトペテルブルク","リヴォニア","ワルシャワ","ウクライナ","セヴァストポリ"],"fleetDestination":[]},#15
        "ミュンヘン":{"attr":"land","base":True,"armyDestination":["ボヘミア","シレジア","ベルリン","キール","ルール","ブルゴーニュ","チロル"],"fleetDestination":[]},#16
        "北アフリカ":{"attr":"land","base":False,"armyDestination":["チュニス"],"fleetDestination":["西地中海","中大西洋","チュニス"]},
        "ナポリ":{"attr":"land","base":True,"armyDestination":["アヴュリア","ローマ"],"fleetDestination":["ティレニア海","イオニア海","アヴュリア","ローマ"]},
        "ノルウェー":{"attr":"land","base":True,"armyDestination":["スウェーデン","フィンランド","サンクトペテルブルク"],"fleetDestination":["北海","スカゲラク","ノルウェー海","バレンツ海","スウェーデン","サンクトペテルブルク北岸"]},#17
        "パリ":{"attr":"land","base":True,"armyDestination":["ピカルディ","ブルゴーニュ","ガスコーニュ","ブレスト"],"fleetDestination":[]},#18
        "ピカルディ":{"attr":"land","base":False,"armyDestination":["ベルギー","ブルゴーニュ","パリ","ブレスト"],"fleetDestination":["イギリス海峡","ベルギー","ブレスト"]},
        "ピエモント":{"attr":"land","base":False,"armyDestination":["チロル","ヴェニス","トスカーナ","マルセイユ"],"fleetDestination":["リヨン湾","トスカーナ","マルセイユ"]},
        "ポルトガル":{"attr":"land","base":True,"armyDestination":["スペイン"],"fleetDestination":["中大西洋","スペイン南岸","スペイン北岸"]},#19
        "プロシア":{"attr":"land","base":False,"armyDestination":["リヴォニア","ワルシャワ","シレジア","ベルリン"],"fleetDestination":["バルト海","リヴォニア","ベルリン"]},
        "ローマ":{"attr":"land","base":True,"armyDestination":["トスカーナ","ヴェニス","アヴュリア","ナポリ"],"fleetDestination":["ティレニア海","トスカーナ","ナポリ"]},#20
        "ルール":{"attr":"land","base":False,"armyDestination":["キール","ミュンヘン","オランダ","ベルギー","ブルゴーニュ"],"fleetDestination":[]},
        "ルーマニア":{"attr":"land","base":True,"armyDestination":["セヴァストポリ","ウクライナ","ガリシア","ブダペスト","セルビア","ブルガリア"],"fleetDestination":["黒海","セヴァストポリ","ブルガリア東岸"]},#21
        "セルビア":{"attr":"land","base":True,"armyDestination":["ブルガリア","ルーマニア","ブダペスト","トリエステ","アルバニア","ギリシャ"],"fleetDestination":[]},#22
        "セヴァストポリ":{"attr":"land","base":True,"armyDestination":["モスクワ","ウクライナ","ルーマニア","アルメニア"],"fleetDestination":["黒海","ルーマニア","アルメニア"]},#23
        "シレジア":{"attr":"land","base":False,"armyDestination":["ワルシャワ","プロシア","ベルリン","ミュンヘン","ボヘミア","ガリシア"],"fleetDestination":[]},
        "スミルナ":{"attr":"land","base":True,"armyDestination":["コンスタンティノープル","アンカラ","アルメニア","シリア"],"fleetDestination":["東地中海","エーゲ海","コンスタンティノープル","シリア"]},#24
        "スペイン":{"attr":"land","base":True,"armyDestination":["ポルトガル","ガスコーニュ","マルセイユ"],"fleetDestination":[]},#25
        "スペイン北岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":["中大西洋","ガスコーニュ","ポルトガル"]},#25
        "スペイン南岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":[]},#25
        "サンクトペテルブルク":{"attr":"land","base":True,"armyDestination":["ノルウェー","フィンランド","リヴォニア","モスクワ"],"fleetDestination":[]},#26
        "サンクトペテルブルク北岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":["バレンツ海","ノルウェー"]},#26
        "サンクトペテルブルク南岸":{"attr":"land","base":True,"armyDestination":[],"fleetDestination":["ボスニア海","フィンランド","リヴォニア"]},#26
        "スウェーデン":{"attr":"land","base":True,"armyDestination":["ノルウェー","フィンランド"],"fleetDestination":["ボスニア海","バルト海","スカゲラク","フィンランド","ノルウェー"]},#27
        "シリア":{"attr":"land","base":False,"armyDestination":["アルメニア","スミルナ"],"fleetDestination":["東地中海","スミルナ"]},
        "トリエステ":{"attr":"land","base":True,"armyDestination":["アルバニア","セルビア","ブダペスト","ウィーン","チロル","ヴェニス"],"fleetDestination":["アドリア海","ヴェニス","アルバニア"]},#28
        "チュニス":{"attr":"land","base":True,"armyDestination":["北アフリカ"],"fleetDestination":["イオニア海","ティレニア海","西地中海","北アフリカ"]},#29
        "トスカーナ":{"attr":"land","base":False,"armyDestination":["ピエモント","ヴェニス","ローマ"],"fleetDestination":["リヨン湾","ティレニア海","ピエモント","ローマ"]},
        "チロル":{"attr":"land","base":False,"armyDestination":["ウィーン","ボヘミア","ミュンヘン","ピエモント","ヴェニス","トリエステ"],"fleetDestination":[]},
        "ウクライナ":{"attr":"land","base":False,"armyDestination":["セヴァストポリ","モスクワ","ワルシャワ","ガリシア","ルーマニア"],"fleetDestination":[]},
        "ヴェニス":{"attr":"land","base":True,"armyDestination":["トリエステ","チロル","ピエモント","トスカーナ","ローマ","アヴュリア"],"fleetDestination":["アドリア海","トリエステ","アヴュリア"]},#30
        "ウィーン":{"attr":"land","base":True,"armyDestination":["ブダペスト","ガリシア","ボヘミア","チロル","トリエステ"],"fleetDestination":[]},#31
        "ウェールズ":{"attr":"land","base":False,"armyDestination":["リヴァプール","ヨークシャー","ロンドン"],"fleetDestination":["アイリッシュ海","イギリス海峡","リヴァプール","ロンドン"]},
        "ワルシャワ":{"attr":"land","base":True,"armyDestination":["ウクライナ","モスクワ","リヴォニア","プロシア","シレジア","ガリシア"],"fleetDestination":[]},#32
        "ヨークシャー":{"attr":"land","base":False,"armyDestination":["エディンバラ","リヴァプール","ウェールズ","ロンドン"],"fleetDestination":["北海","エディンバラ","ロンドン"]},
        "北大西洋":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["ノルウェー海","アイリッシュ海","中大西洋","クライド","リヴァプール"]},
        "アイリッシュ海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["北大西洋","中大西洋","イギリス海峡","ウェールズ","リヴァプール"]},
        "中大西洋":{"attr":"sea","base":False,"armyDestination":["スペイン"],"fleetDestination":["北大西洋","アイリッシュ海","イギリス海峡","西地中海","ブレスト","ガスコーニュ","スペイン北岸","ポルトガル","スペイン南岸","北アフリカ"]},
        "西地中海":{"attr":"sea","base":False,"armyDestination":["スペイン"],"fleetDestination":["中大西洋","リヨン湾","ティレニア海","スペイン南岸","北アフリカ","チュニス"]},
        "リヨン湾":{"attr":"sea","base":False,"armyDestination":["スペイン"],"fleetDestination":["ティレニア海","西地中海","スペイン南岸","マルセイユ","ピエモント","トスカーナ"]},
        "ティレニア海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["リヨン湾","西地中海","イオニア海","トスカーナ","ローマ","ナポリ","チュニス"]},
        "イオニア海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["ティレニア海","アドリア海","エーゲ海","東地中海","チュニス","ナポリ","アヴュリア","アルバニア","ギリシャ"]},
        "アドリア海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["イオニア海","アヴュリア","ヴェニス","トリエステ","アルバニア"]},
        "エーゲ海":{"attr":"sea","base":False,"armyDestination":["ブルガリア"],"fleetDestination":["イオニア海","東地中海","ギリシャ","ブルガリア南岸","コンスタンティノープル","スミルナ"]},
        "東地中海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["イオニア海","エーゲ海","スミルナ","シリア"]},
        "黒海":{"attr":"sea","base":False,"armyDestination":["ブルガリア"],"fleetDestination":["セヴァストポリ","ルーマニア","ブルガリア東岸","コンスタンティノープル","アンカラ","アルメニア"]},
        "ノルウェー海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["北大西洋","北海","バレンツ海","クライド","エディンバラ","ノルウェー"]},
        "イギリス海峡":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["アイリッシュ海","中大西洋","北海","ウェールズ","ロンドン","ブレスト","ピカルディ","ベルギー"]},
        "北海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["ノルウェー海","イギリス海峡","ヘルゴランド湾","スカゲラク","ノルウェー","デンマーク","オランダ","ベルギー","ロンドン","ヨークシャー","エディンバラ"]},
        "ヘルゴランド湾":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["北海","デンマーク","キール","オランダ"]},
        "スカゲラク":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["北海","デンマーク","ノルウェー","スウェーデン"]},
        "バルト海":{"attr":"sea","base":False,"armyDestination":[],"fleetDestination":["ボスニア海","スウェーデン","リヴォニア","プロシア","ベルリン","キール"]},
        "ボスニア海":{"attr":"sea","base":False,"armyDestination":["サンクトペテルブルク"],"fleetDestination":["バルト海","スウェーデン","フィンランド","サンクトペテルブルク南岸","リヴォニア"]},
        "バレンツ海":{"attr":"sea","base":False,"armyDestination":["サンクトペテルブルク"],"fleetDestination":["ノルウェー海","サンクトペテルブルク北岸","ノルウェー"]}
    }
    
    
    
    def __init__(self,bot):
        self.bot=bot
        
        #self.bot.remove_command("help")
        
    @commands.command()#group()
    async def ping(self,ctx):
#         if ctx.invoked_subcommand is None:
        await ctx.send('pong'+str(self.standbyLog))
    
    @commands.command()#group()
    async def status(self,ctx):
        """国の初期ステータスをランダムに返す"""
#         if ctx.invoked_subcommand is None:
        name,val=random.choice(list(self.country.items()))
        await ctx.send(str(name)+":"+str(val))
           
    @commands.command()#group() 
    async def clear(self,ctx):
        """キャンバスを初期化して返す"""
#         if ctx.invoked_subcommand is None:
#             global canvas
        self.canvas=copy.deepcopy(self.blank)
        self.canvas=cv2.convertScaleAbs(self.canvas)
        _, num_bytes = cv2.imencode('.jpeg',self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send(file=fileObj)
        
    @commands.command()#group() 
    async def pic(self,ctx):
        """現在のキャンバスの状態を返す，初期化済みの場合真っ黒"""
#         if ctx.invoked_subcommand is None:
#         global canvas
        _, num_bytes = cv2.imencode('.jpeg', self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send(file=fileObj)

    @commands.command()#group() 
    async def line(self,ctx):
        """キャンバスにランダムな線を1本上書きして返す"""
#         if ctx.invoked_subcommand is None:
#             global canvas
#             global width
#             global height
        pointA=(random.randint(1,self.width-1),random.randint(1,self.height-1))
        pointB=(random.randint(1,self.width-1),random.randint(1,self.height-1))
        lineColor=self.colorSet[random.randint(0,6)]
        self.canvas=cv2.line(
            self.canvas,
            pointA,
            pointB,
            lineColor,
            2
        )
        self.canvas=cv2.convertScaleAbs(self.canvas)
        _, num_bytes = cv2.imencode('.jpeg',self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
        await ctx.send(file=fileObj)
            
    @commands.command()#group() 
    async def rect(self,ctx):
        """キャンバスにランダムな直方体を1つ上書きして返す"""
#         if ctx.invoked_subcommand is None:
#             global canvas
#             global width
#             global height
        pointA=(random.randint(1,self.width-1),random.randint(1,self.height-1))
        pointB=(random.randint(1,self.width-1),random.randint(1,self.height-1))
        rectColor=self.colorSet[random.randint(0,6)]
        self.canvas=cv2.rectangle(
            self.canvas,
            pointA,
            pointB,
            rectColor,
            2
        )
        self.canvas=cv2.convertScaleAbs(self.canvas)
        _, num_bytes = cv2.imencode('.jpeg',self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send("pointA:"+str(pointA)+" pointB:"+str(pointB))
        await ctx.send(file=fileObj)
            
    @commands.command()#group() 
    async def fill(self,ctx):
        """ランダムな点を起点に塗りつぶし"""
#         if ctx.invoked_subcommand is None:
#             global canvas
#             global fillMask
#             global width
#             global height
        point=(random.randint(1,self.width-1),random.randint(1,self.height-1))
        fillColor=self.colorSet[random.randint(0,6)]
        retval,self.canvas,mask,rect = cv2.floodFill(image=self.canvas, mask=self.fillMask, seedPoint=point, newVal=fillColor,flags=4)
        self.canvas=cv2.convertScaleAbs(self.canvas)
        _, num_bytes = cv2.imencode('.jpeg',self.canvas)
        num_bytes = num_bytes.tobytes()
        fileObj = discord.File(io.BytesIO(num_bytes),filename="blank.png")
        await ctx.send("point:"+str(point))
        await ctx.send(file=fileObj)
        self.fillMask=np.zeros([self.width+2,self.height+2],np.uint8)

def setup(bot):
    return bot.add_cog(MyCog(bot))

