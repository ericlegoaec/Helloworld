import os
import re
import requests
import base64
from moviepy.editor import VideoFileClip
from tqdm import tqdm

login_info = {"username":"venuschw","password":"Venus2834"}


# def main():
#     res = requests.post(main_url, login_info)
#     session = requests.Session()

#     cookie = res.headers["Set-Cookie"]

#     resp = requests.get(drawing_url)
#     return

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

    video_file = open(filename, 'wb')

    init_segment = base64.b64decode(video['init_segment'])
    video_file.write(init_segment)

    for segment in tqdm(video['segments']):
        segment_url = video_base_url + segment['url']
        resp = requests.get(segment_url, stream=True)
        if resp.status_code != 200:
            print ('not 200!')
            print (resp)
            print (segment_url)
            break
        for chunk in resp:
            video_file.write(chunk)

    video_file.flush()
    video_file.close()
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

    audio_file = open(filename, 'wb')

    init_segment = base64.b64decode(audio['init_segment'])
    audio_file.write(init_segment)

    for segment in tqdm(audio['segments']):
        segment_url = audio_base_url + segment['url']
        resp = requests.get(segment_url)
        if resp.status_code != 200:
            print ('not 200!')
            print (resp)
            print (segment_url)
            break
        for chunk in resp:
            audio_file.write(chunk)

    audio_file.flush()
    audio_file.close()
    return filename

def combine(video_file, audio_file):
    video_clip = VideoFileClip(video_file)
    video_clip.write_videofile(os.path.join("/Users/frederickli/Downloads", os.path.basename(video_file.replace("video_", ""))), audio=audio_file)
    os.remove(video_file)
    os.remove(audio_file)
    return

def main():
    url = input("Enter the master.json: ")
    video_file = video_dl(url)
    audio_file = audio_dl(url)
    # video_file = r"/Users/frederickli/Projects/video_393769816.mp4"
    # audio_file = r"/Users/frederickli/Projects/audio_393769817.mp4"
    combine(video_file, audio_file)
    return

if __name__ == "__main__":
    main()