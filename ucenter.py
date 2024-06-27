import os,time,math
from settings import db


from flask import Blueprint,render_template,request,jsonify,session,redirect,url_for
from moldes import Favorite,Article,Comment

ucenter = Blueprint('ucenter',__name__)
@ucenter.route('/ucenter')
def user_center():
    result = Favorite().find_my_favorite()
    return render_template('user-center.html',result=result)



#切换收藏状态
@ucenter.route('/user/favorite/<int:favoriteid>')
def user_favorite(favoriteid):
    canceled=Favorite().switch_favorite(favoriteid)
    return str(canceled)

#我的草稿
@ucenter.route('/user/draft')
def draft():
    result = Article().find_my_drafted()
    return render_template('user-dref.html',result=result)



#编辑我的草稿
@ucenter.route('/edit/dref/<int:articleid>')
def go_edit_dref(articleid):
    result = Article().find_dref_id(articleid)
    return render_template('dreft-edit.html',result=result)




#我的文章
@ucenter.route('/user/article')
def my_title():
    result = Article().find_my_title(0,10)
    num = Article().find_my_title_count()
    total = math.ceil(num/10)
    return render_template('user-title.html',result=result,page=1,total=total,num=num)

#我的草稿
@ucenter.route('/user_caogao/article')
def my_caogao_title():
    result = Article().find_my_title(0,10)
    num = Article().find_my_title_count()
    total = math.ceil(num/10)
    return render_template('user-caogao.html',result=result,page=1,total=total,num=num)
# #编辑投稿
@ucenter.route('/edit/caogao/<int:articleid>')
def go_edit_cgao(articleid):
    result = Article().find_caogao_id(articleid)
    return render_template('caogao-edit.html',result=result)




# 删除文章
@ucenter.route('/delete/<int:articleid>',methods=['POST','GET'])
def delete_article(articleid):
    # 获取要删除的文章
    article = Article().query.filter_by(articleid=articleid).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('ucenter.my_title'))


#删除草稿
@ucenter.route('/delete/dref/<int:articleid>')
def delete_dref(articleid):
    article = Article().query.filter_by(articleid=articleid).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('ucenter.draft'))







@ucenter.route('/page/mytitle/<int:page>')
def paginate_my_title(page):
    pagesize=10
    start = (page - 1)*pagesize
    article = Article()
    result = article.find_my_title(start,pagesize)
    total = math.ceil(article.find_my_title_count()/10)
    return render_template('user-title.html', result=result,page=page,total=total)


@ucenter.route('/user/comment')
def find_comment():
    comment = Comment()
    result = comment.find_by_userid()
    return render_template('user-comment.html',result=result)

#删除评论
@ucenter.route('/delete/comment/<int:commentid>')
def delete_comment(commentid):
    article = Comment().query.filter_by(commentid=commentid).first()
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('ucenter.find_comment'))



#我要投稿
@ucenter.route('/user/post')
def user_post():
    return render_template('user-add.html')


#查看草稿详情
@ucenter.route('/article/caogao/<int:articleid>')
def read(articleid):
    result = Article().find_by_caogao(articleid)
    article = result[0]

    # 由于直接修改article.content的值会导致数据表内容的修改
    # 所以将result中的值取出来保存到字典中，不直接操作result的article对象
    dict = {}
    for k, v in article.__dict__.items():
        if not k.startswith('_sa_instance_state'):
            dict[k] = v
    dict['nickname'] = result.nickname
    return render_template('caogao_chaokan.html',article=dict)


#编辑我的投稿
@ucenter.route('/edit/caogao',methods=['POST'])
def edit_article():
    articleid = int(request.form.get('articleid'))
    headline = request.form.get('headline')
    content = request.form.get('content')
    type = int(request.form.get('type'))
    article=Article()
    try:
        row = article.find_by_caogao(articleid)

        id = article.update_article(articleid=articleid,type=type,headline=headline,content=content,
                                    thumbnail=row[0].thumbnail,drafted=row[0].drafted,checked=row[0].checked)
        print(id)
        return str(id)
    except:
        return 'edit-fail'
