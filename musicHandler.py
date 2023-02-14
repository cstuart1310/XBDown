import os
import csv
from pytube import YouTube
from pytube import Playlist 
import urllib
import time
import subprocess

headerRows=1 #no of header/title rows to skip

#Filetype, incl audio, incl video
fileTypes={
    "mp3":"A",
    "mp4":"AV"
}

def readFiles():
    with open('downloads.csv', 'r') as file:
        reader = csv.reader(file,delimiter=",")
        rowCount=1
        for row in reader:
            if rowCount>headerRows:#only begins after skipping headers
                downloadRow(row)
            rowCount=rowCount+1

def downloadRow(row):
    
    name=row[0]
    fileType=row[1]
    outputDir=row[2]
    playlist=Playlist(str(row[3]))

    
    fileTypeInfo=getFileTypeInfo(fileType)

    print("Name:",row[0])
    print("fileType:",row[1])
    print("outputDir:",row[2])
    print("Playlist:",row[3])


    print("\nDownloading Playlist",name)
    if ("https://") in row[3]:#Makes sure url is a url
        playlistVideos=playlist.videos
        print("Playlist contains",len(playlistVideos),"videos")
        for video in playlistVideos:
            vidTitle=getTitle(video)
            print(vidTitle)
            if "A" in fileTypeInfo:
                getHighestAudio(video)
            if "V" in fileTypeInfo:
                getHighestVideo(video)
            convertToFileType(vidTitle,fileType)
        print("_"*20)
    else:
        print ("Error, url is either not a url or isn't pytube-able")

def getHighestAudio(video):#Downloads the highest quality audio available
    print("Downloading Audio")
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_audio_only().download()
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error, sleeping")
                time.sleep(30)

def getHighestVideo(video):#Downloads the highest quality video available
    print("Downloading Video")
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_highest_resolution().download()
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error, sleeping")
                time.sleep(30)

def getTitle(video):
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            vidTitle=str(video.title)
            downloadSuccessful=True                        
            return vidTitle
        except Exception as e:
            print("Error, sleeping")
            print(e)
            time.sleep(30)

def convertToFileType(vidTitle,fileType):
    if fileType=="mp4":
        print("File is already mp4, skipping ffmpeg")
    else:
        print("Converting to",fileType)
        outputName=vidTitle+"."+fileType
        subprocess.run(['ffmpeg','-i',(vidTitle+".mp4"),outputName])#,shell=True,capture_output=True)

def getFileTypeInfo(fileType):
    fileTypeChannels=(fileTypes[fileType])
    return fileTypeChannels


def expBackOff():
    multiplier=1
    delay=10
    print("Delaying for ",delay*multiplier,"seconds")
readFiles()