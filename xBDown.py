import os
import csv
from pytube import YouTube, Playlist
from pytube.exceptions import AgeRestrictedError
import urllib
import time
import subprocess
import shutil
import argparse

headerRows=1 #no of header/title rows to skip
vidDelay=1#No of seconds to wait between each title lookup (Used to stop throttling)
maxRetries=3

#Filetype, incl audio, incl video
fileTypes={
    "mp3":"A",
    "mp4":"AV"
}


def readFiles(downloadsFile):#reads info from csv to find playlist to download
    print("Reading",downloadsFile)
    with open(downloadsFile, 'r') as file:
        reader = csv.reader(file,delimiter=",")
        rowCount=1
        for row in reader:
            if rowCount>headerRows:#only begins after skipping headers
                downloadRow(row)
            rowCount=rowCount+1

def downloadRow(row):
    #data from array from csv
    playlistName=row[0]
    fileType=row[1]
    outputDir=row[2]
    playlist=Playlist(str(row[3]))
    logFilePath=str(row[4])+".txt"# eg xbdownLog.txt
    
    fileTypeInfo=getFileTypeInfo(fileType)#looks up dictionary to see if vid only, audio only, audio and video

    #console info
    print("Name:",playlistName)
    print("fileType:",fileType)
    print("outputDir:",outputDir)
    print("LogFile",logFilePath)

    if os.path.exists(logFilePath)==False:#If text file does not exist
        print("Creating log file")
        open(logFilePath,"a").close()#creates the file

    #downloading
    print("-"*20,"\nDownloading Playlist",playlistName)
    if ("https://") in row[3]:#Makes sure url is a url
        playlistVideos=list(playlist.videos)
        playlistVideos.reverse()
        print("Playlist contains", len(playlistVideos), "videos")

        for video in playlistVideos:
            time.sleep(vidDelay)  # sleeps to prevent ban
            vidTitle = getTitle(video)  # gets title of vid

            if vidTitle==None:
                print("Error getting video title, skipping for now")
                print("Errored video:",video)
            elif vidTitle != None:#If no errors from getting video title
                print("\n",vidTitle)
                if checkDownloaded(vidTitle,logFilePath)==False:#If video hasn't been downloaded already
                    
                    if "A" in fileTypeInfo and "V" in fileTypeInfo: #if format wants audio and video
                        downloadSuccessful=getHighestVideoAudio(video,vidTitle)
                    elif "A" in fileTypeInfo:
                        downloadSuccessful=getHighestAudio(video,vidTitle)
                    elif "V" in fileTypeInfo:
                        downloadSuccessful=getHighestVideoAudio(video,vidTitle)

                    if downloadSuccessful==True:
                        outputName=vidTitle+"."+fileType
                        convertToFileType(vidTitle,fileType,fileTypeInfo,outputName)
                        moveToDest(outputName,outputDir,vidTitle,fileType,playlistName)
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

    if retryMultiplier>=maxRetries:
        return False
    
    while downloadSuccessful==False and retryMultiplier<maxRetries:
        try:
            video.streams.get_audio_only().download(filename=(vidTitle+".mp4"))
            downloadSuccessful=True
            return downloadSuccessful
        except Exception as e:#If an error was raised
                print("Error, sleeping")
                print(e)
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getHighestVideoAudio(video,vidTitle):#Downloads the highest quality video available (A&V)
    print("Downloading Video and Audio")
    retryMultiplier=1
    downloadSuccessful=False

    if retryMultiplier>=maxRetries:
        return False

    while downloadSuccessful==False and retryMultiplier<maxRetries:
        try:
            video.streams.get_highest_resolution().download(filename=(vidTitle+".mp4"))
            downloadSuccessful=True                        
            return downloadSuccessful
        except (urllib.error.HTTPError, KeyError):#If url isn't pytube compatible
                print("Error")
                expBackOff(retryMultiplier)
                retryMultiplier+=1

def getTitle(video):#Tries to get the video title. If it errors out x times because youtube have changed something, it just skips the video
    retryMultiplier=1
    titleDownloadSuccessful=False

    while titleDownloadSuccessful==False:
        try:
            if retryMultiplier>maxRetries:#if past allowed no of reattempts with no title
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
        subprocess.run(['ffmpeg','-i',(vidTitle+".mp4"),outputName,"-y","-stats","-v","quiet"])#converts to desired formt
        os.remove((vidTitle+".mp4"))#Removes the old file

def moveToDest(outputName,outputDir,vidTitle,fileType,playlistName):
    
    #find and replaces outputdir to correct
    dirReplacables=[
    ["$title",vidTitle],
    ["$format",fileType],
    ["$workDir",(os.getcwd())],
    ["$playlist",playlistName]
    ]#values to replace

    for dirReplacable in dirReplacables:#Loops through each of the 2d array vals
        outputDir=outputDir.replace(dirReplacable[0],dirReplacable[1])#eg replaces $title with Brandy


    try:
        print("Moving to",outputDir)
        shutil.move(outputName,outputDir)
    except FileNotFoundError:#if the dir/subdirs aren't found
        os.makedirs(outputDir)
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
    with open(logFilePath,"a") as logFile:
        logFile.write(("\n"+vidTitle))
        
    

def expBackOff(retryMultiplier):
    delay=10
    print("Delaying for ",delay*retryMultiplier,"seconds")
    time.sleep(delay*retryMultiplier)


#Main

parser = argparse.ArgumentParser()
parser.add_argument("-downloads","-d",default="downloads.csv")
args = parser.parse_args()
downloadsFile=args.downloads

try:
    readFiles(downloadsFile)
except FileNotFoundError as e:
    print(e)
