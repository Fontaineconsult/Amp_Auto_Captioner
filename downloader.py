from __future__ import unicode_literals
import os
import youtube_dl


extension = '\\video_temp\\%(title)s.%(ext)s'
current_dir = os.getcwd()


##! make sure file name fits in windows limit

class VideoDownload(object):

    def __init__(self, url):
        self.url = url
        self.video_info = self._get_info()
        self.fixed_title = self.clean_filename(self.video_info['title'])
        self.extension = '\\video_temp\\{}.%(ext)s'.format(self.fixed_title)
        self.options = {'outtmpl': current_dir + self.extension,
                        'forcefilename': False,
                        'format': 'mp4',
                        'progress_hooks': [self.hook],
                        }


    def _get_info(self):

        with youtube_dl.YoutubeDL() as ydl:
            return ydl.extract_info(self.url, download=False)


    def download(self):

        with youtube_dl.YoutubeDL(self.options) as ydl:

            ydl.download([self.url])

    def clean_filename(self, title):

        new_title = title.replace('/', '') \
            .replace('.', ' ') \
            .replace(':','') \
            .replace('?','') \
            .replace("'",'') \
            .replace('"','') \
            .replace(',','') \
            .replace(' ','-') \
            .replace('|', '')

        return new_title


    def hook(self, d):
        pass




