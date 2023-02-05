import os
import csv
from pytube import YouTube
from pytube import Playlist 

def readFiles():
    root=os.path.dirname(os.path.abspath(__file__))+"\\"
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
    url=row[3]

    print("Name:",name)
    print("fileType:",fileType)
    print("outputDir:",outputDir)
    print("URL:",url)
    print("_"*20)

    



readFiles()