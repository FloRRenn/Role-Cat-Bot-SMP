from discord.ext import commands
from discord.utils import get

from .Ultils import *
import re, discord, random
from .EmbedAndMuted import *

from antispam.plugins import AntiSpamTracker
from antispam import AntiSpamHandler, Options

channelTBViPham = 913655584446894170
channelNhaGiam = 920605313416192010
serverID = 909776530161426544

class BotEvent(commands.Cog):
    flagError = False
    def __init__(self, bot):
        self.bot = bot
        self.bot.handler = AntiSpamHandler(bot, options = Options(no_punish = False,  message_duplicate_count = 5))
        self.bot.tracker = AntiSpamTracker(bot.handler, 5)
        self.bot.handler.register_plugin(bot.tracker)
        
        self.NOT_MANAGE_USERS = [840064704968785951, 660730514533122049, 729284476336603228, 869158558720221224]
        # mg2h#2730 - NDTk2#5031 - KurumiFake#7005 - Cá provip#0886
        
        self.NOT_MANAGE_CHANNELS = [909795716375912468, 909824864280543302, 909991284096237598, 923126983225933854, 909776530614390796, 912654355004522527, 913298625566740592, 913332480872972328, 923469376760479814, 923165635511455764, 913655584446894170, 909809672393998396, 912218797832810597, 920605313416192010]
        #chat-log, server-console, server-test,....
        
        self.ViPhamChannel = bot.get_channel(channelTBViPham)
        self.NhaGiam = bot.get_channel(channelNhaGiam)
        
        #Get list words
        self.WordsList = GetWordList()
        self.RANDOM_WARNING_MESSAGES = ['Nào, làm người có văn hóa đi bạn', 'Thích ăn kick không?', 'Bạn mà vi phạm 10 lần là bay ra khỏi server nha', 'Đừng chửi bậy chứ', 'Làm người văn hóa không khó :)', 'Bình tĩnh lại nào bạn tui', ':)']
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        database = getDatabase('MutedMember')
        find = database.find_one({'memberID' : member.id})

        if find is not None:
            muted_role = get(self.bot.get_guild(serverID).roles, name = 'Muted')
            await member.add_roles(muted_role)
            
            timeleft = find["timestamp"]
            database.update_one({'memberID' : member.id} , {"$set" : {'timestamp' : timeleft + 30}})
            await self.NhaGiam.send(f'{member.mention} định trốn tội à?? Không dễ đâu bạn!!!\nVì bạn cố tình dùng bug để lách luật nên thời gian bị giam của bạn sẽ tăng thêm 30 phút.\nThay vì được thả ra sau **{timeleft} phút** nữa, do hành động nông nổi, bạn sẽ được thả ra sau  **{timeleft + 30} phút** :))')

        role = get(member.guild.roles, name = 'Member')
        await member.add_roles(role)
        
        if not find:
            await member.send(f'Xin chào!! Cảm ơn bạn đã tham gia sever SMP của mình. Vui lòng vào kênh {self.bot.get_channel(909991284096237598).mention} xem rõ nội quy của server mình!!!')    
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        global flagError
        
        if self.flagError == False:
            self.flagError = True
            
            if isinstance(error, commands.MissingAnyRole):
                await ctx.send(f'{ctx.author.mention} có muốn trải nghiệm nhà giam trước không?\n Chỉ có role `Owner` `Admin` `coder` `Police` mới được phép dùng lệnh này.')
            
            self.flagError = False
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # If bot => Do nothing
        if message.author.bot:
            return
        
        # If high-level member => Do nothing
        if message.author.id in self.NOT_MANAGE_USERS:
            return
        
        # Dont scan all channels in NOT_MANAGE_CHANNELS and private temp channels
        if message.channel.id in self.NOT_MANAGE_CHANNELS or 'no_scan' in message.channel.name:
            return
        
        # Get message conntent for scanning
        mess = message.content.lower()
        
        # Scam => Ban
        if 'everyone' in mess and ('nitro' in mess or 'gift' in mess):
            reason = 'Scam'
            
            await message.author.send('Thích scam à, CÚT!!!\nAre you scamming?? Seriously, fuck you!\nGet out of my server.\nhttps://i.imgur.com/HVTSjnc.jpeg')
            embed = CreateEmbed(message.author, message.channel, 
                                'Không cần thiết', reason, 
                                'Ban', message.author.avatar_url, mess)
            
            await self.ViPhamChannel.send(embed = embed)
        
            try:
                await message.author.ban(reason = reason)
            except:
                await self.ViPhamChannel.send(f'Không thể ban {message.author}')
            return
        
        try:
            isURL = re.search("(?P<url>https?://[^\s]+)", message.content).group("url")
        except:
            isURL = None
           
        #Detect NSFW 
        if isURL or len(message.attachments) > 0:
            prediction = await isNude(isURL, message.attachments)
            
            #is NSFW
            if prediction >= 75:
                reason = 'Gửi link 18+'
                
                try:
                    await message.author.ban(reason = reason)
                    #await message.channel.send(f'Đã ban {message.author}')
                except:
                    await self.ViPhamChannel.send(f'**Không thể ban {message.author.mention} ({message.author})**')
                    
                embed = CreateEmbed(message.author, message.channel, 0, reason, 'Ban', message.author.avatar_url, mess)
                await self.ViPhamChannel.send(embed = embed)
             
            #Cant define URL   
            elif prediction == 10:
                allowed_mentions = discord.AllowedMentions(everyone = True)
                
                embed = discord.Embed(title = 'Không thể xác định', description = 'Không xác định được đây có phải link 18+ hay không? Vui lòng kiểm tra lại.', color = 0xE74C3C)
                embed.add_field(name = 'Người gửi', value = f'{message.author.mention} ({message.author})', inline = True) 
                embed.add_field(name = 'Tại kênh', value = message.channel.mention, inline = True)
                
                if len(message.content) > 1024:
                    content = message.content[:1024]
                embed.add_field(name = 'Link (cẩn thận khi bấm vào)', value = content, inline = False)
                embed.set_thumbnail(url = message.author.avatar_url)
                
                await self.ViPhamChannel.send(content = "@everyone", allowed_mentions = allowed_mentions, embed = embed)  
                
            elif prediction == 3:
                await message.delete()
                await message.channel.send(f'Xin lỗi {message.author.mention}, mình không cho phép gửi video ở đây, lý do là vì nếu không may 1 thành viên nào đó có thể né được kiểm duyệt và gửi video 18+ thì khá là phiền phức cho server. Nếu bạn thật sự muốn gửi video này thì bạn hãy up nó lên [Youtube](https://youtube.com/) và gửi link youtube đó vào lại đây hoặc là chụp màn hình phần video đó.')
            
            return  
        
        #Cho lọc member vào tuần tới   
        chatLogs(message.author.name + '#' + message.author.discriminator, message.author.id, message.author.nick)    
        
        #Bad words
        listWordinMessContent = mess.split(' ')
        if any(word in listWordinMessContent for word in self.WordsList):
            await message.delete()
            result = MuteMember(message.author.id)
                
            #isBan = True
            if result[1] == True:
                reason = 'Chửi bậy quá nhiều'
                DoSomething = 'Ban'
                
                message.author.ban(reason)
            
            #isMute = True
            elif result[0] == True:
                mute_role = get(self.bot.get_guild(serverID).roles, name = 'Muted')
                await message.author.add_roles(mute_role)
                
                await message.channel.send(f'{message.author.mention} đã bị đưa vào {self.NhaGiam.mention} trong {result[2]} phút để xám hối')
                await self.NhaGiam.send(f'{message.author.mention}, bạn đã bị muted trong {result[2]} phút.')
                
                reason = 'Chửi bậy quá nhiều'
                DoSomething = f'Đưa vào nhà giam {result[2]} phút'
                             
            else:
                await message.channel.send(f'{random.choice(self.RANDOM_WARNING_MESSAGES)}\n{message.author.mention} đã vi phạm **{result[3]} lần**')
                
                reason = 'Dùng từ tục'
                DoSomething = 'Cảnh cáo'
              
            embed = CreateEmbed(message.author, message.channel, result[3], reason, DoSomething, message.author.avatar_url, mess)  
            await self.ViPhamChannel.send(embed = embed)
            return
          
        #Track spamming      
        else:
            await self.bot.handler.propagate(message)
            await self.bot.process_commands(message)   

def setup(bot):
    bot.add_cog(BotEvent(bot))