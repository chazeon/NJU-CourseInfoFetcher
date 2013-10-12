import os
import re

liColApt = []       # an aptcol should be (nocol, col, noapt, apt)

def getCollegeInfo(url = "ColAptList"):
    collegeLog = open(url)
    anItem = "(null)"
    noapt = "(null)"
    apt = "(null)"
    nocol = "(null"
    col = "(null)"
    anItemString = collegeLog.readline()
    while anItemString != '':
        if anItemString[:4] == "    ":
            noapt = anItemString[4:-1].split("%")[0]
            apt =   anItemString[4:-1].split("%")[1]
            liColApt.append((nocol, col, noapt, apt))
        else:
            nocol = anItemString[:-1].split("_")[0]
            col =   anItemString[:-1].split("_")[1]
        anItemString = collegeLog.readline()
    collegeLog.close()

def downloadWebPages(url):
    downloadRes = re.match(r"(^[^\n]+curSpeciality=)\D*\d+(&curGrade=)\d{4,4}([^\n]+$)", url).groups()
    if downloadRes == None:
        print("Download Error!")
        return
    os.system("mkdir " + "files-tmp")
    for curGrade in range(2013, 2014):
        os.system("mkdir " + "files-tmp/" + str(curGrade))
        for anItem in liColApt:
            curSpecialty = anItem[2]
            #print(anItem)
            #print(downloadRes[0] + curSpecialty + downloadRes[1] +
            #        str(curGrade) + downloadRes[2] + " >> '" + "files-tmp/" +
            #        str(curGrade) + "/" + "_".join(anItem) + ".html'")
            os.system(downloadRes[0] + curSpecialty + downloadRes[1] +
                    str(curGrade) + downloadRes[2] + " >> '" + "files-tmp/" +
                    str(curGrade) + "/" + "_".join(anItem) + ".html'")
            while os.path.getsize("files-tmp/" + str(curGrade) + "/" + "_".join(anItem) + ".html") == 0:
                os.system(downloadRes[0] + curSpecialty + downloadRes[1] +
                        str(curGrade) + downloadRes[2] + " >> '" + "files-tmp/" +
                        str(curGrade) + "/" + "_".join(anItem) + ".html'")
                

getCollegeInfo()
