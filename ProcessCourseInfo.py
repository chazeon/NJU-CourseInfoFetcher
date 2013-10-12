# coding: utf-8
"""
This program grab course information from a series of HTML files which were pre-downloaded from NJU Jiaowu Online System.

The HTML files must be named followed this rule:
    studentFromId_studentFrom.html
for example, an type of student id-ed after 011, named after 汉语言文学, their course file would be named as:
    011_汉语言文学.html

That would be our first step.
"""

# TODO: support course from other grades.

import os
import sys
import re
from UserDict import UserDict

classPerday = 12
#_STATUSLINE = ""
dWeekdays = {
        "周一" : (0 * classPerday),
        "周二" : (1 * classPerday),
        "周三" : (2 * classPerday),
        "周四" : (3 * classPerday),
        "周五" : (4 * classPerday),
        "周六" : (5 * classPerday),
        "周日" : (6 * classPerday)
        }

lWeekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

liCourse = []

def len_zh(data):
    """UTF-8 Chinese Wordcount Support"""
    temp = re.findall('[^a-zA-Z0-9.() \-ⅠⅡ]+', data)
    temp2 = re.findall('[ⅠⅡ]+', data)
    count = 0
    #print("@TEST(temp1,2): " + str(temp) + str(temp2))
    for i in temp:
        count += len(i) / 3
        #print("@TEST: " + str(count) + "'%s'" % i)
    for m in temp2:
        count += (len(m) / 3 * 2)
        #print("@TEST: " + str(count) + "'%s'" % m)
    #return 0
    return(count)

class Course(UserDict):
    def __init__(self, identi, name):
        UserDict.__init__(self)
        self["identi"] = identi
        self["name"] = name
        self["category"] = ""
        self["teacherFrom"] = ""
        self["credit"] = 0
        self["length"] = 0
        self["place"] = ""
        self["teacher"] = ""
        self["timeString"] = ""
        self["studentFrom"] = ""
        self["grade"] = 0
        self["exactTime"] = long(0)
        self["shortTime"] = ""
        self["classroom"] = []
        self["shortTimeAndClassroom"] = ""
        self["clearTimeString"] = ""

    def parseTime(self):
        if self["timeString"] == "":
            return
        #print("@TEST: " + self["timeString"])
        liTimeStringT = re.search(
                "^([^</>]*)(<br */?>)?([^</>]*)?(<br */?>)?([^</>]*)?(<br */?>)?([^</>]*)?(<br */?>)?([^</>]*)?(<br */?>)?([^</>]*)?(<br */?>)?([^</>]*)?$",
                self["timeString"]).groups()
        liTimeString = list(liTimeStringT)

        #print("//".join([str(m) for m in liTimeString]))

        while "<br>" in liTimeString: liTimeString.remove("<br>")
        while "<br/>" in liTimeString: liTimeString.remove("<br/>")
        while "<br />" in liTimeString: liTimeString.remove("<br />")
        while None in liTimeString: liTimeString.remove(None)
        while '' in liTimeString: liTimeString.remove('')
        
        #print("//".join(liTimeString))

        for s in liTimeString:
            #print("@TEST: " + s)
            splitATime = re.search("^(.+[^;])\ (.+[^;])\ (.+)&nbsp;(.+)?$", s).groups()
            #self["shortTimeAndClassroom"] += "%s %s %s" % (splitATime[0], splitATime[1], splitATime[2])
            #print(splitATime)
            try:
                startAndEnd = re.search("^第(\d+)-(\d+)节$", splitATime[1].rstrip()).groups()
            except AttributeError:
                print("\033[93m[ERROR]\033[0m %s  %s %s %s - ERROR WHEN PARSING TIME" % (self["name"], self["grade"], self["studentFrom"], " ".join(splitATime)))
                return
            start = int(startAndEnd[0]) + dWeekdays[splitATime[0]]
            end = int(startAndEnd[1]) + dWeekdays[splitATime[0]]

            if start == 1 or (self["exactTime"] >> (start - 2)) % 2 == 0:
                self["shortTime"] += "%s %s " % (splitATime[0], splitATime[1])
            else:
                #print("@TEST: %s" % (self["shortTime"]))
                searchRes = re.search(r"^(.+)\d+节 $", self["shortTime"]).groups()
                #print("@TEST : " + str(startAndEnd))
                #print("@TEST : " + str(searchRes))
                self["shortTime"] = searchRes[0] + "%s节 " % startAndEnd[1]


            #print("%d, %d" % (start, end))
            #try: (self["exactTime"] >> (start - 2)) % 2 == 0
            #except ValueError: print(start)
            for i in range(end - start + 1):
                self["exactTime"] += (1 << (start + i - 1))
                #print("@TEST: " + 'len(self["classroom"])' + str(len(self["classroom"])))
                if start == 1:
                    self["classroom"].append((splitATime[2], splitATime[3]))
                elif ((self["exactTime"] >> (start + i - 2)) % 2 == 0):
                    #print("@TEST: " + str(bin((self["exactTime"] >> (start + i - 1)))))
                    #print("%s,%s" % (self["studentFrom"], self["name"]))
                    self["classroom"].append((splitATime[2], splitATime[3]))
                else:
                    pass
                # if (self["exactTime"] >> (start - 2) % 2 == 0):
                    #print("%s,%s" % (self["studentFrom"], self["name"]))
                #self["classroom"].append((splitATime[2], splitATime[3]))
                #if self["identi"] == "13000030TA":
                    #print("%s %s" % (splitATime[2], splitATime[3]))
                    #TODO: Add classroom information
        #self.fromExactTimeGetShortTime()
        self["clearTimeString"] = self["timeString"].replace("&nbsp;", " ")
        self["clearTimeString"] = self["clearTimeString"].replace("<br>", "\n        ")
        self["clearTimeString"] = self["clearTimeString"].replace("<br/>", "\n        ")
        self["clearTimeString"] = self["clearTimeString"].replace("<br />", "\n        ")
        self["clearTimeString"] = "        " + self["clearTimeString"]


    def fromExactTimeGetShortTime(self):
        flag = 0
        tmpCounter = -1
        exactTime = self["exactTime"]
        shortTime = ""
        while exactTime != 0:
            tmpCounter += 1
            if exactTime % 2 == 0:
                if flag != 0:
                    shortTime += toWeek(flag, tmpCounter - 1)
                    flag = 0
            else:
                if flag == 0: flag = tmpCounter
            exactTime >> 1
        self["shortTime"] = shortTime

    def toWeek(start, end):
        i = 0
        s = ""
        for i in range(7):
            if start / classPerDay == 0:
                s += lWeekdays
                s += " 第%d节-第%d节" % (start + 1, end + 1)
            else:
                start -= classPerDay
                end -= classPerDay


def readClassFileOfYear(workingDirectory, year = 2013):
    global liCourse
    preCounter = len(liCourse)
    try:
        classAndClassIdList = [k for (k,v) in 
                [os.path.splitext(f) for f in 
                    os.listdir(os.path.join(workingDirectory, str(year)))]]
    except OSError:
        print("No files of grade %d of list have been found. - [FAIL]" % year)
        return "ERROR"
        

    #classList = [(v[:v.find("_")],v[(v.find("_") + 1):]) for v in classAndClassIdList]      # TODO
    classList = []
    for v in classAndClassIdList:
        classList = classList + re.findall(r"(\S+)_(\S+)_(\S+)_(\S+)", v)
    #print(classList)
    #print(classAndClassIdList)
    for (k, l, m, n) in classList:
        fsock = open(os.path.join(workingDirectory, str(year), "%s_%s_%s_%s.html" % (k, l, m, n)), "r")
        tmps = fsock.read()
        fsock.close()
        #print(n)
        getCourseInfo(tmps, l + ":" + n, year)                                                       # TODO
    #print("hi")
    #printInformation()
    print("\033[92m[SUCCESS]\033[0m NJU grade %d course information loaded(%d)" % (year, len(liCourse) - preCounter))

def readClassFile(workingDirectory = "files", grade = 0b0001, stdGrade = 2013):
    global liCourse
    liCourse = []
    for plusGrade in range(10):
        if (grade >> (plusGrade)) % 2 == 1:
            readClassFileOfYear(workingDirectory, stdGrade - plusGrade)

        
def getCourseInfo(text, studentFrom, grade):
    """
Use a fucking long Regular Expression to find information of class.

    Return a list of tuples.
    Every tuples are a group of matched result.
    """
    global liCourse
    #liCourse = []
    pattern = """
        <tr\ .*\s*.*\s*>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\d{8,8}\D{0,3})				# course number
        </td>
        \s*
        <td\ valign=\"middle\">
        (\D+)						# course name
        </td>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\D+)						# category
        </td>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\D+)						# teacher from
        </td>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\d+.\d)					# credit
        </td>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\d+)						# period
        </td>
        \s*
        <td\ align=\"center\"\ valign=\"middle\">
        (\D+)						# where
        </td>
        \s*
        <td\ valign=\"middle\">
        (.*)						# the teacher
        </td>
        \s*
        <td\ valign=\"middle\">
        (.*)						# time and place
        </td>
        \s*
        </tr>
        """
    searchResult = re.findall(pattern, text, re.VERBOSE)
    #print(searchResult)
    if searchResult == None:
        return
    #print(searchResult)
    for oneCourseOfResult in searchResult:
        tmpCourse = Course(oneCourseOfResult[0], oneCourseOfResult[1])
        tmpCourse["category"]       = oneCourseOfResult[2]
        tmpCourse["teacherFrom"]    = oneCourseOfResult[3]
        tmpCourse["credit"]         = float(oneCourseOfResult[4])
        tmpCourse["length"]         = int(oneCourseOfResult[5])
        tmpCourse["place"]          = oneCourseOfResult[6]
        tmpCourse["teacher"]        = oneCourseOfResult[7]
        tmpCourse["timeString"]     = oneCourseOfResult[8]
        tmpCourse["studentFrom"]    = studentFrom
        tmpCourse["grade"]          = grade
        tmpCourse.parseTime()
        #print(tmpCourse["name"])
        liCourse.append(tmpCourse)
    # TODO: deal with time.

def printInformation():
    for aCourse in liCourse:
        print("%s %s %s " % (aCourse["name"].ljust(35 + len_zh(aCourse["name"])), aCourse["exactTime"], aCourse["studentFrom"]))
        #print("\n")
        pass

def findByName(RegExPattern, longForm = 0):
    for aCourse in liCourse:
        #print(aCourse["name"])
        if re.search(RegExPattern, aCourse["name"]) != None:
            print("%s%s%s届%s " % (aCourse["name"].ljust(35 + len_zh(aCourse["name"]), "."), aCourse["shortTime"].ljust(35 + len_zh(aCourse["shortTime"]), "."), aCourse["grade"], aCourse["studentFrom"]))
            if longForm == 1:
                #classroomString = " ".join(["%s %s " % (a, b) for (a, b) in aCourse["classroom"]])
                #print(len(aCourse["classroom"]), aCourse["classroom"])
                classroomString = " ".join(["%s " % a.rjust(12 + len_zh(a), ".") for (a, b) in aCourse["classroom"]])
                print("".ljust(35, " ") + classroomString.ljust(35 + len_zh(classroomString), ' ') + aCourse["teacher"].ljust(40 + len_zh(aCourse["teacher"])))
                print("")
            if longForm == 2: print(aCourse["clearTimeString"])
    print("")

def findByTime(weekOfDay, startClass, endClass, longForm = 0):
    startTime = (weekOfDay - 1) * 12 + startClass
    endTime = (weekOfDay - 1) * 12 + endClass
    for aCourse in liCourse:
        flag = 0
        for t in range(endTime - startTime + 1):
            if ((aCourse["exactTime"] >> (startTime + t - 1)) % 2) == 1:
                print("%s%s%s届%s " % (aCourse["name"].ljust(35 + len_zh(aCourse["name"]), '.'), aCourse["shortTime"].ljust(35 + len_zh(aCourse["shortTimeAndClassroom"]), '.'), aCourse["grade"], aCourse["studentFrom"]))
                if longForm == 1:
                    #classroomString = " ".join(["%s %s " % (a, b) for (a, b) in aCourse["classroom"]])
                    #print(len(aCourse["classroom"]), aCourse["classroom"])
                    classroomString = " ".join(["%s " % a.rjust(12 + len_zh(a), ".") for (a, b) in aCourse["classroom"]])
                    print("".ljust(35, " ") + classroomString.ljust(35 + len_zh(classroomString), ' ') + aCourse["teacher"].ljust(40 + len_zh(aCourse["teacher"])))
                    print("")

                if longForm == 2: print(aCourse["clearTimeString"])

                flag = 1
                break
        if flag == 1:
            continue
    print("")

def findByNameAndTime(RegExPattern, weekOfDay, startClass, endClass, longForm = 0):
    for aCourse in liCourse:
        if re.search(RegExPattern, aCourse["name"]) != None:
            startTime = (weekOfDay - 1) * 12 + startClass
            endTime = (weekOfDay - 1) * 12 + endClass
            for t in range(endTime - startTime + 1):
                if ((aCourse["exactTime"] >> (startTime + t - 1)) % 2) == 1:
                    #print((aCourse["exactTime"] >> (startTime + t - 1)) % 2)
                    #print("%s \t%s \t%s \t%s" % (aCourse["name"].ljust(35), aCourse["timeString"], aCourse["studentFrom"], str(aCourse["exactTime"])))
                    print("%s%s届%s" % (aCourse["name"].ljust(70 + len_zh(aCourse["name"]), '.'), aCourse["grade"], aCourse["studentFrom"]))
                    if longForm == 2: print(aCourse["clearTimeString"])

                    if longForm == 1:
                        #classroomString = " ".join(["%s %s " % (a, b) for (a, b) in aCourse["classroom"]])
                        #print(len(aCourse["classroom"]), aCourse["classroom"])
                        classroomString = " ".join(["%s " % a.rjust(12 + len_zh(a), ".") for (a, b) in aCourse["classroom"]])
                        print("".ljust(35, " ") + classroomString.ljust(35 + len_zh(classroomString), ' ') + aCourse["teacher"].ljust(40 + len_zh(aCourse["teacher"])))
                        print("")


                    break
    print("")

def findByTeacher(RegExPattern, longForm = 0):
    for aCourse in liCourse:
        if re.search(RegExPattern, aCourse["teacher"]) != None:
            print("%s%s%s%s届%s" % (aCourse["name"].ljust(35 + len_zh(aCourse["name"]), '.'), aCourse["shortTime"].ljust(40 + len_zh(aCourse["shortTime"]), '.'), aCourse["teacher"].ljust(15 + len_zh(aCourse["teacher"]), '.'), aCourse["grade"], aCourse["studentFrom"]))
            if longForm == 1:
                #classroomString = " ".join(["%s %s " % (a, b) for (a, b) in aCourse["classroom"]])
                #print(len(aCourse["classroom"]), aCourse["classroom"])
                classroomString = " ".join(["%s " % a.rjust(12 + len_zh(a), ".") for (a, b) in aCourse["classroom"]])
                print("".ljust(35, " ") + classroomString.ljust(35 + len_zh(classroomString), ' ') + aCourse["teacher"].ljust(40 + len_zh(aCourse["teacher"])))
                print("")
            if longForm == 2: print(aCourse["clearTimeString"])
    print("")



def LOAD(workingDirectory):
    readClassFile()



if __name__ == "__main__":
    #readClassFile("files", 0b0001, 2013)
    #findByName("数学")
    #findByName("数学", 1)
    #LOAD("files")
    #findByName("物理", 1)
    findByNameAndTime("大学计算机", 3, 7, 8, 0)
    findByNameAndTime("大学计算机", 3, 7, 8, 2)

