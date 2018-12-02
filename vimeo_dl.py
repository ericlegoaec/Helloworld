import os
import re
import requests
import base64
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import multiprocessing
from multiprocessing.pool import ThreadPool

login_info = {"username":"venuschw","password":"Venus2834"}


# def main():
#     res = requests.post(main_url, login_info)
#     session = requests.Session()

#     cookie = res.headers["Set-Cookie"]

#     resp = requests.get(drawing_url)
#     return

def dl_segment(url):
    print (url)
    resp = requests.get(url)
    return resp

def multi_dl(base_url, data, filename):
    media_file = open(filename, 'wb')

    init_segment = base64.b64decode(data['init_segment'])
    media_file.write(init_segment)
    
    seg_arr = list(map(lambda x: x["url"], data["segments"]))
    seg_arr = sorted(seg_arr, key=lambda x: int(x[7:-4]), reverse=True)
    urls_arr = list(map(lambda x: base_url + x, seg_arr))

    p = ThreadPool(multiprocessing.cpu_count())
    results = p.map(dl_segment, urls_arr)
    for resp in results:
        for chunk in resp:
            media_file.write(chunk)
    media_file.flush()
    media_file.close()
    return

def video_dl(master_json_url):
    base_url = master_json_url[:master_json_url.rfind('/', 0, -26) + 1]

    resp = requests.get(master_json_url)
    content = resp.json()

    heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    print (heights)
    idx, _ = max(heights, key=lambda t: t[1])
    video = content['video'][idx]
    video_base_url = base_url + video['base_url']
    print ('base url:', video_base_url)
    filename = 'video_%s.mp4' % video['id']
    print ('saving to %s' % filename)

    multi_dl(video_base_url, video, filename)
    return filename

def audio_dl(master_json_url):
    base_url = master_json_url[:master_json_url.rfind('/', 0, -26) + 1]

    resp = requests.get(master_json_url)
    content = resp.json()

    audio = content['audio'][0]
    audio_base_url = base_url + audio['base_url']
    audio_base_url = re.sub(r"\/[a-z]*\/\.\.", "", audio_base_url)
    print ('base url:', audio_base_url)
    filename = 'audio_%s.mp4' % audio['id']
    print ('saving to %s' % filename)

    multi_dl(audio_base_url, audio, filename)
    return filename

def combine(video_file, audio_file):
    video_clip = VideoFileClip(video_file)
    video_clip.write_videofile(os.path.join("/Users/frederickli/Downloads", os.path.basename(video_file.replace("video_", ""))), audio=audio_file)
    os.remove(video_file)
    os.remove(audio_file)
    return

def main():
    url = "https://skyfire.vimeocdn.com/1543522346-0x14f3ceab98ff6be39727f351deff0c88e7b9aa38/301441808/sep/video/1152474535,1152474555,1152474553,1152474549/master.json?base64_init=1"
    #url = input("Enter the master.json: ")
    # video_file = video_dl(url)
    # audio_file = audio_dl(url)
    video_file = "/Users/frederickli/Projects/video_1152474549.mp4"
    audio_file = "/Users/frederickli/Projects/audio_1152474535.mp4"
    combine(video_file, audio_file)
    return

if __name__ == "__main__":
    main()