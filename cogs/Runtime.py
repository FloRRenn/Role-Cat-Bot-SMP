from discord.ext import commands, tasks
from discord.utils import get

import asyncpg
from .Ultils import *

channelTBViPham = 913655584446894170
channelNhaGiam = 920605313416192010
serverID = 909776530161426544

class Runtime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(serverID)
        
        self.UnMuted.add_exception_type(asyncpg.PostgresConnectionError)
        self.deleteRoom.add_exception_type(asyncpg.PostgresConnectionError)
        
        self.UnMuted.start()
        self.deleteRoom.start()
        
    @tasks.loop(minutes = 1)
    async def UnMuted(self):
        UNMUTED = getDatabase('MutedMember')
        allMember = UNMUTED.find({})
        
        muted_role = get(self.guild.roles, name = 'Muted')
        
        for member in allMember:
            timeLeft = member['timestamp'] - 1
            
            if timeLeft <= 0:
                try:
                    getUser = self.guild.get_member(member['memberID'])
                    await getUser.remove_roles(muted_role)
                except:
                    pass
                
                UNMUTED.delete_one({'memberID' : member['memberID']})
                
            else:
                UNMUTED.update_one({'memberID' : member['memberID']}, {'$set' : {'timestamp' : timeLeft}})
                
    @tasks.loop(minutes = 1)
    async def deleteRoom(self):
        room = getDatabase('CreateRoom')
        find = room.find({})

        for i in find:
            timeleft = i['timeleft'] - 1
            channelID = i['channelID']
            channel = self.bot.get_channel(channelID)
            
            if timeleft == 0:
                roleName = i['roleName']

                role = get(self.guild.roles, name = roleName)
                
                await role.delete()
                await channel.delete()
                room.delete_one({'channelID' : channelID})
                return
                    
            if timeleft == 10:
                await channel.send('Kênh này sẽ bị xóa trong **10 phút** nữa.')
                
            elif timeleft == 5:
                await channel.send('Còn **5 phút** trước khi kênh bị xóa.')
                
            elif timeleft == 1:
                await channel.send('Sẽ xóa kênh sau **1 phút** nữa.')
                
            room.update_one({'channelID' : channelID}, {'$set' : {'timeleft' : timeleft}})
            
    @UnMuted.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

    @deleteRoom.before_loop
    async def before(self):
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(Runtime(bot))