'''
get line notify https://notify-bot.line.me/my/

'''
import requests,json
import urllib.parse

#token สำหรับส่งข้อความเข้า line กลุ่ม
LINE_ACCESS_TOKEN="9CD4rqw9Q2Hagu7fopCwWwPeNNHsqBS2yFuXuQoGJIS"
url = "https://notify-api.line.me/api/notify"




def sendMessage(message):
    if message:
        msg = urllib.parse.urlencode({"message": message})
        LINE_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded',
                        "Authorization": "Bearer " + LINE_ACCESS_TOKEN}
        session = requests.Session()
        a = session.post(url, headers=LINE_HEADERS, data=msg)
        print(a.text)

