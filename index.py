import math,json
from flask import Blueprint,render_template,session,request,jsonify,abort
from moldes import Article,User
from settings import Config,db

index = Blueprint('index','__name__')


@index.route('/')
def home():
    #从请求中获取浏览器的cookie值，用于实现自动登录的判断
    if session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password !=None:
            user =User()
            result = user.find_by_username(username)
            if len(result)==1 and result[0].password ==password:
                session['islogin']='true'
                session['userid']=result[0].userid
                session['username']=username
                session['nickname']=result[0].nickname
                session['role']=result[0].role
            else:
                pass

    article = Article()
    result = article.find_limit_with_users(0,5)
    total = math.ceil(article.get_total_count()/5)
    last,most,recommended = article.find_last_most_recommened()
    return render_template('index.html',result=result,page=1,total=total,last=last,most=most,recommended=recommended)





# 分页
@index.route('/page/<int:page>')
def paginate(page):
    pagesize=5
    start = (page - 1)*pagesize
    article = Article()
    result = article.find_limit_with_users(start,pagesize)
    total = math.ceil(article.get_total_count()/5)
    last, most, recommended = article.find_last_most_recommened()
    return render_template('index.html', result=result,page=page,total=total,last=last,most=most,recommended=recommended)







@index.route('/type/<int:type>-<int:page>')
def classify(type, page):
    start = (page - 1) * 5
    article = Article()
    result = article.find_by_type(type, start, 5)
    total = math.ceil(article.get_count_by_type(type) / 5)
    return render_template('type.html', result=result, page=page, total=total, type=type)

@index.route('/search/<int:page>-<keyword>')
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 10:
        # 终止函数
        abort(404)

    start = (page-1) * 10
    article = Article()
    result = article.find_by_headline(keyword, start, 10)
    total = math.ceil(article.get_count_by_headline(keyword) / 10)

    return render_template('search.html', result=result, page=page, total=total, keyword=keyword)

@index.route('/recommend')
def recommend():
    article = Article()
    last, most, recommended = article.find_last_most_recommened()
    list = []
    list.append(last)
    list.append(most)
    list.append(recommended)
    return jsonify(eval(str(list)))




