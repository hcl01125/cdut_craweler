# cdut_craweler
一个成都理工大学教务处查成绩和学籍的小爬虫

部分函数的实现参考了https://github.com/Vietronic/CDUT_crawler

程序介绍:

    全部程序为三个部分:
    [score.py], [status.py], [LoginFunction.py]
    [user.csv] 存放学生信息

    score.py 为查询并解析成绩单页面的模块
    status.py 为查询并解析学籍页面的模块
    LoginFunction.py 为相关函数的封装和大部分逻辑代码

使用方法:

    python score.py [参数] :传递参数并登录查询成绩单

    python status.py [参数] :传递参数并登录查询学籍信息

功能说明:

    1.实现了传递参数智能判断并查询对应结果. 参数为单个,可以为(学号,姓名,身份证号)中的任一个,如 python score.py 张三

    2.使用姓名查询时,实现了针对多个重名对象时的判断逻辑

    3.实现了用单一信息就可以查询并组合账号密码,然后登录教务处和学籍管理页面

    4.实现了模拟登录学籍管理页面和教务处成绩单页面的逻辑

    5.实现了对成绩单页面的爬取,并提取相关信息,然后按学期分类展示的功能

    6.实现了对学籍信息的抓取和排版

    7.为了体现代码的简洁性,将所有需要复用和相关的逻辑全部封装为函数,并专门存放,方便日后优化

    8.部分逻辑有待优化,查询时间过长(大概10s ?),代码还能更简洁高效

已知bug:

    默认成绩单只有一页,所以当成绩单超过一页时无法获取第二页信息

修复日志:

    2018.7.31: 修复部分学生成绩单错位的bug,由于并不是所有同学的成绩单页面'学期'栏的class值都一样的,所以一部分学生会错位,故添加查询'学期'栏class值的操作

    2018.8.11: 优化了参数查询的逻辑,运行速度应该会上升一点点 添加对非法输入的判断,外部运行看不到打脑壳的错误信息了
