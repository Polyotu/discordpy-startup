from discord.ext import commands,tasks
import discord
import datetime
from datetime import datetime
import subprocess
import sys
import os
import time
import pya3rt
import requests
import re
import math
import asyncio
from io import BytesIO
import wave
from randomDice import dice
from textAnalysys import text_analysys
apikey = "DZZgARp1wuae2DZ49wpmJfyhEeFdptl0"
usser = pya3rt.TalkClient(apikey)
pattern = re.compile(r'\$\$[0-9]{1,3}d[0-9]{1,3}|\$\$[0-9]{1,3}D[0-9]{1,3}')
greet_pattern = re.compile(r'(たーきー|ターキー)(くん|ちゃん)、*(こんばんは|こんにちは|おはよう)ー*！*')
greet_pattern_hny = re.compile(r'(たーきー|ターキー)(くん|ちゃん)、*(あけましておめでとう)ー*！*')
name_pattern=re.compile(r'(たーきー|ターキー)(くん|ちゃん)*')


class MyCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.bot.remove_command("help")
        self.loopTask.start()
        self.speakQueue=asyncio.Queue(maxsize=100)
        self.playNextQueue = asyncio.Event()
        self.bot.loop.create_task(self.speakQueueLoop(self.speakQueue))

    async def speakQueueLoop(self,speakQueue):
        while True:
            print("speak!")
            self.playNextQueue.clear()
            queueTop = await self.speakQueue.get()
            print(str(list(queueTop.keys())[0]))
            # os.system('./AquesTalkPi ' + str(list(queueTop.keys())[0]) + ' > /mnt/usb1/output.wav')
            # source = discord.FFmpegPCMAudio("/mnt/usb1/output.wav")
            ret = subprocess.Popen(['./AquesTalkPi', str(list(queueTop.keys())[0])], stdout=subprocess.PIPE)
            print(ret.stdout)
            # f=wave.open(BytesIO(ret.stdout))
            # source = discord.FFmpegPCMAudio(BytesIO(f.readframes(f.getnframes())))#,pipe=True)
            # f=BytesIO(ret.stdout)
            # source = discord.FFmpegPCMAudio(f)
            source = discord.FFmpegPCMAudio(ret.stdout,pipe=True)
            (list(queueTop.values())[0]).play(source,after=self.toggle_next)
            await self.playNextQueue.wait()

    def toggle_next(self,error):
        try:
            self.bot.loop.call_soon_threadsafe(self.playNextQueue.set)
        except Exception as e:
            print(e)

    @commands.group(invoke_without_command=True)
    async def help(self,ctx):
        embed=discord.Embed(title="コマンド一覧", description="コマンド一覧です．詳細は各コマンドに対しhelpオプションをつけて実行して下さい．(例：$$ping help)", color=0xfbff00)
        embed.add_field(name="ping", value="稼働していればpongと返ってきます．", inline=False)
        embed.add_field(name="help", value="本コマンド．", inline=False)
        embed.add_field(name="join(またはconnect,summon)", value="ボイスチャットに入ってから使うと同じボイスチャットにbotを呼べます．以降Botがテキストチャンネルの内容を読み上げます．", inline=False)
        embed.add_field(name="bye(またはdisconnect,leave)", value="ボイスチャットにいるBotを退出させます．", inline=False)
        embed.add_field(name="dead", value='某AAを表示します．', inline=False)
        embed.add_field(name="tomb", value='某AAを表示します．', inline=False)
        # embed.add_field(name="chat,talk,hey X", value='引数Xは必須．Botと簡単な会話ができます．ボイスチャットにBotがいる場合内容を読み上げます．(使用例："$$talk こんにちは")', inline=False)
        #embed.add_field(name="stage", value="引数無し．現在のステージを表示します．", inline=False)
        embed.add_field(name="xxxdyyy(またはxxxDyyy)", value='option:xxx,yyyに任意の数値(3桁まで)を入れて使用．ダイスを振って合計値を返す．', inline=False)
        embed.add_field(name="noread(またはnr) xxx", value='option:xxxに任意の文字列を入れて使用．読み上げ実行中に，このコマンドを使用してテキストチャンネルに書き込むと読み上げされません．', inline=False)
        embed.add_field(name="talk(またはhey,tk) xxx", value='option:xxxに任意の文字列を入れて使用．botと会話が可能です．読み上げ参加中は返答内容を読み上げます．', inline=False)
        await ctx.send(embed=embed)

    @commands.group()
    async def ping(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('pong!')
    
    @ping.command(name="help",aliases=["-h"])
    async def ping_help(self,ctx):
        embed=discord.Embed(title="pingコマンドのヘルプ", description="$$pingと打つとbotがpong!と応答します．生存確認にどうぞ．", color=0xfbff00)
        embed.add_field(name="使用例", value='$$ping', inline=False)
        await ctx.send(embed=embed)

    @commands.group(aliases=["hey","tk"])
    async def talk(self,ctx):
        if ctx.invoked_subcommand is None:
            """botと話せる．talk,heyでも可"""
            await ctx.send("なんでしょう？")
    
    @talk.command(name="talk",aliases=["-t"])
    async def talk_talk(self,ctx,*args):
        intext=text_analysys(str(args))
        try:
            intext=re.sub(name_pattern,"",intext)
            response = usser.talk(intext)
            reply = ((response['results'])[0])['reply'] 
            print(intext+" -> "+reply)
            if ctx.message.guild.voice_client:
                await self.speakQueue.put_nowait({str(reply):ctx.message.guild.voice_client})
                # os.system('./AquesTalkPi ' + reply + ' > /mnt/usb1/output.wav')
                # source = discord.FFmpegPCMAudio("/mnt/usb1/output.wav")
                # ctx.message.guild.voice_client.play(source)
            else:
                pass
            await ctx.send(reply)
        except:
            await ctx.send("エラーが発生しました．別の文章を入力してください．")

    @talk.command(name="help",aliases=["-h"])
    async def talk_help(self,ctx):
        embed=discord.Embed(title="talkコマンドのヘルプ", description="$$talk(または$$hey,tk) -t xxx(xxx部分に話しかける内容)  の形でコマンドを入力すると，botが対話形式で応答してくれます．", color=0xfbff00)
        embed.add_field(name="使用例1", value='$$talk -t こんにちは', inline=False)
        embed.add_field(name="使用例2", value='$$hey -t ありがとう', inline=False)
        embed.add_field(name="使用例3", value='$$tk -t こんばんは', inline=False)
        await ctx.send(embed=embed)


    @commands.group(aliases=["nr"])
    async def noread(self,ctx):
        if ctx.invoked_subcommand is None:
            print("nr")

    @noread.command(name="help",aliases=["-h"])
    async def noread_help(self,ctx):
        embed=discord.Embed(title="noreadコマンドのヘルプ", description="$$noread(または$$nr)と先頭についたテキストは，このボットは読み上げません．", color=0xfbff00)
        embed.add_field(name="使用例1", value='$$noread 読み上げさせないコマンド', inline=False)
        embed.add_field(name="使用例2", value='$$nr 読み上げさせないコマンド', inline=False)
        await ctx.send(embed=embed)

    # @commands.group(aliases=["tlg"])
    # async def tweetlog(self,ctx):
    #     if ctx.invoked_subcommand is None:
    #         tmp,length=flgstrage(1)
    #         ans=dice(1,length)
    #         reply,length=flgstrage(ans)
    #         await ctx.send(str(ans)+"/"+str(length)+" "+reply)

    # @tweetlog.command(name="desig",aliases=["-d"])
    # async def tweetlog_designation(self,ctx,a=0):
    #     a=int(a)
    #     reply,length=flgstrage(a)
    #     await ctx.send(str(a)+"/"+str(length)+" "+reply)

    # @tweetlog.command(name="help",aliases=["-h"])
    # async def tweetlog_help(self,ctx):
    #     embed=discord.Embed(title="tweetlogコマンドのヘルプ", description="$$tweetlog(または$$tlg)とコマンドを打つとパワーのある内輪ネタが返ってきます．番号指定もできます．", color=0xfbff00)
    #     embed.add_field(name="使用例1", value='$$tweetlog', inline=False)
    #     embed.add_field(name="使用例2", value='$$tlg', inline=False)
    #     embed.add_field(name="使用例3(番号指定)", value='$$tlg -d 10', inline=False)
    #     embed.add_field(name="使用例4(番号指定)", value='$$tlg desig 10', inline=False)
    #     await ctx.send(embed=embed)


    @commands.group(aliases=["connect","summon"]) #connectやsummonでも呼び出せる
    async def join(self,ctx):
        if ctx.invoked_subcommand is None:
            """Botをボイスチャンネルに入室させる．connect,summonでも可"""
            # await ctx.send("現在メンテナンス中につき,ボイスチャットへの参加が出来なくなっています.")
            voice_state = ctx.author.voice

            if (not voice_state) or (not voice_state.channel):
                print("Error because there are no users on voice channel")
                await ctx.send("先にボイスチャンネルに入っている必要があります。")
                return

            channel = voice_state.channel
            embed=discord.Embed(title=channel.name+"に入室しました。", description="コマンド一覧:$$help 2021/06/28 軽微なバグ修正．検証はしてないので死んでたら教えてください．不具合があった場合にはTwitter：Poly_Zetaまで．", color=0xff6600)
            # await ctx.send(channel.name+"に入室しました。コマンド一覧:$$help 2020/11/09 メンテナンスをしたため，一部コマンドの引数などに変更が加わっています．")
            await ctx.send(embed=embed)
            await channel.connect()
            print("connected to:",channel.name)
            myactivity = discord.Activity(name=str(len(self.bot.voice_clients))+'箇所で音声', type=discord.ActivityType.listening)
            await self.bot.change_presence(activity=myactivity)

    @join.command(name="help",aliases=["-h"])
    async def join_help(self,ctx):
        embed=discord.Embed(title="joinコマンドのヘルプ", description="ボイスチャットに参加している状態で$$joinとコマンドを打つと，botがボイスチャットに参加して，テキストチャットの内容を読み上げます．", color=0xfbff00)
        embed.add_field(name="使用例1", value='$$join', inline=False)
        embed.add_field(name="使用例2", value='$$summon', inline=False)
        embed.add_field(name="使用例3", value='$$connect', inline=False)
        await ctx.send(embed=embed)

    @commands.group(aliases=["disconnect","leave"])
    async def bye(self,ctx):
        if ctx.invoked_subcommand is None:
            """Botをボイスチャンネルから切断する．disconnect,byeでも可"""
            voice_client = ctx.message.guild.voice_client
            print(voice_client)

            if not voice_client:
                print("Error because I have not joined the channel")
                await ctx.send("Botはこのサーバーのボイスチャンネルに参加していません。")
                return

            await voice_client.disconnect()
            # await voice_client.cleanup()
            await ctx.send("ボイスチャンネルから切断しました。")
            print(voice_client)
            print("disconnect")
            print()
            myactivity = discord.Activity(name=str(len(self.bot.voice_clients))+'箇所で音声', type=discord.ActivityType.listening)
            await self.bot.change_presence(activity=myactivity)
    
    @bye.command(name="help",aliases=["-h"])
    async def bye_help(self,ctx):
        embed=discord.Embed(title="byeコマンドのヘルプ", description="$$byeとコマンドを打つと，ボイスチャットに参加しているbotを退出させます．", color=0xfbff00)
        embed.add_field(name="使用例1", value='$$bye', inline=False)
        embed.add_field(name="使用例2", value='$$disconnect', inline=False)
        embed.add_field(name="使用例3", value='$$leave', inline=False)
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_message(self,message):
        log=str(datetime.now())
        if message.author == self.bot.user:
            print(
                str(message.channel)+
                str(message.author)+
                str(message.content)+
                str(log)
            )
        # await self.speakQueue.put_nowait({message.content:message.channel.id})
        
        if message.content.startswith('$$'):
            if pattern.fullmatch(message.content):
                state=re.findall('[0-9]+',message.content)
                ret=dice(state[0],state[1])
                if(ret!=-1):
                    await message.channel.send(message.content[2:]+"->"+str(ret))
                else:
                    await message.channel.send("error!")
        elif name_pattern.search(message.content):
            print("called")
            try:
                print(message.content)
                intext=re.sub(name_pattern,"",message.content)
                response = usser.talk(intext)
                print(response)
                reply = ((response['results'])[0])['reply']
                print(intext+" -> "+reply)
                await message.channel.send(reply)
                if message.guild.voice_client:
                    await self.speakQueue.put_nowait({str(reply):message.guild.voice_client})
                    # os.system('./AquesTalkPi ' + reply + ' > /mnt/usb1/output.wav')
                    # source = discord.FFmpegPCMAudio("/mnt/usb1/output.wav")
                    # message.guild.voice_client.play(source)
            except:
                print("err")
                pass
        elif greet_pattern.fullmatch(message.content):
            dt_now=datetime.now()
            if (5<=int(dt_now.hour) and int(dt_now.hour)<=9):
                reply="おはよう"
            elif(10<=int(dt_now.hour) and int(dt_now.hour)<=17):
                reply="こんにちは"
            else:
                reply="こんばんは"
            await message.channel.send("はい"+reply)
        elif greet_pattern_hny.fullmatch(message.content):
            dt_now=datetime.now()
            if dt_now.month==1 and dt_now.day==1:
                await message.channel.send("はいあけましておめでとう")
            else:
                await message.channel.send("きょうは"+str(dt_now.month)+"がつ"+(dt_now.day)+"にち")
        elif message.author == self.bot.user and not message.content.startswith('ﾝﾜﾜﾜﾜﾜ'):
            pass
        elif ('http' in message.content):
            pass
        elif message.guild.voice_client:
            try:
                text=text_analysys(message.content)
                print(text)
                await self.speakQueue.put_nowait({text:message.guild.voice_client})
                # os.system('./AquesTalkPi "' + text + '" > /mnt/usb1/output.wav')
                # source = discord.FFmpegPCMAudio("/mnt/usb1/output.wav")
                # message.guild.voice_client.play(source)
            except:
                pass
        else:
            pass
        # await self.bot.process_commands(message)
    
    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        #print("update"+str(before.channel)+str(after.channel)+str(member))#beforeがnonNullでafterがnull->vcから離脱した
        if (before.channel is not None) and (after.channel is None):
            print("before.channel"+str(before.channel))
            print("after.channel"+str(after.channel))
            if (len(before.channel.members)==1):# and ():
                print("members"+str(len(before.channel.members)))
                if (before.channel.members[0].id==742047892000473169):
                    print("id"+str(before.channel.members[0].id))
                    for i in self.bot.voice_clients:
                        if i.channel==before.channel:
                            print("i.channel"+str(i.channel))
                            print("Auto disconnect")
                            embed=discord.Embed(title="ボイスチャットを離脱しました", description="自動離脱機能が作動しました．できれば最後の1人がボイスチャットを離脱する前に，disconnect(またはleave,bye)コマンドを使用してbotをボイスチャットから切断してください．", color=0xff6600)
                            try:
                                await before.channel.guild.system_channel.send(embed=embed)
                            except:
                                try:
                                    await before.channel.guild.text_channels[0].send(embed=embed)
                                except:
                                    pass
                            await i.disconnect()

    @tasks.loop(seconds=3600.0)
    async def loopTask(self):
        # garv = self.bot.get_channel(747691184410853437)
        garv = self.bot.get_channel(858965180552708126)
        dtnow=datetime.now()
        log=str(dtnow)
        o = subprocess.run(['vcgencmd measure_temp'], shell=True, stdout=subprocess.PIPE, check=True).stdout.decode("utf8")
        print("timer"+log+o)
        myactivity = discord.Activity(name=str(len(self.bot.voice_clients))+'箇所で音声', type=discord.ActivityType.listening)
        await self.bot.change_presence(activity=myactivity)
        await garv.send(log+" "+o+" "+str(len(self.bot.voice_clients))+'箇所で音声を再生中')
    
    @loopTask.before_loop
    async def before_loopTask(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    return bot.add_cog(MyCog(bot))


# def flgstrage(a:int):
#     flgdict={
#         1:"https://twitter.com/hawkgald/status/1246828228368461824",
#         2:"https://twitter.com/hawkgald/status/1246828932529188866",
#         3:"https://twitter.com/hawkgald/status/1246863053334831104",
#         4:"https://twitter.com/hawkgald/status/1325447715703021570",
#         5:"https://twitter.com/hawkgald/status/1322886938957815809",
#         6:"https://twitter.com/hawkgald/status/1322568236785823750",
#         7:"https://twitter.com/hawkgald/status/1322486349375549440",
#         8:"https://twitter.com/hawkgald/status/1321456206196531200",
#         9:"https://twitter.com/hawkgald/status/1320962564960874497",
#         10:"https://twitter.com/hawkgald/status/1320429268325691392",
#         11:"https://twitter.com/hawkgald/status/1311498314144124928",
#         12:"https://twitter.com/hawkgald/status/725728267903356928",
#         13:"https://twitter.com/hawkgald/status/1317335149046984704",
#         14:"https://twitter.com/hawkgald/status/1317332591368830977",
#         15:"https://twitter.com/hawkgald/status/1326186708178669571",
#         16:"https://twitter.com/hawkgald/status/1306949472270733312",
#         17:"https://twitter.com/hawkgald/status/1306407447372820480",
#         18:"https://twitter.com/hawkgald/status/1320046636316291072",
#         19:"https://twitter.com/hawkgald/status/1151132975213318147",
#         20:"https://twitter.com/hawkgald/status/1082315255085096961",
#         21:"https://twitter.com/hawkgald/status/594370070110818304",
#         22:"https://twitter.com/hawkgald/status/840646119126257664",
#         23:"https://twitter.com/hawkgald/status/893868236894224386",
#         24:"https://twitter.com/hawkgald/status/893866149913350144",
#         25:"https://twitter.com/hawkgald/status/893860584185241601",
#         26:"https://twitter.com/hawkgald/status/893840620506107904",
#         27:"https://twitter.com/hawkgald/status/893839902235742209",
#         28:"https://twitter.com/hawkgald/status/893827078147133440",
#         29:"https://twitter.com/hawkgald/status/1041530954500648960",
#         30:"https://twitter.com/hawkgald/status/1076465187094290432",
#         31:"https://twitter.com/hawkgald/status/1076729374089465859",
#         32:"https://twitter.com/hawkgald/status/1076751686637514758",
#         33:"https://twitter.com/hawkgald/status/1076752750396862464",
#         34:"https://twitter.com/hawkgald/status/1104499321976717312",
#         35:"https://twitter.com/hawkgald/status/1320038365748621313",
#         36:"https://twitter.com/hawkgald/status/1317349140116893696",
#         37:"https://twitter.com/moguru_taberu/status/1313298991421947904",
#         38:"https://twitter.com/hawkgald/status/1041968278170521600",
#         39:"https://twitter.com/Aoiro_Wolf/status/1034551688047280128",
#         40:"https://twitter.com/Aoiro_Wolf/status/1181092581477773312",
#         41:"https://twitter.com/lai_rr/status/1309932124460298240",
#         42:"https://twitter.com/lai_rr/status/1225865861405102080",
#         43:"https://twitter.com/Aoiro_Wolf/status/1127417817517608960",
#         44:"https://twitter.com/lai_rr/status/1083416404664045568",
#         45:"https://twitter.com/lai_rr/status/1250806063776952321",
#         46:"https://twitter.com/Aoiro_Wolf/status/1324654907199123457",
#         47:"https://twitter.com/moguru_taberu/status/1269947799681941505",
#         48:"https://twitter.com/moguru_taberu/status/1264958042807734274",
#         49:"https://twitter.com/moguru_taberu/status/1185363430867234816",
#         50:"https://twitter.com/moguru_taberu/status/1095637077180350464",
#         51:"https://twitter.com/moguru_taberu/status/1231056099178008576",
#         52:"https://twitter.com/moguru_taberu/status/1151136493538164737",
#         53:"https://twitter.com/lai_rr/status/1084203026238205952",
#         54:"https://twitter.com/hawkgald/status/1238557988031352832",
#         55:"https://twitter.com/lai_rr/status/1262820433323110400",
#         56:"https://twitter.com/lai_rr/status/1083807900252815360",
#         57:"https://twitter.com/hawkgald/status/1178290635742175233",
#         58:"https://twitter.com/lai_rr/status/1250086798748872705",
#         59:"https://twitter.com/hawkgald/status/1076428821656555520",
#         60:"https://twitter.com/lai_rr/status/953641339286990852"
#     }
#     if(len(flgdict)<a or a<1):
#         return "error!",len(flgdict)
#     else:
#         return flgdict[a],len(flgdict)
