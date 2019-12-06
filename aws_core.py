import boto3
import os
import requests
import time
import json
import re

# Must configure AWS CLI first https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html


class S3Upload(object):

    def __init__(self, video_title=None):
        self.s3 = boto3.resource('s3')
        self.local_file = os.getcwd() + '\\video_temp\\{}.{}'.format(video_title, 'mp4')
        self.s3_resource = None
        self.aws_title = self._fix_filenames(video_title)
        self.media_uri = "https://s3.us-west-2.amazonaws.com/amp-video-host/{}.{}".format(self.aws_title, "mp4")


    def upload_to_bucket(self):
        print("uploading")
        self.s3.meta.client.upload_file(self.local_file, 'amp-video-host', self.aws_title + ".mp4")


    def _fix_filenames(self, title):
        title = title.replace(" ", "_")

        regex = re.compile("^[0-9a-zA-Z._-]+")
        new_title = ''

        for letter in title:
            if re.match(regex, letter) is not None:
                new_title += letter


        return new_title

class AWStranscribe(object):

    def __init__(self, S3Upload=None):
        self._upload_obj = S3Upload
        self.transcribe = boto3.client('transcribe')
        self.file = S3Upload.aws_title
        self.transcription = None
        self.metadata = None
        self.status = None
        self.complete = False

    def start_transcribe(self):

        self.transcribe.start_transcription_job(
            TranscriptionJobName=self._upload_obj.aws_title,
            LanguageCode='en-US',
            MediaFormat='mp4',
            Media= {'MediaFileUri': self._upload_obj.media_uri},
            Settings={
                'ShowSpeakerLabels': False,
                'ChannelIdentification': False,
                'ShowAlternatives': False,
            }

        )

        self.metadata = self.transcribe.get_transcription_job(TranscriptionJobName=self._upload_obj.aws_title)



    def update_status(self):

        self.metadata = self.transcribe.get_transcription_job(TranscriptionJobName=self._upload_obj.aws_title)
        self.status = self.metadata['TranscriptionJob']['TranscriptionJobStatus']

        if self.metadata['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
            self.complete = True

        return self.complete

    def download_json(self):

        if self.complete:
            transcript = requests.get(self.metadata['TranscriptionJob']['Transcript']['TranscriptFileUri'])
            data = json.loads(transcript.content)
            return data












