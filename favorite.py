from flask import Blueprint,render_template,session,request
from moldes import Favorite
import math

favorite = Blueprint('favorite ',__name__)

#文章接口

@favorite.route('/favorite',methods=['POST'])
def add_favorite():
    articleid= request.form.get('articleid')
    if session.get('islogin') is None:
        return 'not-login'
    else:
        try:
            Favorite().insert_favorite(articleid)
            return 'favorite-pass'
        except:
            return 'favorite-faill'


#取消收藏接口
@favorite.route('/favorite/<int:articleid>',methods=['DELETE'])
def cancel_favorite(articleid):
    try:
        Favorite().cancel_favorite(articleid)
        return 'cancel-pass'
    except:
        return 'cancel-fail'