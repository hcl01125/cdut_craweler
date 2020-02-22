#encoding=utf-8
# 该文件为登录学籍管理页面获取信息的模块
# TODO: 1. 从学籍表中查询账号密码，登录教务处
# TODO: 2. 查询成绩、班级等各项信息，并解析保存
# TODO: 3. 登录学籍管理，查询家庭住址等其他信息，并解析保存

import sys
import requests
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

# 浏览器标志头
CHROME_HEADERS = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'

# post地址
StudentStatusLoginUrl = 'http://202.115.139.10/jwc_xjgl/login_prooftest.jsp'
StudentStatusInfoUrl = 'http://202.115.139.10/jwc_xjgl/stu_message_viewok_print.jsp'

# 登录请求头
StudentStatusHeader = {
    'User-Agent':'%s' %CHROME_HEADERS,
    'Referer':'http://202.115.139.10/web/index.html'
}

# POST字典
# 登录页面的post字段
StudentStatusPostdata = {
    'UserID': Stunum,
    'PassWords': StuPass,
    'sf_def': 'students',
    'CHKNUM':''
}

print('正在获取...')

# 学籍系统的页面发生了跳转，因此需要在getcookie函数中禁用跳转，否则取不到cookie
StudentStatusCookie = LoginFunction.GetCookie(StudentStatusLoginUrl, StudentStatusPostdata, StudentStatusHeader)
#print(StudentStatusCookie)
StudentStatusRequest = requests.get(StudentStatusInfoUrl, cookies = StudentStatusCookie)
#print(StudentStatusRequest.text)

# 对获取的页面进行解析

LoginFunction.AnalyzeStatus(StudentStatusRequest.content)
