import re
from settings import Config,db
from flask import Blueprint,render_template
import hashlib
from moldes import User,Article
from flask import session,request,redirect,url_for,make_response,sessions
from utility import parse_image_url,generate_thumb

user = Blueprint('user',__name__)

@user.route('/user',methods=['POST'])
def register():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    role = request.form.get('role').strip()
    ecode = request.form.get('ecode').lower().strip()
    if ecode != session.get('ecode'):
        return 'ecode-error'
    #注册时继续验证邮箱地址的正确性
    elif not re.match('.+@.+\..+',username) or len(password)<5:
        return 'up-invalid'
    elif len(user.find_by_username(username))>0:
        return 'user-repeated'
    else:
        #对密码进行MD5加密并保存
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.do_register(username,password,role)
        try:
            session['islogin']='true'
            session['userid']=result.userid
            session['username']=username
            session['username']=result.nickname
            session['role']=role
            return 'reg-pass'
        except:
            return 'reg-fail'


@user.route('/login',methods=['POST'])
def login():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').lower().strip()
    if vcode != session.get('vcode'):
        return 'vcode-error'
    else:
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        print(result[0].password)
        if len(result)==1 and result[0].password==password:
            session['islogin']='true'
            session['userid'] = result[0].userid
            session['username'] = result[0].username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role
            #重新定义响应内容，并在响应头中设置2条cookie变量
            response = make_response('login-pass')
            # cookie的max_age即为有效期，单位时间为秒30天30*24*3600
            response.set_cookie('username',username,max_age=30*24*3600)
            response.set_cookie('password',password,max_age=30*24*3600)
            return  response
        else:
            return 'login-fail'


#重置密码
@user.route('/getpass',methods=['POST'])
def getpass():
    user = User()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    fcode = request.form.get('fcode').lower().strip()
    if fcode != session.get('ecode'):
        return 'vcode-error'
    else:
        password = hashlib.md5(password.encode()).hexdigest()
        result = user.find_by_username(username)
        result[0].password = password
        db.session.commit()
        if len(result)==1:
            session['userid'] = result[0].userid
            session['username'] = result[0].username
            session['nickname'] = result[0].nickname
            session['role'] = result[0].role
            #重新定义响应内容，并在响应头中设置2条cookie变量
            response = make_response('login-pass')
            # cookie的max_age即为有效期，单位时间为秒30天30*24*3600
            response.set_cookie('username',username,max_age=30*24*3600)
            response.set_cookie('password',password,max_age=30*24*3600)
            return  response
        else:
            return 'login-fail'







#注销
@user.route('/logout')
def logout():
    session.clear()
    response = make_response('自定义响应，随便看看，会跳转的',302)
    response.headers["Location"]=url_for('index.home')
    response.delete_cookie('username')
    response.set_cookie('password','',max_age=0)
    return response




@user.route('/user_article', methods=['POST'])
def add__user_article():
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    drafted = int(request.form.get('drafted'))
    checked = int(request.form.get('checked'))
    articleid = int(request.form.get('articleid'))
    if session.get('userid') is None:
        return 'perm-denied'
    else:
        user = User().find_by_userid(session.get('userid'))
        if user.role == 'user':
            # # 权限合格，可以执行发布文章的代码
            # # 首先为文章生成缩略图，优先从内容中找，找不到则随机生成一张
            url_list = parse_image_url(content)
            if len(url_list) > 0:   # 表示文章中存在图片
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，则根据文章类别指定一张缩略图
                thumbname = '%d.png' % type

                article = Article()
            # 再判断articleid是否为0，如果为0则表示是新数据
                if articleid == 0:
                    try:
                        id = article.insert_article(type=type, headline=headline, content=content,
                                                    thumbnail=thumbname,drafted=drafted, checked=checked)

                        return str(id)
                    except Exception as e:
                        return 'post-fail'
                else:
                # 如果是已经添加过的文章，则做修改操作
                    try:
                        id = article.update_article(articleid=articleid, type=type,
                                                    headline=headline, content=content,
                                                    thumbnail=thumbname, drafted=drafted, checked=checked)

                    except:
                        return 'post-fail'

        # 如果角色不是作者，则只能投稿，不能正式发布
        elif checked == 1:
                return 'perm-denied'
        else:
            return 'perm-denied'

