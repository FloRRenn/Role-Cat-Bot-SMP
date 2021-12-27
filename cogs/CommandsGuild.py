from discord.ext import commands
from discord.ext.commands.core import guild_only
from discord.utils import get

import asyncio, discord
from .Ultils import *

channelNhaGiam = 920605313416192010
serverID = 909776530161426544

class CommandsGuild(commands.Cog):
    flagRoom = flagInvite = flagGiam = False
    
    def __init__(self, bot):
        self.bot = bot
        
    @guild_only()
    @commands.command(pass_context = True, aliases = ['room'])
    async def CreateRoom(self, ctx):
        if self.flagRoom == False:
            self.flagRoom = True
            
            database = getDatabase('CreateRoom')
            CurrentRoomInDatabase = database.count_documents({})
            
            if CurrentRoomInDatabase == 5:
                await ctx.send('Không thể tạo thêm channel vì đã đạt tới giới hạn. Vui lòng thử lại sau')
                return
            
            find = database.find_one({'onwerID' : ctx.author.id})
            if not find:
                msg = await ctx.send('Bạn có chắc là sẽ tạo phòng ko? Xin vui lòng đọc kỹ luật\nhttps://i.imgur.com/ieiZp4c.png')
                await ctx.send('=> Gõ **y** để đồng ý tạo phòng\n=> Gõ **từ khác** để không đồng ý')
                
                try:
                    mess =  await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 90)
                except asyncio.TimeoutError:
                    await ctx.send(f'**Hủy tạo phòng vì không nhận được phản hồi từ {ctx.author.mention}**')
                    return
                
                if mess.content.lower() == 'y':       
                    guild = ctx.guild
                    
                    channelName = ctx.author.name + '_no_scan'
                    roleName = f'Phòng của {ctx.author.name}'
                    
                    autorize_role = await guild.create_role(name = roleName)
                    category = discord.utils.get(ctx.guild.categories, id = 909776530614390795)
                    
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(read_messages = False),
                        guild.me: discord.PermissionOverwrite(read_messages = True),
                        autorize_role: discord.PermissionOverwrite(read_messages = True)
                    }
                    
                    await guild.create_text_channel(channelName, overwrites=overwrites, category=category)
                    await ctx.author.add_roles(autorize_role)
                    
                    await asyncio.sleep(0.2)
                    server = self.bot.get_guild(serverID)
                    
                    for channel in server.channels:
                        if channel.name == channelName:
                            break   
                        
                    info = {
                        'channelID' : channel.id,
                        'onwerID' : ctx.author.id,
                        'timeleft' : 60,
                        'roleName' : roleName
                    }
                    
                    database.insert_one(info)
                    await ctx.send(f'{ctx.author.mention} đã tạo kênh {channel.mention}, thời hạn sử dụng là **60 phút**')     
                    
                else:
                    await ctx.send('**Hủy tạo phòng**')
                    
            else:
                await ctx.send(f'**{ctx.author.mention}, bạn không thể tạo thêm kênh vì kênh mà bạn tạo trước đó vẫn chưa hết hạn.**')
                
            self.flagRoom = False
            
    @guild_only()
    @commands.command(pass_context = True, aliases = ['inv', 'invite'])
    async def Invite2Room(self, ctx,  member : discord.Member = None):
        if self.flagInvite == False:
            self.flagInvite = True
            
            database = getDatabase('CreateRoom')
            
            find = database.find_one({'onwerID' : ctx.author.id})
            if find:
                try:
                    msg = await ctx.send(f'**{member.mention} có muốn vào phòng của {ctx.author.mention} không?**')
                    try:
                        mess =  await self.bot.wait_for('message', check=lambda message: message.author.id == member.id, timeout = 90)
                        
                    except asyncio.TimeoutError:
                        await ctx.send(f'**Hủy lời mời vì không nhận được phản hồi từ {member.mention}**')
                        return
                    
                    if mess.content.lower() == 'y':
                        roleName = f'Phòng của {ctx.author.name}'
                        try:
                            role = get(self.bot.get_guild(serverID).roles, name = roleName)
                            await member.add_roles(role)
                            await ctx.send(f'**Đã mời {member.mention} vào phòng của {ctx.author.mention}.**')
                            
                        except:
                            await ctx.send('**Có vẻ là phòng của bạn đã không còn tồn tại.**')
                            
                    else:
                        await ctx.send(f'**{member.mention} không muốn vào phòng của {ctx.author.mention}.**')
                    
                except:
                    pass
            else:
                await ctx.send('Kênh bạn tạo có vẻ đã bị xóa hoặc Chỉ có chủ kênh mới có thể thực hiện lệnh này.')
                
            self.flagInvite = False       
        
    @commands.has_any_role('coder', 'Police', 'Admin', 'Owner')
    @commands.command(aliases = ['giam'], pass_context = True)
    @guild_only()
    async def GiamGiu(self, ctx, member : discord.Member, time : int = 15):   
        if self.flagGiam == False:
            self.flagInvite = True
            
            MUTED = getDatabase('MutedMember')
            find = MUTED.find_one({'memberID' : member.id})
            NhaGiam = self.bot.get_channel(channelNhaGiam)
            
            if not find:
                muted_role = get(self.bot.get_guild(serverID).roles, name = 'Muted')
                await member.add_roles(muted_role)
                
                info = {
                    'memberID' : member.id,
                    'timestamp' : time,
                    'isBot' : False
                }
                MUTED.insert_one(info)
                
                await ctx.send(f'Đã đưa {member.mention} vào {NhaGiam.mention} trong {time} phút')
                await NhaGiam.send(f'{member.mention} đã sẽ bị giam ở đây {time} phút. Lệnh được đưa ra từ {ctx.author.mention}.')
            
            else:
                await ctx.send(f'{member.mention} đã bị đưa vào {NhaGiam.mention} trước đó.')
                
            self.flagGiam = False
        
        
def setup(bot):
    bot.add_cog(CommandsGuild(bot))