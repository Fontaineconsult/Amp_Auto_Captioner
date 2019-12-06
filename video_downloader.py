from __future__ import unicode_literals
import youtube_dl
import boto3
import os
import time
import requests, json
import srtUtils as srt

amara_username = 'captions2'
amara_api_key = "c639e50c5ac807d3dd828396ce23b08c1143bf80"
auth_header = {'X-api-username': amara_username, 'X-api-key': amara_api_key}

#Must configure AWS CLI first https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
#requires ffmpeg https://ffmpeg.zeranoe.com/builds/   add to path ffmpeg exes need to be next to youtubedl.exe

s3 = boto3.resource('s3')
transcribe = boto3.client('transcribe')
current_dir = os.getcwd()


video = "https://www.dailymotion.com/video/x7oq0ea"

extension = '\\video_temp\\%(title)s.%(ext)s'


ydl_opts = {'outtmpl': current_dir + extension,
            'forcefilename': True,
          }


with youtube_dl.YoutubeDL(ydl_opts) as ydl:

    ydl.download([video])
    info = ydl.extract_info(video, download=False)


extension = os.getcwd() + '\\video_temp\\{}.{}'.format(info['title'], 'mp4')


print("Uploading")

aws_title = info['title'].replace(" ","-")

s3.meta.client.upload_file(extension, 'amp-video-storage', aws_title + ".mp4")

objects = s3.meta.client.list_objects_v2(
    Bucket='amp-video-storage')

print("Starting Transcription Job")

response = transcribe.start_transcription_job(

    TranscriptionJobName=aws_title,
    LanguageCode='en-US',
    MediaFormat='mp4',
    Media={
        'MediaFileUri': 'https://s3.us-west-2.amazonaws.com/amp-video-storage/{}.mp4'.format(aws_title)
    },
    Settings={
        'ShowSpeakerLabels': False,
        'ChannelIdentification': False,
        'ShowAlternatives': False,
    }

)


job_name = response['TranscriptionJob']['TranscriptionJobName']

complete = False

while not complete:

    time.sleep(10)
    progress = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    print(progress['TranscriptionJob']['TranscriptionJobStatus'])

    if progress['TranscriptionJob']['TranscriptionJobStatus'] == "COMPLETED":
        complete = True


print("Finished Transcription")

transcription = transcribe.get_transcription_job(TranscriptionJobName=job_name)

transcript = requests.get(transcription['TranscriptionJob']['Transcript']['TranscriptFileUri'])
data = json.loads(transcript.content)


print(data)

## fix srt name
srt.writeTranscriptToSRT(data, "en-us", "{}.srt".format(aws_title))


post_data = {

    "video_url": video,
    "title": info['title'],
    "description": "Automator Test Job",
    "primary_audio_language_code": "en-US"
}



post_video = requests.post("https://amara.org/api/videos/", headers=auth_header, data=post_data)
amara_video_info = json.loads(post_video.content)
amara_video_id = amara_video_info['id']

print(post_video.content)


with open("{}.srt".format(aws_title), 'r') as srt:
    srt_string = srt.read()


sub_post_data = {
    "subtitles": srt_string,
    "sub_format": "srt",
    "title": aws_title,
    "is_complete": False
}



post_subtitles = requests.post("https://amara.org/api/videos/{}/languages/en-US/subtitles/".format(amara_video_id),
                               headers=auth_header,
                               data=sub_post_data)




print(post_subtitles.content)

print("Auto Captioning Finished. Go to: https://amara.org/en/videos/{}/info/{}/".format(amara_video_id, aws_title))




