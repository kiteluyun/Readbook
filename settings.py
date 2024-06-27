#系统配置文件：1.数据库工具配置，2.系统配置
from flask_sqlalchemy import SQLAlchemy

import pymysql
pymysql.install_as_MySQLdb() #安装myspldb的驱动
db = SQLAlchemy()


class Config:#(object)括号中写的是父类，默认是object（面向对象的根类）
    DEBUG = True
    SECRET_KEY='hxci123456'
    # 添加mysql数据库的配置项:格式：数据类型+驱动：//用户名：密码@数据库主机地址：端口/数据库名
    SQLALCHEMY_DATABASE_URI= 'mysql://root:123456@localhost:3306/Readbook'