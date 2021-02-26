"""

啟用伺服器基本樣板

"""
# 1-引用套件

# 引用Web Server套件
from flask import Flask, request, abort

# 從 lineBot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json

# 引入所需要的消息與模板消息
from linebot.models import (
    MessageEvent, TemplateSendMessage, PostbackEvent
)
import boto3

# 伺服器準備
import os
from os import environ

# 將消息模型，文字收取消息與文字寄發消息 引入
from linebot.models import (
    TextMessage, TextSendMessage, ImageSendMessage
)

from linebot.models.events import FollowEvent

secretFileContentJson = json.load(open("./line_secret_key", 'r', encoding="utf-8"))
server_url = secretFileContentJson.get("server_url")
# 準備好溝通用的組件, handler, line_bot_api, app
# 設定Server啟用細節
app = Flask(__name__, static_url_path="/images", static_folder="../images/")

# app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# 創建 s3 客戶端
# from environment import keys
AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = environ['AWS_SECRET_ACCESS_KEY']

# build aws s3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# =============================================================================================================
# 業務方法編寫

# # 刪除圖文選單
# line_bot_api.delete_rich_menu('richmenu-6048f6a1f4289de5bb7f79ecdbfacbab')
#
# 看有多少圖文選單ID
# rich_menu_list = line_bot_api.get_rich_menu_list()
# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)


# FOLLOW

'''

製作文字與圖片的教學訊息

'''

# 消息清單
reply_message_list = [
    TextSendMessage(text="你知道 #MeToo 嗎 ?"),
    ImageSendMessage(
        original_content_url="https://api.time.com/wp-content/uploads/2018/03/screen-shot-2018-03-12-at-10-50-51-am.png",
        preview_image_url="https://issat.dcaf.ch/var/ezwebin_site/storage/images/issat2/share/blogs/issat-blog/how-the-metoo-movement-highlights-the-need-for-security-sector-reform-in-the-global-north/2843788-8-eng-GB/How-the-MeToo-Movement-Highlights-the-Need-for-Security-Sector-Reform-in-the-Global-North.jpg"),
    TextSendMessage(
        text="「#MeToo」是在 2017年始自美國，但旋即席捲全球的反性侵及性騷擾社會運動。\n\n「#MeToo」運動有四大特點：\n\n第一，性侵及性騷擾倖存者以實名分享自己的故事及作出指控；\n\n第二，「#MeToo」是以媒體，一種被社會公認為第四公權力的平台，作為主要申訴渠道；"
    ),
    TextSendMessage(
        text="第三，「#MeToo」是因着對現存制度不滿， 而希望透過制度外的行動，從而喚醒社會對性侵及性騷擾的關注及討論，取得公義及推動改革；\n\n第四，「#MeToo」和一般社會運動不一樣，並沒有任何組織，多是由個別性侵或性騷擾倖存者透過社交媒體自發分享自己的故事。"
    )
]
'''
    ，
    撰寫用戶關注時，我們要處理的商業邏輯
    ，
    1. 取得用戶個資，並存回伺服器
    2. 把先前製作好的自定義菜單，與用戶做綁定
    3. 回應用戶，歡迎用的文字消息與圖片消息
    
    '''

# 載入Follow事件

rich_menu_list = line_bot_api.get_rich_menu_list()


# 告知handler，如果收到FollowEvent，則做下面的方法處理
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)

    # 將用戶資訊存在檔案內
    with open("./user.txt", "a") as myfile:
        myfile.write(json.dumps(vars(user_profile), sort_keys=True))
        myfile.write('\r\n')

    # 綁定首頁圖文選單
    line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_list[0].rich_menu_id)

    # 回覆文字消息與圖片消息
    line_bot_api.reply_message(
        event.reply_token,
        reply_message_list
    )


# ===================================================================================================================
'''
Button篇
    設定模板消息，指定其參數細節。

'''
# MYTH ----------------------------------------------
# 性騷擾前言
with open("./Myth/first.json", encoding="utf-8") as first:
    text_message1 = json.load(first)
reply_send_message13 = TextSendMessage.new_from_json_dict(text_message1)
# 性侵害前言
with open("./Myth/second.json", encoding="utf-8") as second:
    text_message2 = json.load(second)
reply_send_message14 = TextSendMessage.new_from_json_dict(text_message2)

# 1
with open("Myth/reply1.json", encoding="utf-8") as f1:
    confirm_template_message1 = json.load(f1)
reply_send_message1 = TemplateSendMessage.new_from_json_dict(confirm_template_message1)
# 2
with open("Myth/reply2.json", encoding="utf-8") as f2:
    confirm_template_message2 = json.load(f2)
reply_send_message2 = TemplateSendMessage.new_from_json_dict(confirm_template_message2)
# 3
with open("Myth/reply3.json", encoding="utf-8") as f3:
    confirm_template_message3 = json.load(f3)
reply_send_message3 = TemplateSendMessage.new_from_json_dict(confirm_template_message3)
# 4
with open("Myth/reply4.json", encoding="utf-8") as f4:
    confirm_template_message4 = json.load(f4)
reply_send_message4 = TemplateSendMessage.new_from_json_dict(confirm_template_message4)
# 5
with open("Myth/reply5.json", encoding="utf-8") as f5:
    confirm_template_message5 = json.load(f5)
reply_send_message5 = TemplateSendMessage.new_from_json_dict(confirm_template_message5)
# 6
with open("Myth/reply6.json", encoding="utf-8") as f6:
    confirm_template_message6 = json.load(f6)
reply_send_message6 = TemplateSendMessage.new_from_json_dict(confirm_template_message6)
# 7
with open("Myth/reply7.json", encoding="utf-8") as f7:
    confirm_template_message7 = json.load(f7)
reply_send_message7 = TemplateSendMessage.new_from_json_dict(confirm_template_message7)
# 8
with open("Myth/reply8.json", encoding="utf-8") as f8:
    confirm_template_message8 = json.load(f8)
reply_send_message8 = TemplateSendMessage.new_from_json_dict(confirm_template_message8)
# 9
with open("Myth/reply9.json", encoding="utf-8") as f9:
    confirm_template_message9 = json.load(f9)
reply_send_message9 = TemplateSendMessage.new_from_json_dict(confirm_template_message9)
# 10
with open("Myth/reply10.json", encoding="utf-8") as f10:
    confirm_template_message10 = json.load(f10)
reply_send_message10 = TemplateSendMessage.new_from_json_dict(confirm_template_message10)
# End
text_message3 = TextSendMessage(text="問題已結束 !")
# -------------------------------------------------------------------------------------------------

# MeToo 輪播事件

with open("./CarouselTemplate.json", encoding="utf-8") as f:
    carousel_template_message = json.load(f)
reply_send_message11 = TemplateSendMessage.new_from_json_dict(carousel_template_message)
# -----------------------------------------------------------------------------------------------------

# 專業諮詢

with open("./prohelp.json", encoding="utf-8") as p:
    text_message4 = json.load(p)
reply_send_message12 = TextSendMessage.new_from_json_dict(text_message4)

'''

設計一個字典

'''
template_message_dict = {
    "我想知道性侵和性騷擾的迷思": [reply_send_message13, reply_send_message1],
    "我想知道#MeToo事件": reply_send_message11,
    "專業諮詢": reply_send_message12,
    "其實，女人並不易擺脫男人的性騷擾。主要理由是：男人的力量與地位通常大於女人，致使女人的抗拒需付出相當大的代價。": reply_send_message2,
    "沒錯，女人並不易擺脫男人的性騷擾。主要理由是：男人的力量與地位通常大於女人，致使女人的抗拒需付出相當大的代價。": reply_send_message2,
    "其實，性騷擾事件的發生率遠超過一般人的想像，大多數的人都曾有遭到性騷擾之經驗。": reply_send_message3,
    "性騷擾事件的發生率遠超過一般人的想像，大多數的人都曾有遭到性騷擾之經驗。": reply_send_message3,
    "其實，職場的性騷擾往往容易發生，又以男人性騷擾女人的比例較高。": reply_send_message4,
    "職場的性騷擾往往容易發生，又以男人性騷擾女人的比例較高。": reply_send_message4,
    "其實，絕大多數的性騷擾事件之發生皆非被害者自找的，加害者、受害者與情境都可能是要因。": reply_send_message5,
    "絕大多數的性騷擾事件之發生皆非被害者自找的，加害者、受害者與情境都可能是要因。": reply_send_message5,
    "其實，男人被性騷擾後也會出現不良影響。總之，不管男人或女人，都沒有人願意讓自己的身體遭到侵犯。": [reply_send_message14, reply_send_message6],
    "男人被性騷擾後也會出現不良影響。不管男人或女人，都沒有人願意讓自己的身體遭到侵犯。": [reply_send_message14, reply_send_message6],
    "其實，這是從男性為中心的角度去詮釋女性應順從之誤解。面對男性的霸王硬上弓，女人務必要勇敢的說不。": reply_send_message7,
    "這是從男性為中心的角度去詮釋女性應順從之誤解。面對男性的霸王硬上弓，女人務必要勇敢的說不。": reply_send_message7,
    "其實，性侵害事件也可能發生在市內，特別是自己的家中。": reply_send_message8,
    "性侵害事件也可能發生在市內，特別是自己的家中。": reply_send_message8,
    "其實，性侵害的強暴犯也可能是自己熟悉的人。": reply_send_message9,
    "性侵害的強暴犯也可能是自己熟悉的人。": reply_send_message9,
    "其實，這並非男性無法控制情慾的藉口，而是男性放縱自我情慾與不尊重女性自主權之結果。": reply_send_message10,
    "這並非男性無法控制情慾的藉口，而是男性放縱自我情慾與不尊重女性自主權之結果。": reply_send_message10,
    "其實，這是一種指責性侵害受害者之觀點，而將所有責任歸咎於受害者的穿著。": text_message3,
    "這是一種指責性侵害受害者之觀點，而將所有責任歸咎於受害者的穿著。": text_message3,
    "返回": TextSendMessage(text="上一頁"),
    "我想認識#MeToo": TextSendMessage(text="下一頁")
}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        template_message_dict.get(event.message.text)
    )


# 切換圖文選單
# [0]是選單1
# [1]是選單2
@handler.add(PostbackEvent)
def handle_post_message(event):
    print(event.postback.data)
    user_profile = line_bot_api.get_profile(event.source.user_id)
    if "rich_menu2" in event.postback.data:
        line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_list[1].rich_menu_id)
    elif "backtomenu" in event.postback.data:
        line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_list[0].rich_menu_id)
    elif "需要性平教育" in event.postback.data:
        with open("./sexual harassment.txt", "a") as s:
            s.write(json.dumps(vars(user_profile), sort_keys=True))
            s.write('\r\n')
    elif "很需要性平教育" in event.postback.data:
        with open("./sexual assault.txt", "a") as s1:
            s1.write(json.dumps(vars(user_profile), sort_keys=True))
            s1.write('\r\n')
    else:
        pass

# 啟動伺服器

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])

# ngrok.exe http 5000 -region ap
