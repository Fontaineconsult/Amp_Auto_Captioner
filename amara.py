import requests
import json
import os
from config import Config

app_config = Config()


class Amara(object):

    def __init__(self, video_url, title):


        self.auth_header = {'X-api-username': app_config.amara_user_id, 'X-api-key': app_config.amara_key}
        self.video_url = video_url
        self.title = title
        self.metadata = None
        self.video_id = None


    def post_video(self):
        post_data = {

            "video_url": self.video_url,
            "title": self.title,
            "description": "Automator Test Job",
            "primary_audio_language_code": "en-US"
        }

        post_video = requests.post("https://amara.org/api/videos/", headers=self.auth_header, data=post_data)
        self.metadata = json.loads(post_video.content)
        self.video_id = self.metadata['id']

        print("Amara Video Located Here: amara.org/en/videos/{}".format(self.metadata['id']))
        return self.video_id

    def post_subtitle(self):

        with open(os.getcwd() + "\\srt_temp\\{}.srt".format(self.title), 'r') as srt:
            srt_string = srt.read()


        sub_post_data = {
            "subtitles": srt_string,
            "sub_format": "srt",
            "title": self.title,
            "is_complete": False
        }



        post_subtitles = requests.post("https://amara.org/api/videos/{}/languages/en-US/subtitles/".format(self.video_id),
                                       headers=self.auth_header,
                                       data=sub_post_data)
        print("Subtitles Posted", post_subtitles)

