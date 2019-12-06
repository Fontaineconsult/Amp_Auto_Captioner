import requests
import json
import re
from config import Config

youtube_config = Config()

class YouTube(object):


    def __init__(self, link):

        self.link = link
        self.key = youtube_config.youtube_key
        self.payload = {
            'part':'status',
            'id': '',
            'key': self.key
        }

    def build_payload(self, id):

        payload = self.payload
        payload['id'] = id
        return payload

    def get_id(self):
        youtube_regex = re.compile(r'((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)')
        youtube_id_search = youtube_regex.search(self.link)
        return youtube_id_search.group(4)

    def is_embeddable(self):
        youtube_search = requests.get("https://www.googleapis.com/youtube/v3/videos?", params=self.build_payload(self.get_id()))
        content = json.loads(youtube_search.content.decode('utf-8'))

        return content['items'][0]['status']['embeddable']













