import os
import csv

root=os.path.dirname(os.path.abspath(__file__))+"\\"
# with open((root+"downloads.csv"),"r") as downloadsFile:
#     reader=csv.reader(downloadsFile)

#     for row in reader:
#         print(row)

with open('downloads.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)