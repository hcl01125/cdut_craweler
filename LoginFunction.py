#encoding=utf-8
# 该模块为登录教务处及学籍管理、处理页面相关的函数
# TODO: 1. 从学籍表中查询账号密码，登录教务处
# TODO: 2. 查询成绩、班级等各项信息，并解析保存
# TODO: 3. 登录学籍管理，查询家庭住址等其他信息，并解析保存
# TODO: 4. 综合排版所有信息，输出成 word 或 pdf

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
    with open('/root/文档/cdut_crawel/学籍表.csv','r') as csvfile:
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

# 定义解析成绩单页面的函数 
# (attr：成绩单页面第一次请求时的object值, requ：beautifulSoup对象(用于解析科目成绩), requ2：用于解析绩点等信息)
# fix: 添加requ2，专门解析绩点相关信息
def AnalyzeScore(attr,requ,requ2):
    Soup = BeautifulSoup(requ.content, "html.parser")
    Soup2 = BeautifulSoup(requ2.content, "html.parser") # Soup2专门用于解析绩点等信息
    
    # 先用正则表达式搜索学期那一栏的class值
    SemesterObject = re.search(r'\w\w">20\w\w0\w<', requ.text).group()
    object = attr + 's' + SemesterObject[0]+SemesterObject[1]

    # 建立并获得成绩字典
    ScoreList = [] # 最终的成绩字典
    Score = {} # 中间变量，传递每学期的字典
    semester = [] # 保存学期列表

    # 获取姓名绩点等信息
    TagName = Soup2.find_all(name='td')
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

# 定义查询课程列表的函数
def GetCourseList(URL, TaskType, Cookie):
    # 选课页面的查询字符串
    SelectParams = {
        'Action':'GetTeachTask',
        'taskType': TaskType, # 01:计划课 02:选修课 03:补课 04:跨专业选课 (GET)
        'rnd':'0.7902151354983268', # 随机数
        'pageIndex':'0', 
        'pageSize':'300'
    }

    # 课程查询
    req = requests.get(URL, cookies = Cookie, params = SelectParams)
    #print(Course.json())
    try:
        ReqCourse = req.json()
    except:
        print('解析出错!')
    Course = ReqCourse['TeachTaskEntities']
    CourseList = []

    for i in range(len(Course)):
        # 筛出待选课程
        if Course[i]['IsSelectCourse'] == False:
            CourseList.append(Course[i])

    for i in range(len(CourseList)):
        print(
            str(i+1), CourseList[i]['CourseName'] + "(%s)  " %(CourseList[i]['Id']),
            CourseList[i]['TeacherName'], 
            '  剩余:', 
            str(CourseList[i]['MaxStuNum'] - CourseList[i]['StuNum'])
        )
    t = input('请输入要选的课程序号:')
    print(
        '\n确定要选?  ', 
        CourseList[int(t)-1]['CourseName'] + "(%s)  " %(CourseList[int(t)-1]['Id']), 
        CourseList[int(t)-1]['TeacherName'],
        '  剩余:', 
        str(CourseList[int(t)-1]['MaxStuNum'] - CourseList[int(t)-1]['StuNum'])
    )

    key = input()

    if key == '':
        return CourseList[int(t)-1]['Id']


#CheckCourse('01', AaoCookie)

# 定义选课的函数
def SelectCourse(URL, Cookie, ClassId, SclassId, TaskId, TaskType, JclassId):
    Params = {
        'Action':'SelectCourse',
        'TaskType': TaskType, # 课程类型 01:计划课 02:选修课 03:补课 04:跨专业选课
        'TaskId':TaskId, # 课程Id
        'ClassId': ClassId, # 实验教学班Id ClassMode=01
        'ClassId2':'0',
        'ClassId3':'0',
        'SclassId': SclassId, # 课堂教学班Id ClassMode=02
        'SclassId2':'0',
        'SclassId3':'0',
        'oclassId':'0', # 暂时没看到这样的Id ClassMode=04
        'oclassId2':'0',
        'oclassId3':'0',
        'jclassId': JclassId, # 实践教学班Id ClassMode=03
        'jclassId2':'0',
        'jclassId3':'0',
        'oType':'04'
    }
    # 选课
    XK = requests.post(URL, cookies = Cookie, params = Params)
    print(XK.json())


# 定义退课的函数
def ExitCourse(URL, Cookie, TaskId, TaskType):
    Params = {
        'Action':'ExitSelectCourse',
        'TaskType': TaskType, # 01:计划课 02:选修课 03:补课 04:跨专业选课 05:全校开设所有课程
        'TaskId':TaskId
    }

    # 退课
    TK = requests.post(URL, cookies = Cookie, params = Params)
    print(TK.json())



# 定义查看课程详情的函数
# 查询课程信息,以列表形式返回各参数值
def ViewCourse(URL, Cookie, TaskId, TaskType):
    Params = {
        'Action':'GetTeachTaskClass',
        'TaskType': TaskType, # 01:计划课 02:选修课 03:补课 04:跨专业选课
        'TaskId':TaskId,
        'pageIndex':'1',
        'pageSize':'100'

    }

    # 查看课程
    '''
    课程详情的json为一个有两个key的字典:
        "data":{}  为课程详情,存放课程,班级
        "TaskId":xxxxxx 课程Id
    课程分多种: 
        1. 单项(data中只含"02"的列表)
        2. 含实验课(data项中还有"01"的列表) 01为实验教学班,02为课堂教学班
        3. 多班(data中"02"的列表含有多个班级)
    '''
    VK = requests.post(URL, cookies = Cookie, params = Params)
    try:
        ReqCourse = VK.json()
    except:
        print('解析出错!')
    Course = ReqCourse['data']

    # 选课函数需要的参数
    SelectValue = {
        'ClassId':'0',
        'SclassId':'0',
        'jclassId':'0',
        'oclassId':'0'
    }
    ClassList = []
    
    for key in Course:
        # 判断多班级的情况
        if len(Course['%s' %key]) > 1:
            for i in range(len(Course['%s' %key])):
                ClassList.append(Course['%s' %key][i])

            for x in range(len(ClassList)):
                print(
                    str(x+1),
                    ClassList[x]['TeachNames']
                )
            t = input('输入要选择的班级:')

            if ClassList[int(t)-1]['ClassMode'] == '01':  
                SelectValue['ClassId'] = ClassList[int(t)-1]['Id']
            elif ClassList[int(t)-1]['ClassMode'] == '02':  
                SelectValue['SclassId'] = ClassList[int(t)-1]['Id']
            elif ClassList[int(t)-1]['ClassMode'] == '03':  
                SelectValue['jclassId'] = ClassList[int(t)-1]['Id']
            elif ClassList[int(t)-1]['ClassMode'] == '04':  
                SelectValue['oclassId'] = ClassList[int(t)-1]['Id']

            # return ClassList[int(t)-1]['ClassMode'], ClassList[int(t)-1]['Id']
        # 其他情况统一处理
        else:
            for i in range(len(Course['%s' %key])):
                if Course['%s' %key][i]['ClassMode'] == '01':  
                    SelectValue['ClassId'] = Course['%s' %key][i]['Id']
                elif Course['%s' %key][i]['ClassMode'] == '02':  
                    SelectValue['SclassId'] = Course['%s' %key][i]['Id']
                elif Course['%s' %key][i]['ClassMode'] == '03':  
                    SelectValue['jclassId'] = Course['%s' %key][i]['Id']
                elif Course['%s' %key][i]['ClassMode'] == '04':  
                    SelectValue['oclassId'] = Course['%s' %key][i]['Id']
    return SelectValue
