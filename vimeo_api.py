import requests
import base64
import json
import re


from config import Config

vimeo_config = Config()

class Vimeo(object):

    def __init__(self, link):
        self.link = link
        self.client_identifier = vimeo_config.vimeo_client_identifier
        self.client_secret = vimeo_config.vimeo_client_secret
        self.resource_id = self.get_vimeo_id()
        self.access_token = self.get_access_token()

    def get_access_token(self):
        combined_ident_secret = "{}:{}".format(self.client_identifier, self.client_secret)

        str_encode_combined = str.encode(combined_ident_secret)

        base_64_str_encode = base64.b64encode(str_encode_combined)

        base_64_utf8_str_encode = base_64_str_encode.decode('utf-8')

        params = {'grant_type': "client_credentials"}

        header = {'Authorization': 'basic ' + base_64_utf8_str_encode}

        vimeo_authentication = requests.post("https://api.vimeo.com/oauth/authorize/client", params=params, headers=header)

        vimeo_auth_content = vimeo_authentication.content.decode('utf-8')

        vimeo_auth_content_json = json.loads(vimeo_auth_content)

        try:
            vimeo_access_token = vimeo_auth_content_json['access_token']
            return vimeo_access_token
        except KeyError:
            print("Something went wrong getting the vimeo key", vimeo_auth_content_json)


    def get_vimeo_id(self):
        vimeo_id_search = re.compile(r"(?:vimeo.com)\/(?:channels\/|channels\/\w+\/|groups\/[^\/]*\/videos\/|album\/\d+\/video\/|video\/|)(\d+)(?:$|\/|\?)")
        vimeo_url_id = vimeo_id_search.search(self.link)

        if vimeo_url_id:
            vimeo_resource_id = vimeo_url_id.group(1)
            return vimeo_resource_id


    def check_vimeo_embed(self):
        api_endpoint = "https://api.vimeo.com/videos/"
        video_resource = "{}{}".format(api_endpoint, self.resource_id)
        resource_get_header = {"Authorization": "Bearer {}".format(self.access_token)}

        print(self.resource_id)

        resource_get = requests.get(video_resource, headers=resource_get_header)
        data = json.loads(resource_get.content)
        print(data["embed"])


test = Vimeo("https://vimeo.com/374312058")
print(test.check_vimeo_embed())




