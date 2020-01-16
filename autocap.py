#!python

from sys import argv
import cap_automate

if __name__ == "__main__":
    if argv[2] == "-c":
        print("Will auto caption ", argv[1])
        auto_caption = cap_automate.AutoCaption(argv[1])
        auto_caption.auto_caption()
    elif argv[2] == "-d":
        print("Only downloading video")
        auto_caption = cap_automate.AutoCaption(argv[1])
        auto_caption.download_video()

    elif argv[2] == "-u":
        print("Uploading to S3 bucket")
        auto_caption = cap_automate.AutoCaption(argv[1])
        auto_caption.download_video()

    else:
        print("Please provide flag: -c for auto caption, -d for download only. -u for upload without captions")


    print("Close the window")