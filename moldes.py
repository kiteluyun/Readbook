import random

from flask import session
import time
from settings import db
from sqlalchemy import func
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' #指定当前模型映射的表名
    #创建属性，也就是映射表中的字段/列
    userid = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(40),nullable=False)
    nickname = db.Column(db.String(120), nullable=False)#用户昵称
    avatar = db.Column(db.String(120), nullable=True)  # 图片文件名
    role = db.Column(db.String(10),nullable=False)#用户角色 adimn管理员 editor作者 user 普通用户
    createtime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updatetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    #添加关联属性User表关联Article
    #art属性，是user表关联article的数据，user.art返回一个用户对应的所有文章列表数据
    #user引用，是article表关联user的数据 article.user返回一个文章所属的用户数据
    # 定义属性关系
    article = db.relationship('Article', backref='users')
    comment = db.relationship('Comment', backref='users')
    favorite = db.relationship('Favorite', backref='users')
    opinion = db.relationship('Opinion', backref='users')
    def find_all(self):
        result = db.session.query(User).all()
        return result

    #查询用户名，可用于注册时判断用户名是否已经被注册，也可用于登录校验
    def find_by_username(self,username):
        result = db.session.query(User).filter_by(username=username).all()
        return result
    def do_register(self,username,password,role):
        now = time.strftime('%Y-%m-%d  %H:%M:%S')
        nickname = username.split('@')[0] #默认将邮箱账号前缀作为昵称
        avatar = str(random.randint(1,17))
        user = User(username=username,password=password,role=role,nickname=nickname,avatar=avatar+'.jpg',createtime=now,updatetime=now)
        db.session.add(user)
        db.session.commit()
        return user

    def find_by_userid(self, userid):
        user = db.session.query(User).filter_by(userid=userid).one()
        return user

    #查询所有用户信息
    def find_all_user(self):
        result = db.session.query(User).all()
        return result






class Article(db.Model):
    __tablename__ = 'article'
    articleid = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    type = db.Column(db.String(255), nullable=False)#类型
    title = db.Column(db.String(255),nullable=False)#标题
    content = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(255),nullable=False)#图片
    readcount = db.Column(db.Integer,nullable=False,default=0) #文章阅读次数
    replycount = db.Column(db.Integer,nullable=False,default=0)#评论回复次数
    recommended = db.Column(db.Integer,nullable=False,default=0)#是否设置为推荐文章，默认为0，不推荐
    hidden = db.Column(db.Integer,nullable=False,default=0)#文章是否被隐藏，默认为0，不隐藏
    drafted = db.Column(db.Integer,nullable=False,default=0)#文章是否为草稿，默认为0.非草稿tinyint
    checked = db.Column(db.Integer, nullable=False,default=1)#文章是否已被审核，默认为1，正式文章
    createtime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updatetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    comment = db.relationship('Comment', backref='article')
    favorite = db.relationship('Favorite', backref='article')
    #与用户表进行连接查询并获取用户信息，且只返回10条数据
    def find_limit_with_users(self,start,count):
        result = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid)\
            .order_by(Article.articleid.asc()).limit(count).offset(start).all()
        return result
    #查询文章表中的所有数据并返回结果集
    def find_all(self):
        result = db.session.query(Article).order_by(Article.articleid.desc()).all()
        return result
    #根据id查询文章表中的唯一数据，并返回该行记录
    def find_by_id(self,articleid):
        row = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1,Article.articleid==articleid).first()
        return  row

    #获取文章总数
    def get_total_count(self):
        count = db.session.query(Article.articleid).filter(Article.hidden==0,Article.drafted==0,Article.checked==1).count()
        return count

    #根据文章类别查询文章，并进行分页查询
    def find_by_type(self,type,start,count):
        result = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid)\
            .filter(Article.hidden==0,Article.drafted==0,Article.checked==1,Article.type==type)\
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    #根据文章类别获取文章数量
    def get_count_by_type(self,type):
        count = db.session.query(Article.articleid).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1,Article.type==type).count()
        return count

    #对文章标题进行模糊查询，并实现分页
    def find_by_headline(self,headline,start,count):
        result = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid)\
            .filter(Article.hidden==0,Article.drafted==0,Article.checked==1,Article.title.like('%'+headline+'%'))\
            .order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    #根据文章标题进行模糊搜索，返回结果数量
    def get_count_by_headline(self,headline):
        count = db.session.query(Article.articleid).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1,Article.title.like('%'+headline+'%')).count()
        return count
    #查询阅读次数最多的9篇文章
    def find_last_9(self):
        result = db.session.query(Article.articleid,Article.title).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1).order_by(Article.articleid.desc()).limit(9).all()
        return result

    ##查阅阅读次数最多的9篇文章
    def find_most_9(self):
        result = db.session.query(Article.articleid,Article.title).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1).order_by(Article.readcount.desc()).limit(9).all()
        return result

    #查询特别推荐的9篇文章，从所有的推荐文章中随机挑选9篇
    def find_recommended_9(self):
        result = db.session.query(Article.articleid,Article.title).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==1,Article.recommended==1).order_by(func.rand()).limit(9).all()
        return result

    #一次性返回3种类型的推荐
    def find_last_most_recommened(self):
        last = self.find_last_9()
        most = self.find_most_9()
        recommened = self.find_recommended_9()
        return  last,most,recommened


    #每阅读一次文章，文章阅读次数增加1
    def update_read_count(self,articleid):
        article = db.session.query(Article).filter_by(articleid=articleid).one()
        article.readcount +=1
        db.session.commit()

    #更具文章编号查询文章标题
    def find_headline_by_id(self,articleid):
        row = db.session.query(Article.title).filter_by(articleid=articleid).first()
        return row.title

    #查询当前文章的上一篇和下一篇的编号和标题
    def find_prev_next_by_id(self,articleid):
        dict={}
        #查询比当期文章小一号的文章编号中的最大一个，即为上一篇文章
        row = db.session.query(Article).filter(Article.hidden==0,Article.drafted==0,Article.checked==1,Article.articleid<articleid).\
            order_by(Article.articleid.desc()).limit(1).first()

        #如果没有查询到比当期编号更小的文章编号，则说明当前文章为第一篇文章
        if row is None:
            prev_id = articleid
        else:
            prev_id = row.articleid

        dict['prev_id'] = prev_id
        dict['prev_headline'] = self.find_headline_by_id(prev_id)

        row = db.session.query(Article).filter(Article.hidden==0,Article.drafted==0,Article.checked==1,Article.articleid>articleid).\
            order_by(Article.articleid).limit(1).first()
        if row is None:
            next_id = articleid
        else:
            next_id = row.articleid

        dict['next_id']=next_id
        dict['next_headline']=self.find_headline_by_id(next_id)
        return dict

    #当发表或者回复评论后，字段加1
    def update_replycount(self,articleid):
        row = db.session.query(Article).filter_by(articleid=articleid).first()
        row.replycount += 1
        db.session.commit()

    #插入一篇新的文章，草稿或投稿通过参数进行区分
    def insert_article(self,type,headline,content,thumbnail,drafted=0,checked=1):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        userid = session.get('userid')
        article = Article(userid=userid,type=type,title=headline,content=content,thumbnail=thumbnail,drafted=drafted,checked=checked,createtime = now,updatetime=now)
        db.session.add(article)
        db.session.commit()
        return article.articleid
    #根据文章编号更新文章内容，可用于文章编辑或草稿修改，以及草稿的发布
    def update_article(self, articleid, type, headline, content, thumbnail, drafted=0, checked=1):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        row = db.session.query(Article).filter_by(articleid=articleid).first()
        row.type = type
        row.headline = headline
        row.content = content
        row.thumbnail = thumbnail
        row.drafted = drafted

        row.checked = checked
        row.updatetime = now  # 修改文章的更新时间
        db.session.commit()
        return articleid  # 继续将文章ID返回调用处

    #查询文章表中除草稿外的所有数据，并返回结果集
    def find_all_except_draft(self,start,count):
        result = db.session.query(Article).filter(Article.drafted==0).order_by(Article.articleid.desc()).limit(count).offset(start).all()
        return result

    #查询除草稿外的所有文章的总数量
    def get_count_execpt_draft(self):
        count = db.session.query(Article).filter(Article.drafted==0).count()
        return count

    #按照文章分类进行查询
    def find_by_type_except_draft(self,start,count,type):
        if type==0:
            result = self.find_all_except_draft(start,count)
            total = self.get_count_execpt_draft()
        else:
            result = db.session.query(Article).filter(Article.drafted==0,Article.type==type).order_by(Article.articleid.desc())\
                .limit(count).offset(start).all()
            total = db.session.query(Article).filter(Article.drafted==0,Article.type==type).count()
        return result,total

    #按照标题进行模糊查询
    def find_by_headline_except_draft(self,headline):
        result = db.session.query(Article).filter(Article.drafted==0,Article.title.like('%'+headline+'%')).\
            order_by(Article.articleid.desc()).all()
        return result
    #切换文章的隐藏状态
    def switch_hidden(self,articleid):
        row = db.session.query(Article).filter_by(articleid=articleid).first()
        if row.hidden==1:
            row.hidden=0
        else:
            row.hidden=1
        db.session.commit()
        return row.hidden
    #切换文章的推荐状态
    def switch_recommended(self,articleid):
        row = db.session.query(Article).filter_by(articleid=articleid).first()
        if row.recommended==1:
            row.recommended=0
        else:
            row.recommended=1
        db.session.commit()
        return row.recommended
        #切换文章的审核状态
    def switch_checked(self,articleid):
        row = db.session.query(Article).filter_by(articleid=articleid).first()
        if row.checked==1:
            row.checked=0
        else:
            row.checked=1
        db.session.commit()
        return row.checked
    #查询我的草稿
    def find_my_drafted(self):
        result = db.session.query(Article).filter(Article.drafted==1,Article.userid==session.get('userid')).all()
        return result


    #查询我的文章
    def find_my_title(self,start,count):
        result = db.session.query(Article).filter(Article.userid==session.get('userid')).limit(count).offset(start).all()
        return result

    def find_my_title_count(self):
        count = db.session.query(Article).filter(Article.userid==session.get('userid')).count()
        return count

    #我的草稿编辑
    def find_dref_id(self,articleid):
        row = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid).filter\
            (Article.hidden==0,Article.checked==1,Article.articleid==articleid).first()
        return  row

    #查询所有推荐文章
    def find_all_recommended(self):
        result = db.session.query(Article).filter(Article.recommended==1).all()
        return result

    #查询所有隐藏的文章
    def find_all_hidden(self):
        result = db.session.query(Article).filter(Article.hidden==1).all()
        return result
    #查询所有已经审核文章
    def find_all_checked(self):
        result = db.session.query(Article).filter(Article.checked==1).all()
        return result
    #我的投稿编辑
    def find_caogao_id(self,articleid):
        row = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid).filter\
            (Article.hidden==0,Article.checked==0,Article.articleid==articleid).first()
        return  row
    def find_by_caogao(self,articleid):
        row = db.session.query(Article,User.nickname).join(User,User.userid==Article.userid).filter\
            (Article.hidden==0,Article.drafted==0,Article.checked==0,Article.articleid==articleid).first()
        return  row








from utility import model_join_list
class Comment(db.Model):#用户评论表
    __tablename__='comment'#userid\articleid为外键
    commentid = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    articleid = db.Column(db.Integer, db.ForeignKey('article.articleid'))
    content = db.Column(db.Text, nullable=False)#评论内容
    replyid = db.Column(db.Integer,nullable=False,default=0)
    agreecount = db.Column(db.Integer,nullable=False,default=0)#赞同该评论的数量
    opposecount = db.Column(db.Integer,nullable=False,default=0)#赞同该评论的数量
    hidden = db.Column(db.Integer, nullable=False,default=0)  # 文章是否被隐藏，默认为0，不隐藏
    createtime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updatetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    opinion = db.relationship('Opinion', backref='comment')

    #新增评论
    def insert_comment(self,articleid,content):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'),articleid=articleid,content=content,createtime=now,updatetime=now)
        db.session.add(comment)
        db.session.commit()
        print(now)


    #根据文章编号查询所有评论
    def find_by_articleid(self,articleid):
        result = db.session.query(Comment).filter_by(articleid=articleid,hidden=0).all()
        return result

    #根据用户ID和日期查询是否已经超过每天只能发表的评论限制
    def check_limit_per_5(self):
        start = time.strftime('%Y-%m-%d %H:%M:%S')
        end = time.strftime('%Y-%m-%d 23:59:59')
        result =db.session.query(Comment).filter(Comment.userid==session.get('userid'),Comment.createtime.between(start,end)).all()
        if len(result)>=5:
            return True
        else:
            return False

    #查询评论与用户信息，评论也分页处理
    def find_limit_with_user(self,articledid,start,count):
        result = db.session.query(Comment,User).join(User,User.userid==Comment.userid).\
            filter(Comment.articleid==articledid,Comment.hidden==0).order_by(Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    def insert_reply(self,articleid,commentid,content):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(userid=session.get('userid'),articleid=articleid,content=content,replyid=commentid,createtime=now,updatetime=now)
        db.session.add(comment)
        db.session.commit()


    #查询原始评论与对应的用户信息
    def find_comment_with_user(self,articleid,start,count):
        result=db.session.query(Comment,User).join(User,User.userid==Comment.userid).filter\
            (Comment.articleid==articleid,Comment.hidden==0,Comment.replyid==0).order_by\
            (Comment.commentid.desc()).limit(count).offset(start).all()
        return result

    #查询回复评论
    def find_reply_with_user(self,replyid):
        result = db.session.query(Comment,User).join(User,User.userid==Comment.userid).\
            filter(Comment.replyid==replyid,Comment.hidden==0).all()
        return result

    #根据原始评论和回复评论生成一个关联列表
    def get_comment_user_list(self,articleid,start,count):
        result = self.find_comment_with_user(articleid,start,count)
        comment_list = model_join_list(result)
        print(comment_list)
        for comment in comment_list:
            #查询原始评论对应的回复评论，将其转换为列表并保存到comment_list
            result = self.find_reply_with_user(comment['commentid'])
            comment['reply_list']=model_join_list(result)
        return comment_list

    #查询某篇文章的原始评论数
    def get_count_by_article(self,articleid):
        count=db.session.query(Comment).filter_by(articleid=articleid,hidden=0,replyid=0).count()
        return count

    def hide_comment(self,commentid):
        #如果评论已经有了回复，且回复未全部隐藏，则不接受隐藏操作
        #返回fail表示不满足隐藏条件，隐藏成功时返done
        result = db.session.query(Comment).filter_by(replyid=commentid,hidden=0).all()
        if len(result)>0:
            return 'Fail'
        else:
            row = db.session.query(Comment).filter_by(commentid=commentid).first()
            row.hidden=1
            db.session.commit()
            return 'Done'


    #根据评论ID查询文章ID和评论者ID
    def find_article_commenter_by_id(self,commentid):
        row = db.session.query(Comment).filter_by(commentid=commentid).first()
        articleid = row.articleid
        commenterid = row.userid
        return articleid,commenterid

    #更新用户的点赞数量
    def update_agreee_oppose(self,commentid,type):
        row = db.session.query(Comment).filter_by(commentid=commentid).first()
        if type == 1:
            row.agreecount +=1
        elif type ==0 :
            row.opposecount +=1
        db.session.commit()

    def hide_comment(self,commentid):
        result = db.session.query(Comment).filter_by(replyid=commentid,hidden=0).all()
        if len(result)>0:
            return 'Fail'
        else:
            row = db.session.query(Comment).filter_by(commentid=commentid).first()
            row.hidden=1
            db.session.commit()
            return 'Done'
    #根据用户userid查询评论
    def find_by_userid(self):
        result = db.session.query(Comment).filter(Comment.userid==session.get('userid')).all()
        return result

    #获取所有评论
    def find_all_comment(self):
        result = db.session.query(Comment).join(Article,Article.articleid==Comment.articleid).\
            order_by(Comment.commentid.asc()).all()
        print(result)
        return result

    # result = db.session.query(Article, User.nickname).join(User, User.userid == Article.userid) \
    #     .order_by(Article.articleid.asc()).limit(count).offset(start).all()
    # return result





class Favorite(db.Model):
    __tablename__ = 'favorite'#文章收藏表
    # userid\articleid为外键
    favoriteid = db.Column(db.Integer,primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    articleid = db.Column(db.Integer, db.ForeignKey('article.articleid'))
    canceled = db.Column(db.Integer,nullable=False,default=0) #文章是否被取消收藏默认为0，不取消收藏
    createtime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updatetime = db.Column(db.DateTime, nullable=False, default=datetime.now())

    #插入文章收藏数据
    def insert_favorite(self,articleid):
        row = db.session.query(Favorite).filter_by(articleid=articleid,userid=session.get('userid')).first()

        if row is not None:
            row.canceled = 0
        else:
            now = time.strftime('%Y-%m-%d %H:%M:%S')

            favorite = Favorite(articleid=articleid,userid=session.get('userid'),\
                                canceled = 0,createtime = now,updatetime=now)

            db.session.add(favorite)
        db.session.commit()


    #取消文章收藏
    def cancel_favorite(self,articleid):
        row = db.session.query(Favorite).filter_by(articleid=articleid,userid=session.get('userid')).first()
        row.canceled=1
        db.session.commit()


    #判断文章是否已经被收藏
    def check_favorite(self,articleid):
        row = db.session.query(Favorite).filter_by(articleid=articleid,userid=session.get('userid')).first()
        if row is None:
            return  False
        elif row.canceled==1:
            return False
        else:
            return True

    #为用户中心查询我的收藏
    def find_my_favorite(self):
        result = db.session.query(Favorite,Article).join(Article,Favorite.articleid==Article.articleid).\
            filter(Favorite.userid==session.get('userid')).all()
        return result

    #切换收藏和取消收藏状态
    def switch_favorite(self,favoriteid):
        row = db.session.query(Favorite).filter_by(favoriteid=favoriteid).first()
        if row.canceled==1:
            row.canceled=0
        else:
            row.canceled=1
        db.session.commit()
        return row.canceled

 # 查询所有收藏
    def find_all_favorite(self):
        result = db.session.query(Favorite, Article).join(Article, Favorite.articleid == Article.articleid).all()
        return result




class Opinion(db.Model):
    __tablename__ = 'opinion'#点赞记录表
    opinionid = db.Column(db.Integer, primary_key=True)
    commentid = db.Column(db.Integer, db.ForeignKey('comment.commentid'))
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'))
    type= db.Column(db.Integer, nullable=False)
    createtime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updatetime = db.Column(db.DateTime, nullable=False, default=datetime.now())

    # 插入点赞记录
    def insert_opinion(self,commentid,type):
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        if session.get('userid') is None:
            userid=0
        else:
            userid = session.get('userid')
        opinion = Opinion(commentid=commentid,userid=userid,type=type,createtime=now,updatetime=now)
        db.session.add(opinion)
        db.session.commit()

    def check_opinion(self,commentid):
        is_checked=False
        if session.get('userid') is None:
            result = db.session.query(Opinion).filter_by(commentid=commentid).all()
            if len(result) > 0:
                is_checked=True
        else:
            userid = session.get('userid')
            result = db.session.query(Opinion).filter_by(commentid=commentid,userid=userid).all()
            if len(result)>0:
                is_checked=True
        return is_checked


