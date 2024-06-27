from flask import Flask,render_template,request,session
from moldes import Article,User
from settings import Config,db
from index import index
from type import type
from utility import utility
from article import article
from favorite import favorite
from comment import comment
from ueditor import ueditor
from ucenter import ucenter
from admin import admin
from user import user
from moldes import User

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  #初始化数据库工具对象，使flask和数据库连接起来n

app.register_blueprint(index,url_prefix='/')
app.register_blueprint(user,url_prefix='/')
app.register_blueprint(type,url_prefix='/')
app.register_blueprint(article,url_prefix='/')
app.register_blueprint(utility,url_prefix='/')
app.register_blueprint(favorite,url_prefix='/')
app.register_blueprint(comment,url_prefix='/')
app.register_blueprint(ueditor,url_prefix='/')
app.register_blueprint(ucenter,url_prefix='/')
app.register_blueprint(admin,url_prefix='/')


# @app.route('/img')
# def img():
#     result = Article.query.get(1001)
#     print(result.thumbnail)
#
#     return 'ok'



# 定义文章类型函数，供模板页面直接调用
@app.context_processor
def gettype():
    type = {
        '1': 'PHP开发',
        '2': 'Java开发',
        '3': 'Python开发',
        '4': 'Web前端',
        '5': '测试开发',
        '6': '数据科学',
        '7': '网络安全',
        '8': '大数据'
    }
    return dict(article_type=type)




#重写truncate原生过滤器
def mytruncate(s,length,end='...'):
    count=0
    new=''
    for c in s:
        new += c
        if ord(c)<128:
            count+=0.5
        else:
            count+=1
        if count > length:
            break
    return new+end

app.jinja_env.filters.update(truncate=mytruncate)



# @app.before_request
def before():
    url = request.path
    pass_list = ['/user','/login','/logout']
    #以下请求不实现自动登录
    if url in pass_list or url.endswith('.png') or url.endswith('.jpg') or url.endswith('.js') or url.endswith('.css'):
        pass
    elif session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password !=None:
            user = User()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['username'] = result[0].nickname
                session['role'] = result[0].role
        else:
        #如果用户为游客，则拦截下列接口，游客不能使用这些接口
            deny_list=['/readall','/prepost','/article','/comment','/reply','favortie']
            import re
            if url in deny_list or re.match("/comment/\d+$",url):
                return render_template('no-per.html')
      #如果用户登录，则根据角色判断哪些接口可以使用
    else:
        role = session.get('role')
        if role != 'editor' and (url=='/article' or url =='/prepost'):
            return render_template('no-per.html')




if __name__ == '__main__':
    app.run()