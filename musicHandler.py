import os
import csv
from pytube import YouTube
from pytube import Playlist 
import urllib
import time
import subprocess
import shutil

headerRows=1 #no of header/title rows to skip
vidDelay=3#No of seconds to wait between each title lookup (Used to stop throttling)
retries=3

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
    category=row[5]
    videoCounterOffset=int(row[6])

    fileTypeInfo=getFileTypeInfo(fileType)

    print("Name:",row[0])#Name of playlist
    print("fileType:",row[1])#File type to convert to (Impacts which streams are downloaded)
    print("outputDir:",row[2])#Dir to move files to when processing finished
    print("Playlist:",row[3])#URL of playlist
    print("LogFile",row[4])#File of videos already downloaded
    print("Category:",row[5])#Type of video (Music, tv), used for naming things
    print("VideoCounterOffset:",row[6])#Offset val used to skip vids before a series starts



    print("\nDownloading Playlist",name)
    if ("https://") in row[3]:#Makes sure url is a url
        playlistVideos=playlist.videos
        print("Playlist contains",len(playlistVideos),"videos")

        videoCounter=0#Resets counter
        for video in list(playlistVideos)[videoCounterOffset:]:#Loops through all videos after offset val
            videoCounter=videoCounter+1#increments
            time.sleep(vidDelay)
            print("\n"*3)
            vidTitle=getTitle(video)#gets title of vid
            
            if vidTitle==False:
                print("Error getting video title, skipping for now")
                print("Errored video:",video)
            elif vidTitle != False:#If no errors from getting video title
                print("\n",vidTitle)
                if checkDownloaded(vidTitle,logFilePath)==False:#If video hasn't been downloaded already
                    if category=="TVSeries":#Custom naming for tv series's
                        print("TV Series naming")
                        outputName="S01E"+(str(videoCounter).zfill(3))#Renames in format s01e001 s01e002 etc (One season per playlist)
                    else:
                        print("Standard naming")
                        outputName=vidTitle

                    if "A" in fileTypeInfo:
                        getHighestAudio(video,vidTitle,outputName)
                    if "V" in fileTypeInfo:
                        getHighestVideo(video,vidTitle,outputName)


                    convertToFileType(vidTitle,fileType,outputName)
                    moveToDest(outputName+"."+fileType,outputDir)
                    appendDownloaded(vidTitle,logFilePath)
                elif checkDownloaded==True:#If already downloaded
                    print("Already downloaded")
        print("_"*20)
    else:
        print ("Error, url is either not a url or isn't pytube-able")

def getHighestAudio(video,vidTitle,outputName):#Downloads the highest quality audio available
    print("Downloading Audio")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_audio_only().download(filename=(outputName+".mp4"))
            downloadSuccessful=True                        
        except urllib.error.HTTPError:#If url isn't pytube compatible
                print("Error, sleeping")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getHighestVideo(video,vidTitle,outputName):#Downloads the highest quality video available
    print("Downloading Video")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_highest_resolution().download(filename=(outputName+".mp4"))
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
        subprocess.run(['ffmpeg','-i',(vidTitle+".mp4"),(outputName+"."+fileType)])
        os.remove((vidTitle+".mp4"))#Removes the old file

def moveToDest(outputName,outputDir):
    moved=False
    moveRetryCounter=-1
    while moved==False and moveRetryCounter>retries:
        moveRetryCounter+=1
        try:
            print("Moving to",outputDir)
            shutil.move(outputName,outputDir)
            moved=True
        except shutil.Error:
            print("Error moving, file stuck in download dir")
        except FileNotFoundError:
            print("Output dir does not exist, creating it now")
            os.makedirs(outputDir)

def getFileTypeInfo(fileType):
    fileTypeChannels=(fileTypes[fileType])
    return fileTypeChannels

def checkDownloaded(vidTitle,logFilePath):
    try:
        logLines=open(logFilePath).read().splitlines()
        if vidTitle in logLines:
            return True
        else:
            return False
    except FileNotFoundError:
        print("Can't find log file, creating a new one")
        open(logFilePath,"w").close()#Creates the log file

def removeIllegalChars(vidTitle):
    invalid = ["<",">",":",'"',"/","|","?","*","&","'"]
    for character in invalid:
        vidTitle=vidTitle.replace(character,"")
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
