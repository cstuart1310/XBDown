import os
import csv
from pytube import YouTube
from pytube import Playlist 
import urllib
import time
import subprocess
import shutil

headerRows=1 #no of header/title rows to skip

retries=5

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
            
            if vidTitle==False:
                print("Error getting video title, skipping for now")
                print("Errored video:",video)
            elif vidTitle != False:#If no errors from getting video title
                print("\n",vidTitle)
                if checkDownloaded(vidTitle,logFilePath)==False:#If video hasn't been downloaded already
                    if "A" in fileTypeInfo:
                        getHighestAudio(video,vidTitle)
                    if "V" in fileTypeInfo:
                        getHighestVideo(video,vidTitle)
                
                    outputName=vidTitle+"."+fileType
                    convertToFileType(vidTitle,fileType,outputName)
                    moveToDest(outputName,outputDir)
                    appendDownloaded(vidTitle,logFilePath)
                else:#If already downloaded
                    print("Already downloaded")
        print("_"*20)
    else:
        print ("Error, url is either not a url or isn't pytube-able")

def getHighestAudio(video,vidTitle):#Downloads the highest quality audio available
    print("Downloading Audio")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_audio_only().download(filename=(vidTitle+".mp4"))
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error, sleeping")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getHighestVideo(video,vidTitle):#Downloads the highest quality video available
    print("Downloading Video")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_highest_resolution().download(filename=(vidTitle+".mp4"))
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error")
                expBackOff(retryMultiplier)
                retryMultiplier+=1
def getTitle(video):#Tries to get the video title. If it errors out x times because youtube have changed something, it just skips the video
    retryMultiplier=1
    downloadSuccessful=False

    while downloadSuccessful==False:
        try:
            if retryMultiplier>retries:
                return False
            vidTitle=str(video.title)
            vidTitle=removeIllegalChars(vidTitle)
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
        os.remove((vidTitle+".mp4"))#Removes the old file

def moveToDest(outputName,outputDir):
    print("Moving to",outputDir)
    shutil.move(outputName,outputDir)

def getFileTypeInfo(fileType):
    fileTypeChannels=(fileTypes[fileType])
    return fileTypeChannels

def checkDownloaded(vidTitle,logFilePath):
    logLines=open(logFilePath).read().splitlines()

        

    # logFile=open(logFilePath,"r")
    # logLines=logFile.readlines()
    # logLines=logLines.replace("\n","")#removes \n's from lines
    print(logLines)
    # logFile.close()
    if vidTitle in logLines:
        return True
    else:
        return False

def removeIllegalChars(vidTitle):
    invalid = ["<",">",":",'"',"/","|","?","*","&","'"]
    for character in invalid:
        vidTitle=vidTitle.replace(character,"")
    #vidTitle=vidTitle.decode('utf-8','ignore').encode("utf-8")#probably could commit to one method or the other but oh well
    return vidTitle


def appendDownloaded(vidTitle,logFilePath):
    logFile=open(logFilePath,"a")
    logFile.write(("\n"+vidTitle))
    logFile.close()

    

def expBackOff(retryMultiplier):
    delay=10
    print("Delaying for ",delay*retryMultiplier,"seconds")
    time.sleep(delay*retryMultiplier)
readFiles()