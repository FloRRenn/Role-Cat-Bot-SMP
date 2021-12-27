from discord.ext import commands
from discord.ext.commands.core import guild_only

import asyncio, os, requests, json
from .Ultils import *

class AdminCommands(commands.Cog):
    flagAdd = flagEmbed = False
    
    def __init__(self, bot):
        self.bot = bot
        
    def download(url: str, dest_folder: str, filename):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder) 

        file_path = os.path.join(dest_folder, filename)

        r = requests.get(url, stream=True)
        if r.ok:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
            return True
                        
        else: 
            return False
        
    @guild_only()
    @commands.has_any_role('coder', 'Admin', 'Owner')
    @commands.command(pass_context = True, aliases = ['word', 'add'])
    async def AddBadWords(self, ctx, *, BADWords : str = None):
        if self.flagAdd == False:
            self.flagAdd = True
            
            if BADWords == None:
                await ctx.send('Không ghi gì sao thêm đc :)')
                return
            
            database = getDatabase('ViPham')
            getList = database.find_one({'_id_' : 0})
            getListWords = getList['badWordsList']
            
            ListAddBadWords = BADWords.split(',')
            for word in ListAddBadWords:
                if word not in getListWords:
                    getListWords.append(word)
                    
            print(getListWords)
            database.update_one({'__id__' : 0}, {'$set' : {'badWordsList' : getListWords}})
            await ctx.send('**Đã thêm thành công**')
            
            self.flagAdd = False
    
    @guild_only()
    @commands.has_any_role('coder', 'Admin', 'Owner')
    @commands.command(pass_context = True, aliases = ['embed'])
    async def CreateEmbedFromFile(self, ctx):
        if self.flagEmbed == False:
            self.flagEmbed = True
            
            if len(ctx.message.attachments) == 0:
                await ctx.send(file=discord.File(os.getcwd() + '/embed.json'))
                await ctx.send('Tải file trên về và điền thông tin vào các phần ghi bằng **TIẾNG VIỆT**, không ghi vào phần tiếng anh và không được xóa dấu **" "**\nSau khi điền xong thì upload file theo hình bên dưới')
                await ctx.send('https://i.imgur.com/3OQZTee.png')
                await ctx.send('Cách bố trí như sau: ')
                
                show = discord.Embed(title = 'Tên tiêu đề', description = 'Mô tả tiêu đề', color = 0x57F312)
                show.set_author(name = 'Tên tác giả')
                show.set_thumbnail(url = 'https://i.imgur.com/1u1br1j.png')
                show.set_image(url = 'https://i.imgur.com/ubDH3nw.gif')
                show.add_field(name = 'Trường 1', value = 'Mô tả trường 1', inline = True)
                show.add_field(name = 'Trường 2', value = 'Mô tả trường 2', inline = True)
                await ctx.send(embed = show)
                
            else:
                try:
                    self.download(ctx.message.attachments[0].url, 'Embed', ctx.message.attachments[0].filename)
                    
                    with open(os.getcwd() + f'/Embed/{ctx.message.attachments[0].filename}', 'r', encoding='utf-8') as f:
                        a = json.loads(f.read())
                except:
                    await ctx.send('File bị lỗi:\n1. Lỡ xóa nhầm dấu `,` hoặc `" "` ở đâu đó.\n2. Sai định dạng file (Định dạng phải là .json).')
                    return
                
                try:
                    show = discord.Embed()
                    if a['title'] != "":
                        show.title = a['title'] 
                    
                    if a['description'] != "" and len(a['description']) <= 4096:
                        show.description = a['description']
                        
                    elif len(a['description']) > 4096:
                        await ctx.send('Nội dung Desciption chỉ chứa được 4096 ký tự\n==> **Hủy tạo thông báo**')
                        return
                        
                    show.color =  int(a['color'], 16)
                    
                    if a['thumbnail'].startswith("https"):
                        try:
                            show.set_thumbnail(url = a['thumbnail'])
                        except:
                            await ctx.send('**Link ảnh thumbnail** không tồn tại\n==> **Hủy tạo thông báo**')
                            return
                        
                    if a['image'].startswith("https"):
                        try:
                            show.set_image(url = a['image'])
                        except:
                            await ctx.send('**Link ảnh chống trôi** không tồn tại\n==> **Hủy tạo thông báo**')
                            return
                        
                    if a['author'] != '':
                        avartar = a['avatar_author']
                        if not a['avatar_author'].startswith("https"):
                            avartar = 'https://i.imgur.com/DgNBF00.png'
                            
                        try:
                            show.set_author(name = a['author'], icon_url = avartar)
                        except:
                            await ctx.send('Trường **author** bị sai format hoặc **link ảnh author** không tồn tại\n==> **Hủy tạo thông báo**')
                            return
                        
                    count = 1
                    for i in list(a['fields']):
                        if i["name"] == ''  and i["value"] == '':
                            continue
                            
                        elif len(i["name"]) > 256 or len(i["value"]) > 1024:
                            show.add_field(f'Trường {count} bị sai format, **name** chỉ chứ được 256 ký tự và **value** chỉ chứa được 1024 ký tự\n==> **Hủy tạo thông báo**')
                            return
                        
                        elif i["name"] != '' and i["value"] != '':
                            show.add_field(name = i["name"], value = i["value"], inline = True)
                        
                        count += 1
                    
                    await ctx.send(embed = show)
                    
                    await ctx.send('**Thông báo như vậy đã ổn chưa? Nhập Y hoặc N**')
                    try:
                        mess =  await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 90)
                    except asyncio.TimeoutError:
                        await ctx.send('**Hủy gửi thông báo vì không nhận được phản hồi là "Y" hoặc "N" từ người dùng**')
                        return
                    
                    if mess.content.lower() == 'y':
                        while True:
                            await ctx.send('**Nhập ID channel cần gửi (Có thể nhập nhiều ID cùng lúc, ngăn cách chúng bởi dấu phẩy):**')
                            try:
                                mess =  await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout = 180)
                            except asyncio.TimeoutError:
                                await ctx.send('**Hủy gửi thông báo vì không nhận đc ID**')
                                break

                            channels = str(mess.content).split(',')
                            allowed_mentions = discord.AllowedMentions(users = True, roles = True, everyone = True)
                            for id in channels:
                                try:
                                    channel = self.bot.get_channel(int(id))
                                    await channel.send(embed = show, allowed_mentions = allowed_mentions)
                                    await ctx.send(f'Đã gửi thông báo đến channel {channel.mention}')
                                except:
                                    await ctx.send(f'**ID ```{id}``` không khớp với bất kỳ channel nào**')
                                    continue
                            break
                                
                    else:
                        await ctx.send('**Hủy gửi thông báo**')
                        
                except:
                    await ctx.send('**Đã xảy ra lỗi trong quá trình tạo thông báo. Vui lòng kiểm tra lại file.**') 
                    
            self.flagEmbed = False       
        
def setup(bot):
    bot.add_cog(AdminCommands(bot))