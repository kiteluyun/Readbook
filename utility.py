import re,time

from flask import Blueprint,render_template,make_response,session,request
from moldes import User
import random,string
from io import BytesIO
# 导入Python Imaging Library（PIL）中的三个模块：Image用于处理图像，ImageDraw用于在图像上绘制图形，ImageFont用于处理字体。
from PIL import Image,ImageDraw,ImageFont
# Python中用于创建文本类型的MIME对象的模块。MIME（Multipurpose Internet Mail Extensions）是一种在电子邮件中传输文本、图像、音频、视频等多媒体数据的标准。
from email.mime.text import MIMEText
# Header类用于处理MIME标头
from email.header import Header
# Python的smtplib模块中的SMTP_SSL类。SMTP_SSL类是smtplib模块中用于处理SMTPS（SMTP over SSL）协议的类。
from smtplib import SMTP_SSL

#生成图片验证码
class ImageCode:
    def rand_color(self):
        # 随机生成数字
        red = random.randint(32,127)
        green = random.randint(25, 188)
        blue = random.randint(32,127)
        return red,green,blue


    #生成四位随机数字
    def gen_text(self):
        # string.ascii_letters大小写、string.digits 0~9
        str = random.sample(string.ascii_letters+string.digits,4)
        return ''.join(str)

    #生成一些干扰线
    def draw_lines(self,draw,num,width,height):
        """
            绘制干扰线
            :param draw: 图片对象
            :param num: 干扰线数量
            :param width: 图片的宽
            :param height: 图片的高
            :return:
        """
        for num in range(num):
            x1=random.randint(0,width/2)
            y1=random.randint(0,height/2)
            x2=random.randint(0,width)
            y2=random.randint(height/2,height)
            # draw.line()是Python中的PIL（PythonImagingLibrary）模块中的一个函数，用于在图像上绘制直线。
            # 此函数接受一个参数，即表示直线端点的元组。例如(x1, y1, x2, y2)，分别表示直线的起始点和终点的
            draw.line(((x1,y1),(x2,y2)),fill='black',width=2)

    #绘制验证码图片
    def draw_verify_code(self):
        code = self.gen_text()
        width,height=120,50
        im=Image.new('RGB',(width,height),'white')# 创建图片对象，并设定背景色为白色
        font = ImageFont.truetype(font='arial.ttf',size=40) # 选择使用何种字体及字体大小
        draw = ImageDraw.Draw(im) # 新建ImageDraw对象
        #绘制字符串
        for i in range(4):
            draw.text((5+random.randint(-3,3)+23*i,5+random.randint(-3,3)),text=code[i],fill=self.rand_color(),font=font)
        #绘制干扰线
        self.draw_lines(draw,2,width,height)
        # im.show()
        return im,code
    #获取图片
    def get_code(self):
        image,code=self.draw_verify_code()
        buf=BytesIO()
        image.save(buf,'jpeg')
        bstring = buf.getvalue()#获取图片字节码
        return code,bstring#返回验证码的字符串和字节码内容




utility = Blueprint('utility',__name__)
@utility.route('/vcode')
def vcode():
    code,bstring=ImageCode().get_code()
    #创建响应对象
    responese = make_response(bstring)
    responese.headers['Content-Type']='image/jpeg'
    session['vcode']=code.lower()
    return responese







def send_email(receiver,ecode):
    sender = 'luyun <2216828801@qq.com>'
    content = f'<br/>欢迎登录账号：你的邮箱验证码为：' \
              f'<h1><span style="color:red;font-size:20px;">{ecode}</span></h1>,请复制到注册页面完成注册，感谢你的支持'
    message = MIMEText(content,'html','utf-8')
    message['Subject']=Header('注册验证码','utf-8')
    message['From']=sender
    message['To']=receiver
    # 创建一个SMTP(SimpleMailTransferProtocol) 对象, 用于通过SSL(SecureSocketsLayer) 协议连接到QQ的SMTP服务器smtp.qq.com。
    smtpObj = SMTP_SSL('smtp.qq.com')
    # 一个使用SMTP协议登录到邮箱服务器的方法。其中，user参数是邮箱地址，password参数是登录密码。
    smtpObj.login(user='2216828801@qq.com',password='epwfhdnvgnixdjge')
    smtpObj.sendmail(sender,receiver,str(message))
    smtpObj.quit()

# import string
# import random
#随机生成6为数字
def gen_email_code():
    #str1 = string.ascii_letters  # 返回26个英文大小写字母的字符串
    #str2 = string.digits  # 返回阿拉伯数字的字符串
    str=random.sample(string.digits,6)
    return ''.join(str)

@utility.route('/ecode',methods=['POST'])
def ecode():
    email = request.form.get('email')
    if not re.match("[\w]{6,10}@(163|126|qq).com",email):
        return 'email-invalid'
    code=gen_email_code()
    try:
        send_email(email,code)
        session['ecode']=code.lower()
        return 'send-pass'
    except:
        return 'send-fail'







def model_join_list(result):
    list=[]
    for obj1,obj2 in result:
        dict={}
        for k1,v1 in obj1.__dict__.items():
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dict:
                    dict[k1]=v1
        for k2,v2 in obj2.__dict__.items():
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dict:
                    dict[k2]=v2
        list.append(dict)
    return list



# 压缩图片，通过参数width指定压缩后的图片大小
def compress_image(source, dest, width):
    from PIL import Image
    # 如果图片宽度大于1200，则调整为1200的宽度
    im = Image.open(source)
    x, y = im.size      # 获取源图片的宽和高
    if x > width:
        # 等比例缩放
        ys = int(y * width / x)
        xs = width
        # 调整当前图片的尺寸（同时也会压缩大小）
        temp = im.resize((xs, ys), Image.ANTIALIAS)
        # 将图片保存并使用80%的质量进行压缩
        temp.save(dest, quality=80)
    # 如果尺寸小于指定宽度则不缩减尺寸，只压缩保存
    else:
        im.save(dest, quality=80)

# 解析文章内容中的图片地址
def parse_image_url(content):
    import re
    temp_list = re.findall('<img src="(.+?)"', content)
    url_list = []
    for url in temp_list:
        # 如果图片类型为gif，则直接跳过，不对其作任何处理
        if url.lower().endswith('.gif'):
            continue
        url_list.append(url)
    return url_list

# 远程下载指定URL地址的图片，并保存到临时目录中
def download_image(url, dest):
    import requests
    response = requests.get(url)  # 获取图片的响应
    # 将图片以二进制方式保存到指定文件中
    with open(file=dest, mode='wb') as file:
        file.write(response.content)

# 解析列表中的图片URL地址并生成缩略图，返回缩略图名称
def generate_thumb(url_list):
    # 根据URL地址解析出其文件名和域名
    # 通常建议使用文章内容中的第一张图片来生成缩略图
    # 先遍历url_list，查找里面是否存在本地上传图片，找到即处理，代码运行结束
    for url in url_list:
        if url.startswith('/upload/'):
            filename = url.split('/')[-1]
            # 找到本地图片后对其进行压缩处理，设置缩略图宽度为400像素即可
            compress_image('./resource/upload/' + filename,
                           './resource/thumb/' + filename, 400)
            return filename

    # 如果在内容中没有找到本地图片，则需要先将网络图片下载到本地再处理
    # 直接将第一张图片作为缩略图，并生成基于时间戳的标准文件名
    url = url_list[0]
    filename = url.split('/')[-1]
    suffix = filename.split('.')[-1]    # 取得文件的后缀名
    thumbname = time.strftime('%Y%m%d_%H%M%S.' + suffix)
    download_image(url, './resource/download/' + thumbname)
    compress_image('./resource/download/' + thumbname, '../resource/thumb/' + thumbname, 400)

    return thumbname  # 返回当前缩略图的文件名
