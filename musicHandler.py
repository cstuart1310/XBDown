import os
import csv
from pytube import YouTube
from pytube import Playlist 
import urllib
import time
import subprocess
import shutil

headerRows=1 #no of header/title rows to skip

#Filetype, incl audio, incl video
fileTypes={
    "mp3":"A",
    "mp4":"V"
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
    logFilePath=str(row[4])+".txt"
    
    fileTypeInfo=getFileTypeInfo(fileType)

    print("Name:",row[0])
    print("fileType:",row[1])
    print("outputDir:",row[2])
    print("Playlist:",row[3])
    print("LogFile",row[4])



    print("\nDownloading Playlist",name)
    if ("https://") in row[3]:#Makes sure url is a url
        playlistVideos=playlist.videos
        print("Playlist contains",len(playlistVideos),"videos")
        for video in playlistVideos:
            vidTitle=getTitle(video)#gets title of vid
            print("\n",vidTitle)
            if checkDownloaded(vidTitle,logFilePath)==False:#If video hasn't been downloaded already
                if "A" in fileTypeInfo:
                    getHighestAudio(video)
                if "V" in fileTypeInfo:
                    getHighestVideo(video)
            
                outputName=vidTitle+"."+fileType
                convertToFileType(vidTitle,fileType,outputName)
                moveToDest(outputName,outputDir)
                appendDownloaded(vidTitle,logFilePath)
            else:#If already downloaded
                print("Already downloaded")
        print("_"*20)
    else:
        print ("Error, url is either not a url or isn't pytube-able")

def getHighestAudio(video):#Downloads the highest quality audio available
    print("Downloading Audio")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_audio_only().download()
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error, sleeping")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getHighestVideo(video):#Downloads the highest quality video available
    print("Downloading Video")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_highest_resolution().download()
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error")
                expBackOff(retryMultiplier)
                retryMultiplier+=1
def getTitle(video):
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            vidTitle=str(video.title)
            downloadSuccessful=True                        
            return vidTitle
        except Exception as e:
            print("Error")
            print(e)
            expBackOff(retryMultiplier)
            retryMultiplier+=1
def convertToFileType(vidTitle,fileType,outputName):
    if fileType=="mp4":
        print("File is already mp4, skipping ffmpeg")
    else:
        print("Converting to",fileType)
        subprocess.run(['ffmpeg','-i',(vidTitle+".mp4"),outputName])

def moveToDest(outputName,outputDir):
    print("Moving to",outputDir)
    shutil.move(outputName,outputDir)

def getFileTypeInfo(fileType):
    fileTypeChannels=(fileTypes[fileType])
    return fileTypeChannels

def checkDownloaded(vidTitle,logFilePath):
    logFile=open(logFilePath,"r")
    logLines=logFile.readlines()
    if vidTitle in logLines:
        return True
    else:
        return False


def appendDownloaded(vidTitle,logFilePath):
    logFile=open(logFilePath,"r+")
    logFile.write(("\n"+vidTitle))
    logFile.close()

def expBackOff(retryMultiplier):
    delay=10
    print("Delaying for ",delay*multiplier,"seconds")
    time.sleep(delay*multiplier)
readFiles()