from flask import Blueprint,render_template
from moldes import Article
import math

type = Blueprint('type',__name__)

@type.route('/type/<string>')
def classify(string):
    #前端传过来的数据的格式为1-1,2-2.所以需要使用split将其拆分为type和page
    type = int(string.split('-')[0])
    page = int(string.split('-')[1])
    pagesize = 5
    start = (page-1)*pagesize #根据当前页面定义数据的起始位、
    article = Article()
    result = article.find_by_type(type,start,pagesize)
    total = math.ceil(article.get_count_by_type(type)/pagesize)  #计算总页数
    last, most, recommended = article.find_last_most_recommened()
    return render_template('type.html',result=result,page=page,total=total,last=last,most=most,recommended=recommended)