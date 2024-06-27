from flask import Blueprint,render_template,request,jsonify,session,redirect,url_for
from moldes import Article,Comment,User,Favorite
import math
from settings import db
admin = Blueprint('admin',__name__)

# @admin.route('/admin')
# def sys_admin():
#     pagesize=50
#     article = Article()
#     result = article.find_all_except_draft(0,pagesize)
#     total = math.ceil(article.get_count_execpt_draft()/pagesize)
#     return render_template('system-admin.html',page=1,result=result,total=total)




# @admin.before_request
# def before_admin():
#     if session.get('islogin')!='true' or session.get('role') != 'admin':
#         return 'perm-denied'



# 为系统管理首页填充文章列表，并绘制分页栏
@admin.route('/admin')
def sys_admin():
    pagesize = 10
    article = Article()
    result = article.find_all_except_draft(0, pagesize)
    total = math.ceil(article.get_count_execpt_draft() / pagesize)
    return render_template('system-admin.html', page=1, result=result, total=total)




@admin.route('/admin/article/<int:page>')
def admin_article(page):
    pagesize=10
    start = (page-1)*pagesize
    article = Article()
    result = article.find_all_except_draft(start,pagesize)
    total = math.ceil(article.get_count_execpt_draft()/pagesize)
    return render_template('system-admin.html',page=1,result=result,total=total)

@admin.route('/admin/type/<int:type>-<int:page>')
def admin_search_type(type,page):
    pagesize = 10
    start = (page-1)*pagesize
    result,total=Article().find_by_type_except_draft(start,pagesize,type)
    total = math.ceil(total/pagesize)
    return render_template('system-admin.html',page=page,result=result,total=total)

@admin.route('/admin/search/<keyword>')
def admin_search_headline(keyword):
    result = Article().find_by_headline_except_draft(keyword)
    return render_template('system-admin.html',page=1,result=result,total=1)

#推荐
@admin.route('/admin/article/recommend/<int:articleid>')
def admin_article_recommend(articleid):
    recommended = Article().switch_recommended(articleid)
    return str(recommended)
#审核
@admin.route('/admin/article/check/<int:articleid>')
def admin_article_check(articleid):
    checked = Article().switch_checked(articleid)
    return str(checked)
#隐藏
@admin.route('/admin/article/hide/<int:articleid>')
def admin_article_hide(articleid):
    hidden = Article().switch_hidden(articleid)
    return str(hidden)

#查询所有评论
@admin.route('/admin/comment')
def find_all_comment():
    result = Comment().find_all_comment()
    return render_template('system-comment.html',result=result)

#删除评论
@admin.route('/admin/delete/comment/<int:commentid>')
def delete_comment(commentid):
    comment = Comment().query.filter_by(commentid=commentid).first()
    db.session.delete(comment)
    db.session.commit()
    return  redirect(url_for('admin.find_all_comment'))

#查询所有用户
@admin.route('/admin/user')
def admin_user():
    result = User().find_all_user()
    return render_template('system-user.html',result=result)

#删除用户信息
@admin.route('/admin/delete/user/<int:userid>')
def delete_user(userid):
    user = User().query.filter_by(userid=userid).first()
    db.session.delete(user)
    db.session.commit()
    return  redirect(url_for('admin.admin_user'))

#查询所有收藏的文章
@admin.route('/admin/favorite')
def admin_favorite():
    result = Favorite().find_all_favorite()
    return render_template('system-favorite.html',result=result)


#查询所有推荐文章
@admin.route('/admin/recommend')
def admin_recommend():
    result = Article().find_all_recommended()
    return render_template('system-recommend.html',result=result)

#取消推荐
@admin.route('/delete/recommend/<int:articleid>')
def delete_recommend(articleid):
    article = Article().query.filter_by(articleid=articleid).first()
    article.recommended=0
    db.session.commit()
    return redirect(url_for('admin.admin_recommend'))

#查询所有隐藏文章
@admin.route('/admin/hide')
def admin_hidden():
    result = Article().find_all_hidden()
    return render_template('system-hidden.html',result=result)


@admin.route('/delete/hidden/<int:articleid>')
def delete_hidden(articleid):
    article = Article().query.filter_by(articleid=articleid).first()
    article.hidden=0
    db.session.commit()
    return redirect(url_for('admin.admin_hidden'))


@admin.route('/admin/check')
def admin_checked():
    result = Article().find_all_checked()
    return render_template('system-checked.html',result=result)


@admin.route('/delete/check/<int:articleid>')
def delete_check(articleid):
    article = Article().query.filter_by(articleid=articleid).first()
    article.checked=0
    db.session.commit()
    return redirect(url_for('admin.admin_checked'))
