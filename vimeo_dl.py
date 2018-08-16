
import requests
import base64
from tqdm import tqdm

login_info = {"username":"venuschw","password":"Venus2834"}

main_url = "https://www.billyshowell.com"
drawing_url = "https://www.billyshowell.com/membership/my-video-tutorials/34-my-tutorials/paid-tutorials/suitable-for-all/670-strawberry-leaf-tutorial"

def main():
    res = requests.post(main_url, login_info)
    session = requests.Session()

    cookie = res.headers["Set-Cookie"]

    resp = requests.get(drawing_url)
    return

def dl():
    master_json_url = 'https://50skyfiregce-vimeo.akamaized.net/exp=1534104796~acl=%2F277247049%2F%2A~hmac=b9c4eee6b9ffb13c2ffe48a1280a416d219d903d41780b1d4fdf90808203e1e7/277247049/sep/video/1036621174,1036621179,1036621173,1036621172/master.json?base64_init=1'
    base_url = master_json_url[:master_json_url.rfind('/', 0, -26) + 1]

    resp = requests.get(master_json_url)
    print (resp.text)
    content = resp.json()

    heights = [(i, d['height']) for (i, d) in enumerate(content['video'])]
    idx, _ = max(heights, key=lambda t: t[1])
    video = content['video'][idx]
    video_base_url = base_url + video['base_url']
    print ('base url:', video_base_url)

    filename = 'video_%d.mp4' % video['id']
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
    return

main()