import os
import csv
from pytube import YouTube
from pytube import Playlist 

def readFiles():
    with open('downloads.csv', 'r') as file:
        reader = csv.reader(file,delimiter=",")
        rowCount=0
        for row in reader:
            rowCount=rowCount+1
            downloadRow(row)

def downloadRow(row):
    try:
        name=row[0]
        fileType=row[1]
        outputDir=row[2]
        playlist=Playlist(str(row[3]))

        print("Name:",row[0])
        print("fileType:",row[1])
        print("outputDir:",row[2])
        print("Playlist:",row[3])

        print("\nDownloading Playlist")

        for video in playlist.videos:
            print("1")
            video.streams.first().download()
    except:
        print("shit")
    print("_"*20)


readFiles()