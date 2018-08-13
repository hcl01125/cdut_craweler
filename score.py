#encoding=utf-8
# 该文件为获取教务处成绩单的模块
# TODO: 1. 从学籍表中查询账号密码，登录教务处
# TODO: 2. 查询成绩、班级等各项信息，并解析保存
# TODO: 3. 登录学籍管理，查询家庭住址等其他信息，并解析保存

import requests
import time
import sys
import re
import LoginFunction

# 账号密码
Stunum = '201601010101'
StuPass = LoginFunction.SearchFromCsv('XH', Stunum)['SFZH'] # 查询学籍表，获得身份证号

# 默认查询自己的信息，带参数时为他人信息
if len(sys.argv) == 2:
    action = sys.argv[1]
    Key = LoginFunction.CheckArgv(action)

    # 对返回值做判断,遇到非法输入直接退出
    if Key == None:
        sys.exit()

    # print(LoginFunction.CheckArgv(action))
    Stunum = Key[0]
    StuPass = Key[1]
# print(Stunum,StuPass)

# 获取当前时间戳（登录函数需要用到）
TimeNow = int(round(time.time() * 1000))

# 浏览器标志头
CHROME_HEADERS = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'

# POST地址
# 登录页面的post地址
LOGIN_URL = 'http://202.115.133.173:805/Common/Handler/UserLogin.ashx'
# 成绩单页面地址
CjdUrl1 = 'http://202.115.133.173:805/rpt.aspx?rid=stucjd&stucode=' + str(Stunum)
CjdUrl2 = 'http://202.115.133.173:805/FastReport.Export.axd?object=' # + str(object.group())


# 登录请求头
LoginHeads = {
    'User-Agent':'%s' %CHROME_HEADERS,
    'Referer':'http://202.115.133.173:805/Login.html'
}

# POST字典
# 登录页面的post字段
LoginPostData = {
    'Action': 'Login',
    'userName': Stunum,
    'pwd': LoginFunction.getAaoPwd(Stunum, StuPass, str(TimeNow)),
    'sign': str(TimeNow)
}

print('正在获取...')

# 登录过程如下
# 获取cookies
AaoCookie = LoginFunction.GetCookie(LOGIN_URL, LoginPostData, LoginHeads)

# 利用获得的cookie，爬取成绩单页面
# 分两步，第一步请求获得object的值（真实页面地址）（利用正则表达式搜索）
# 第二步组装链接，爬取成绩单页面
CjdRequest1 = requests.get(CjdUrl1, cookies = AaoCookie)
object = re.search(r'fr\w\w\w\w\w\w', CjdRequest1.text).group()

CjdRequest2 = requests.get(CjdUrl2 + object, cookies = AaoCookie)
#print(CjdRequest2.text)

# 解析并输出成绩单
LoginFunction.AnalyzeScore(object, CjdRequest2)
