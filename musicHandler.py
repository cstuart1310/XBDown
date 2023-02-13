import os
import csv
from pytube import YouTube
from pytube import Playlist 
import urllib
import time

def readFiles():
    with open('downloads.csv', 'r') as file:
        reader = csv.reader(file,delimiter=",")
        rowCount=0
        for row in reader:
            rowCount=rowCount+1
            downloadRow(row)

def downloadRow(row):
    
    name=row[0]
    fileType=row[1]
    outputDir=row[2]
    playlist=Playlist(str(row[3]))

    print("Name:",row[0])
    print("fileType:",row[1])
    print("outputDir:",row[2])
    print("Playlist:",row[3])

    print("\nDownloading Playlist")
    if ("https://") in row[3]:
        try:
            for video in playlist.videos:
                if fileType=="mp3":
                    video.streams.get_audio_only().download()
                #video.streams.first().download()
        except urllib.error.HTTPError:
            print("Error, sleeping")
            time.sleep(30)
        print("_"*20)

def expBackOff():
    multiplier=1
    delay=10
    print("Delaying for ",delay*multiplier,"seconds")
readFiles()