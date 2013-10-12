# coding: utf-8
from ProcessCourseInfo import Course
a = Course(212323, "数学")
print(a)
a["timeString"] = "周二 第5-7节 逸A-117&nbsp;4-17周"
a.parseTime()
print(a)

