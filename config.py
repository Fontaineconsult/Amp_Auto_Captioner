import yaml


class Config(object):

    def __init__(self):
        self.amara_user_id = None
        self.amara_key = None
        self.youtube_key = None
        self.vimeo_client_identifier = None
        self.vimeo_client_secret = None
        self._load_config()


    def _load_config(self):

        with open(r'config.yaml') as file:
            config = yaml.load(file)

            self.amara_user_id = config['amara_user_id']
            self.amara_key = config['amara_key']
            self.youtube_key = config['youtube_key']
            self.vimeo_client_identifier = config['vimeo_client_identifier']
            self.vimeo_client_secret = config['vimeo_client_secret']





