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
retries=10

#Filetype, incl audio, incl video
fileTypes={
    "mp3":"A",
    "mp4":"AV"
}

def readFiles():#reads info from csv to find playlist to download
    with open('downloads.csv', 'r') as file:
        reader = csv.reader(file,delimiter=",")
        rowCount=1
        for row in reader:
            if rowCount>headerRows:#only begins after skipping headers
                downloadRow(row)
            rowCount=rowCount+1

def downloadRow(row):
    #data from array from csv
    name=row[0]
    fileType=row[1]
    outputDir=row[2]
    playlist=Playlist(str(row[3]))
    logFilePath=str(row[4])+".txt"# eg xbdownLog.txt
    
    fileTypeInfo=getFileTypeInfo(fileType)#looks up dictionary to see if vid only, audio only, audio and video

    #console info
    print("Name:",row[0])
    print("fileType:",row[1])
    print("outputDir:",row[2])
    print("Playlist:",row[3])
    print("LogFile",row[4])


    #downloading
    print("\nDownloading Playlist",name)
    if ("https://") in row[3]:#Makes sure url is a url
        playlistVideos=playlist.videos#gets array from the object
        print("Playlist contains",len(playlistVideos),"videos")
        for video in playlistVideos.reverse():#each video ordered from newest to oldest
            time.sleep(vidDelay)#sleeps to prevent ban
            print("\n"*3)
            vidTitle=getTitle(video)#gets title of vid
            
            if vidTitle==None:
                print("Error getting video title, skipping for now")
                print("Errored video:",video)
            elif vidTitle != None:#If no errors from getting video title
                print("\n",vidTitle)
                if checkDownloaded(vidTitle,logFilePath)==False:#If video hasn't been downloaded already
                    if "A" in fileTypeInfo and "V" in fileTypeInfo: #if format wants audio and video
                        getHighestVideoAudio(video,vidTitle)
                    elif "A" in fileTypeInfo:
                        getHighestAudio(video,vidTitle)
                    elif "V" in fileTypeInfo:
                        getHighestVideoAudio(video,vidTitle)
                
                    outputName=vidTitle+"."+fileType
                    convertToFileType(vidTitle,fileType,fileTypeInfo,outputName)
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
        except (urllib.error.HTTPError, KeyError):#If url isn't pytube compatible
                print("Error, sleeping")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getHighestVideoAudio(video,vidTitle):#Downloads the highest quality video available (A&V)
    print("Downloading Video and Audio")
    retryMultiplier=1
    downloadSuccessful=False
    while downloadSuccessful==False:
        try:
            video.streams.get_highest_resolution().download(filename=(vidTitle+".mp4"))
            downloadSuccessful=True                        
        except (urllib.error.HTTPError, KeyError):#If url isn't pytube compatible
                print("Error")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getTitle(video):#Tries to get the video title. If it errors out x times because youtube have changed something, it just skips the video
    retryMultiplier=1
    titleDownloadSuccessful=False

    while titleDownloadSuccessful==False:
        try:
            if retryMultiplier>retries:#if past allowed no of reattempts with no title
                return None
            
            vidTitle=str(video.title)#gets title from url
            vidTitle=removeIllegalChars(vidTitle)#removes emojis etc
            titleDownloadSuccessful=True
            return vidTitle
        except Exception as e:#If error getting title
            print("Error")
            print(e)
            expBackOff(retryMultiplier)
            retryMultiplier+=1

def convertToFileType(vidTitle,fileType,fileTypeInfo,outputName):
    if fileType=="mp4" and "AV" in fileTypeInfo:#videos download as an mp4 from youtube and don't need any more converting
        print("File is already mp4, skipping ffmpeg")
    else:
        print("Converting to",fileType)
        subprocess.run(['ffmpeg','-i',(vidTitle+".mp4"),outputName])#converts to desired formt
        os.remove((vidTitle+".mp4"))#Removes the old file

def moveToDest(outputName,outputDir):
    try:
        print("Moving to",outputDir)
        shutil.move(outputName,outputDir)
    except shutil.Error:
        print("Error moving, file stuck in",outputName)

def getFileTypeInfo(fileType):#Returns Channels (Audio/Video) wanted by the filetype from the dic
    fileTypeChannels=(fileTypes[fileType])#looks up the filetype (eg mp4) in dictionary for key (AV)
    return fileTypeChannels

def checkDownloaded(vidTitle,logFilePath):
    logLines=open(logFilePath).read().splitlines()
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


#Main
readFiles()
