from flask import Blueprint,render_template,session,request,jsonify
from moldes import Comment,User,Article,Opinion

import math

comment = Blueprint('comment',__name__)
@comment.route('/comment',methods=['POST'])
def add():
    articleid = request.form.get('articleid')
    content = request.form.get('content')
    # ipaddr = request.remote_addr#获取用户IP地址

    if len(content)<5 or len(content)>1000:
        return 'content-invalid'

    comment=Comment()
    if not comment.check_limit_per_5():

        try:
            comment.insert_comment(articleid=articleid,content=content)
            Article().update_replycount(articleid)

            return 'add-pass'
        except:
            return 'add-fail'
    else:
        return 'add-limit'


#接受回复评论的数据
@comment.route('/reply',methods=['POST'])
def reply():
    articleid = request.form.get('articleid')
    commentid = request.form.get('commentid')
    content = request.form.get('content').strip()

    if len(content)<5 or len(content)>1000:
        return 'content-invalid'

    comment=Comment()
    if not comment.check_limit_per_5():
        try:
            comment.insert_reply(articleid=articleid,commentid=commentid,content=content)

            Article().update_replycount(articleid)
            return 'reply-pass'
        except:
            return 'reply-fail'
    else:
        return 'reply-limit'


@comment.route('/comment/<int:articleid>-<int:page>')
def comment_page(articleid,page):
    start = (page-1)*10
    comment=Comment()
    list=comment.get_comment_user_list(articleid,start,10)
    return jsonify(list)



# @comment.route('/comment/<int:commentid>',methods=['DELETE'])
# def hide_comment(commentid):
#     comment = Comment()
#     print('0000100101')
#     articleid,commenterid=comment.find_article_commenter_by_id(commentid)
#     editorid = Article().find_by_id(articleid)[0].userid
#     userid = session.get('userid')
#     if session.get('role')!='admin' and editorid!=userid and commenterid!=userid:
#         return 'perm-denied'
#     result  = Comment().hide_comment(commentid)
#
#     if result =='Done':
#         return 'hide-pass'
#     else:
#         return 'hide-limit'


@comment.route('/opinion',methods=['POST'])
def do_opinion():
    commentid=request.form.get('commentid')
    type=int(request.form.get('type'))
    opinion=Opinion()
    is_checked = opinion.check_opinion(commentid)
    if is_checked:
        return 'already-opinion'
    else:
        opinion.insert_opinion(commentid,type)
        Comment().update_agreee_oppose(commentid,type)
    return 'opinion-pass'
#
@comment.route('/comment/<int:commentid>',methods=['DELETE'])
def hide_comment(commentid):
    result = Comment().hide_comment(commentid)
    print(result)
    if result=='Done':
        return 'hide-pass'
    else:
        return 'hide-limit'
