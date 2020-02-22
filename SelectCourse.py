#encoding=utf-8
# 成都理工大学自动化选课工具

import LoginFunction
import requests
import time

# 登录所需信息
StuNum = '201601010101'
StuPass = 'xxxxxxxxxxxxxxxxxx'

# 获取当前时间戳（登录函数需要用到）
TimeNow = int(round(time.time() * 1000))

# 浏览器标志头
CHROME_HEADERS = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'

# POST地址
# 登录页面的post地址
LOGIN_URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'

# 选课请求地址
SEL_URL = 'http://202.115.133.173:805/SelectCourse/SelectHandler.ashx'

# 登录请求头
LoginHeads = {
    'User-Agent':'%s' %CHROME_HEADERS,
    'Referer':'http://202.115.133.173:805/Login.html'
}

# POST字典
# 登录页面的post字段
LoginPostData = {
    'Action': 'Login',
    'userName': StuNum,
    'pwd': LoginFunction.getAaoPwd(StuNum, StuPass, str(TimeNow)),
    'sign': str(TimeNow)
}

# 登录获取cookies
AaoCookie = LoginFunction.GetCookie(LOGIN_URL, LoginPostData, LoginHeads)

print('登录成功')
print('你的账号:%s\n' %StuNum, '你的cookie:%s\n' %AaoCookie)
TaskType = input('请输入要查询的课程类别:\n01:计划课 02:选修课 03:补课 04:跨专业选课')
CourseId = LoginFunction.GetCourseList(SEL_URL, TaskType, AaoCookie)
print('正在查询课程详情...')
Value = LoginFunction.ViewCourse(SEL_URL,AaoCookie,CourseId,TaskType)
print('正在选课...')
LoginFunction.SelectCourse(SEL_URL, AaoCookie, Value['ClassId'], Value['SclassId'], CourseId, TaskType, Value['jclassId'] )
