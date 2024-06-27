from flask import Blueprint,render_template,abort,jsonify,request,session
from moldes import Article,Favorite,Comment,User
import math,os
from utility import parse_image_url,generate_thumb

article = Blueprint('article',__name__)


@article.route('/search/<int:page>-<keyword>')
# @article.route('/search/<keyword>')
def search(page,keyword):
    keyword=keyword.strip() #去除关键字前后的空格
    if keyword is None or '%' in keyword or len(keyword)>10:
        abort(404) #如果出错，则直接响应404或500页面，或进入某个提醒页面
    pagesize=5
    start = (page - 1) * pagesize
    article = Article()
    result = article.find_by_headline(keyword,start,pagesize)
    total = math.ceil(article.get_count_by_headline(keyword)/pagesize)
    last, most, recommended = article.find_last_most_recommened()
    return render_template('search.html',result=result,page=page,total=total,keyword=keyword,last=last,most=most,recommended=recommended)




@article.route('/recommend')
def recommend():
    article = Article()
    last, most, recommended = article.find_last_most_recommened()
    list=[]
    list.append(last)
    list.append(most)
    list.append(recommended)
    return jsonify(list)




@article.route('/article/<int:articleid>')
def read(articleid):
    comment = Comment()
    try:
        result = Article().find_by_id(articleid)

        if result is None:
            abort(404)
    except:
        abort(500)
    article=result[0]

    #由于直接修改article.content的值会导致数据表内容的修改
    #所以将result中的值取出来保存到字典中，不直接操作result的article对象
    dict={}
    for k,v in article.__dict__.items():
        if not k.startswith('_sa_instance_state'):
            dict[k] = v
    dict['nickname']=result.nickname

    is_favorited = Favorite().check_favorite(articleid)
    prev_next = Article().find_prev_next_by_id(articleid)
    # comment_user=Comment().find_limit_with_user(articleid,0,50)
    #获取文章对应的原始评论和回复评论
    comment_list = Comment().get_comment_user_list(articleid,0,50)
    count = comment.get_count_by_article(articleid)
    total=math.ceil(count/10)
    Article().update_read_count(articleid)
    return render_template('article_user.html',article=dict,is_favorited=is_favorited,prev_next=prev_next,comment_list=comment_list,total=total)





@article.route('/prepost')
def prepost():
    return render_template('add.html')


@article.route('/article', methods=['POST'])
def add_article():
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
        if user.role == 'editor':
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





@article.route('/edit/<int:articleid>')
def go_edit(articleid):
    result = Article().find_by_id(articleid)
    return render_template('article-edit.html',result=result)


@article.route('/edit',methods=['POST'])
def edit_article():
    articleid = int(request.form.get('articleid'))
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))

    article=Article()
    try:
        row = article.find_by_id(articleid)

        id = article.update_article(articleid=articleid,type=type,headline=headline,content=content,
                                    thumbnail=row[0].thumbnail,drafted=row[0].drafted,checked=row[0].checked)
        print(id)
        return str(id)
    except:
        return 'edit-fail'



