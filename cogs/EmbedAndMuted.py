import aiohttp, io
from .Ultils import *
from .NudeDetect import NudeClassifier
from PIL import Image

webDetect = ['sex', 'kheu-dam', 'vung-trom', 'lam-tinh', 'porn', 'hentai', 'loan-luan', 'hiep-dam', 'hiepdam', 
            'vungtrom', 'lamtinh', 'loanluan', 'quay-len', 'quaylen', 'nude', 'vlxx', 'xvideo', 'xnxx', 'jav', 'pixiv',
            'milf', 'cum', 'blowjob', 'pussy', 'dick', 'boob', 'butt', 'tits', 'rape','handjob','cock','bdsm','gangbang','orgy','femdom','nsfw','anal']

elgalWeb = ['facebook.com', 'youtube.com', 'minecraft', 'steam.com', 'epic.com', 'google.com', 'catsmp.ga', 'minexyzvn.tk', 'youtu.be', 'tenor.com', 'giphy.com']

MAXIMUM_TIMES = 10

async def isNude(url, attachment):
    if url != None:
        if any(word in url for word in webDetect):
            return 100
        
        if any(word in url for word in elgalWeb):
            return 0
    
    #If member sends attachment => Get link attachment
    elif len(attachment) > 0:
        url = getURLimage(attachment)
        
    #If nothing   
    if url == None:
        return 0
    
    #If link is a video
    if '.mp4' in url.lower() or '.mov' in url.lower():
        return 3
    
    image_formats = ("image/png", "image/jpeg", "image/jpg", 'image/webp', 'image/gif')
    
    #download
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            try:
                ContentType = resp.headers['Content-Type']
            except:
                #If cant find type of URL
                return 10

            url = url.lower()
            
            #If is image or gif
            if ContentType in image_formats or url.endswith('gif') or url.endswith('gifv'):
                #download GIF
                if '.gif' in url or '.gifv' in url:
                    with open('image.gif', 'wb') as f:
                        f.write(await resp.read())
                    img = Image.open('image.gif').convert('RGB')
                
                #download Image   
                else:
                    img = Image.open(io.BytesIO(await resp.read()))
                
                #Save image
                try:   
                    img.save('image.jpg')
                
                except:
                    rgb_im = img.convert('RGB')
                    rgb_im.save('image.jpg')

                classifier = NudeClassifier()
                res = float(classifier.classify('image.jpg')['image.jpg']['unsafe']) * 100
                return round(res, 2) 

            #Something else
            else:
                return 10

def MuteInMinutes(times):
    if times in [1,2,4,6,8,10]:
        return False, 0
    
    MutedTime = [0, 15, 30, 60, 720]
    slot = (times - 1)//2
    
    return True, MutedTime[slot]     
            
def MuteMember(memberID : int):
    database = getDatabase("ViPham")
    getMemberInfo = database.find_one({'memberID' : memberID})
    times = 1
    
    if not getMemberInfo:
        info = {
                'memberID' : memberID,
                'times' : times,
            }
        database.insert_one(info)
        
        isBAN = False
        isMute = True
        duration = 720
    
    else:
        times = getMemberInfo['times']
        times += 1 #Tăng lên 1 khi vi phạm
        
        if times > MAXIMUM_TIMES:
            getMemberInfo.delete_one({'memberID' : memberID})
            isBAN = True
            isMute = False
            return (isMute, isBAN, 0, 0)
        
        database.update_one({'memberID' : memberID}, {"$set" : {'times' : times}})
        
        isBAN = False
        isMute, duration = MuteInMinutes(times)
        
    if isMute:
        info = {
            'memberID' : memberID,
            'timestamp' : duration
        }
        
        MuteDB = getDatabase('MutedMember')
        MuteDB.insert_one(info)
        
    return (isMute, isBAN, duration, times)
        
        
        
        