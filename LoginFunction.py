#encoding=utf-8
# 该模块为登录教务处及学籍管理、处理页面相关的函数
# TODO: 1. 从学籍表中查询账号密码，登录教务处
# TODO: 2. 查询成绩、班级等各项信息，并解析保存
# TODO: 3. 登录学籍管理，查询家庭住址等其他信息，并解析保存

import requests
import hashlib
import re
import csv
from bs4 import BeautifulSoup

# 计算教务处登录密码（学号，身份证号，当前时间），返回值为加密后的密码
def getAaoPwd(userName, userPwd, signTime):
    a = hashlib.md5(userPwd.encode())
    b = userName + signTime + a.hexdigest()
    temp = hashlib.md5(b.encode())
    return temp.hexdigest()

# 获取cookies的函数
def GetCookie(url, postdata, header):
    ss = requests.session()
    x = ss.post(url, data=postdata, headers = header, allow_redirects = False)
    return x.cookies

# 定义从csv文件中查找账号密码的函数
def SearchFromCsv(Flag, KeyWords):
    with open('user.csv','r') as csvfile:
        reader = csv.DictReader(csvfile)
        if Flag == 'XM':
            ReturnList = []  # 查询姓名时，判断重名的情况
            for row in reader:
                if row['XM'] == KeyWords:
                    ReturnList.append(row.copy())
            return ReturnList
        elif Flag == 'XH':
            for row in reader:
                if row['XH'] == KeyWords:
                    return row
        elif Flag == 'SFZH':
            for row in reader:
                if row['SFZH'] == KeyWords:
                    return row
        else:
            return False

# 定义解析成绩单页面的函数 (attr：成绩单页面第一次请求时的object值， requ：beautifulSoup对象)
def AnalyzeScore(attr,requ):
    Soup = BeautifulSoup(requ.content, "html.parser")
    
    # 先用正则表达式搜索学期那一栏的class值
    SemesterObject = re.search(r'\w\w">20\w\w0\w<', requ.text).group()
    object = attr + 's' + SemesterObject[0]+SemesterObject[1]

    # 建立并获得成绩字典
    ScoreList = [] # 最终的成绩字典
    Score = {} # 中间变量，传递每学期的字典
    semester = [] # 保存学期列表

    # 获取姓名绩点等信息
    TagName = Soup.find_all(name='td')
    FindKey = ['学  院', '学  号', '专业（层次）', '姓  名', '课程数', '平均成绩', '总学分', '平均学分绩点']
    for k in FindKey:
        for td in TagName:
            if td.getText() == k:
                Score[td.getText()] = td.find_next("td").getText()
    ScoreList.append(Score.copy())
    Score.clear()

    # 循环获取学期列表，并为每个学期分别创建字典
    tag = Soup.find_all(name='td', attrs={'class':object})
    for td in tag:
        if td.getText() not in semester:
            semester.append(td.getText())
    #print(semester)
    semester.sort() # 对学期列表排序

    for seme in semester:
        for td in tag:
            if td.getText() == seme:
                Score['学期'] = td.getText()
                Score[td.find_next("td").getText()] = td.find_next("td").find_next("td").find_next("td").find_next("td").getText() #比较挫的办法，以后再优化吧
        ScoreList.append(Score.copy())
        Score.clear()
    print('\n')
    # 循环输出获得的成绩
    for x in ScoreList:
        if isinstance(x,dict):
            for key,value in x.items():
                print(key,':',value)
        print('\n')
    return

# 定义解析学籍信息页面的函数
def AnalyzeStatus(requ):

    # 定义关键词列表
    FindKey = ['姓\xa0\xa0名','性\xa0\xa0别','身份证号','出生年月','姓名拼音','政治面貌',
    '籍\xa0\xa0贯','民\xa0\xa0\xa0\xa0族','高考省份','考生类别','毕业类型','毕业中学','考生号',
    '手机号码','家庭固定电话','QQ号','邮政编码','电子邮件','父、母亲姓名',
    '家庭详细地址','个人特长','手机号码','培养层次','学院','专业','当前级']  # 万恶的&nbsp; 可以用\xa0转义

    Info = {}

    Soup = BeautifulSoup(requ, "html.parser")
    tag = Soup.find_all("td")
    for xx in FindKey:
        for td in tag:
            if td.getText() == xx:
                temp = re.sub(r'\s','',td.find_next("td").getText()) # 用正则表达式去除结果中的空格
                Info[td.getText()] = temp
    print('\n')
    for key,value in Info.items():
        print(key, ':', value)
    print('\n')


# 定义处理参数的函数，返回值为学号和身份证号
def CheckArgv(argv):
    if u'\u4e00' <= argv[0] <= u'\u9fff':
        x = SearchFromCsv('XM', argv)
        if len(x) >= 2:    # 判断重名的情况
            num = 1
            for a in x:
                print(num, a['XM'], a['XH'])
                num = num + 1
            t = input('请选择要查询的对象:')
            return x[int(t)-1]['XH'], x[int(t)-1]['SFZH']
        elif len(x) == 1:
            return x[0]['XH'], x[0]['SFZH']
        else:
            print('用户不存在')
            return None
    elif len(argv) <= 15:
        x = SearchFromCsv('XH', argv)
        if x == None:
            print('用户不存在')
            return None
        else:
            return x['XH'], x['SFZH']
    else:
        x = SearchFromCsv('SFZH',argv)
        if x == None:
            print('用户不存在')
            return None
        else:
            return x['XH'], x['SFZH']
