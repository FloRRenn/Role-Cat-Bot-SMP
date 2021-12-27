import pymongo, discord, os

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
databaseName = os.environ.get("DATABASE")
cluster = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.y5mnt.mongodb.net/{databaseName}?retryWrites=true&w=majority")
db = cluster.insta 

def getURLimage(attachments):
    imgType = [ "jpg", "gif", "png", "webp", "psd","bmp", "pspimage", "thm",
            "tif", "yuv", "ai", "drw", "eps", "ps", "svg", "tiff",
            "jpeg", "jif", "jfif", "jp2", "jpx", "j2k", "j2c", "fpx",
            "pcd", "pdf", 'gifv']

    try:
        data = attachments[0]
        file = data.filename

        for image_type in imgType:
            if file.endswith(image_type):
                return data.url
        return None
    
    except:
        return None

def getDatabase(name : str):
    return db[name]    

def GetWordList():
    MutedDB = getDatabase("ViPham")
    return MutedDB.find_one({'_id_' : 0})['badWordsList']

def chatLogs(author : str, id, nick : str):
    log = getDatabase('chatLog')
    
    find = log.find_one({'_id_' : id})
    if not find:
        log.insert_one({
            '_id_' : id,
            'name' : author,
            'nickname' : nick,
            'times' : 0
            })  
        
    else:
        log.update_one({'_id_' : id}, {'$set' : {
            'times' : find['times'] + 1,
            'nickname' : nick,
        }})   
        
def CreateEmbed(who : str, channel, times : int, reason : str, dosomething : str, avatar_url : str, message_content : str = None):
    embed = discord.Embed(title = 'Thông tin vi phạm', color = 0xE74C3C)
    
    try:
        embed.add_field(name = 'Người vi phạm', value = who.mention, inline = False)
    except:
        embed.add_field(name = 'Người vi phạm', value = who, inline = False)
        
    embed.add_field(name = 'Tại kênh', value = channel.mention, inline = False)
    embed.add_field(name = 'Lần vi phạm', value = times, inline = True)
    embed.add_field(name = 'Lý do', value = reason, inline = True)
    embed.add_field(name = 'Hình thức xử lý', value = dosomething, inline = False)
    embed.set_thumbnail(url = avatar_url)  
    
    if len(message_content) > 1024:
            message_content = message_content[:1024]
    embed.add_field(name = 'Nội dung tin nhắn', value = message_content, inline = False)
    
    return embed
    