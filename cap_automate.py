from downloader import VideoDownload
from aws_core import AWStranscribe, S3Upload
import time, os, re
import srtUtils as srt
from amara import Amara
import glob
import shutil
from pathlib import Path
from youtube_api import YouTube




class AutoCaption(object):

    def __init__(self, video_link):
        self.video_link = video_link
        self.video_download = None
        self.S3Uploader = None
        self.transcription = None
        self.video_title = None
        self.transcription_downloaded = False
        self.srt_string = None
        self.host_link = None
        self.amara = None


    def verify_link_type(self):

        if re.match(re.compile('C:\\.*.|Z:\\.*.'), self.video_link):
            return True
        return False

    def copy_video(self):
        path = Path(self.video_link)
        title = path.name
        suffix = path.suffix
        title = title.split(".")[0]
        self.video_title = clean_filename(title)
        shutil.copyfile(self.video_link, os.getcwd() + "\\video_temp\\{}{}".format(clean_filename(title), suffix))
        self.video_link = os.getcwd() + "\\video_temp\\{}{}".format(clean_filename(title), suffix)

    def download_video(self):

        self.video_download = VideoDownload(self.video_link)
        self.video_download.download()
        self.video_title = self.video_download.fixed_title



    def upload_to_S3(self):
        self.S3Uploader = S3Upload(self.video_title)
        self.S3Uploader.upload_to_bucket()

    def transcribe(self):
        self.transcription = AWStranscribe(self.S3Uploader)
        self.transcription.start_transcribe()

    def download_transcription(self):
        self.transcription_json = self.transcription.download_json()


    def create_SRT(self):
        srt.writeTranscriptToSRT(self.transcription_json,
                                 "en-us",
                                 os.getcwd() + "\\srt_temp\\{}.srt".format(self.S3Uploader.aws_title))


    def verify_embed(self):

        verify = VerifyEmbed(self.video_link)
        verify = verify.route_to_api()

        if verify:
            self.host_link = self.video_link
        if not verify:
            self.host_link = self.S3Uploader.media_uri



    def create_amara_resource(self):
        self.amara = Amara(self.host_link, self.S3Uploader.aws_title)
        self.amara.post_video()
        self.amara.post_subtitle()


    def cleanup(self):
        srt_files = glob.glob(os.getcwd() + "\\srt_temp\\*")
        for f in srt_files:
            os.remove(f)

        video_files = glob.glob(os.getcwd() + "\\video_temp\\*")
        for f in video_files:
            os.remove(f)


    def auto_caption(self):


            if self.verify_link_type():
                print("Copying Video")
                self.copy_video()
            else:
                print("Downloading")
                self.download_video()

            print("Uploading")
            self.upload_to_S3()

            print("Transcribing")
            self.transcribe()

            while not self.transcription.complete:
                self.transcription.update_status()
                print(self.transcription.status)
                time.sleep(10)

            if self.transcription.complete:
                self.download_transcription()
                self.transcription_downloaded = True

            if self.transcription_downloaded:
                self.create_SRT()
            self.verify_embed()
            self.create_amara_resource()
            self.cleanup()


            print("Done")


class VerifyEmbed(object):

    def __init__(self, link):

        self.link = link
        self.regex = re.compile('(.*.youtube.com.*.|.*.youtu.be.com.*.|.*.youtu.be.*.)|(.*.vimeo.com.*.|.*.player.vimeo.com.*.)|(.*.dailymotion.com.*.)')


    def route_to_api(self):

        match =re.match(self.regex, self.link)

        if match is None:
            return False
        if match.group(1):
            yt_embed = YouTube(self.link)
            return yt_embed.is_embeddable()
        if match.group(2):
            return False
        if match.group(3):
            return False
        else:
            return False


def clean_filename(title):

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


test = AutoCaption("https://www.youtube.com/watch?v=qLkYNFyjWl0")
test.auto_caption()