# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: handle.py

@time: 2017/12/19 20:58

@desc:

"""
import hashlib
import web
from KB_wechat import receive
from KB_wechat import reply


class Handle(object):
    def GET(self):
        try:
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "cadalbns"

            configure_list = [token, timestamp, nonce]
            configure_list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, configure_list)
            hashcode = sha1.hexdigest()
            print("handle/GET func: hashcode, signature: ", hashcode, signature)
            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception as Argument:
            return Argument

    def POST(self):
        try:
            webData = web.data()
            # print("Handle Post webdata is ", webData)
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName

                # TODO 处理用户发来的文本消息
                if recMsg.MsgType == 'text':
                    if recMsg.Content == '1':
                        status = web.config.recorder.dump_wrong_record(user_id=toUser)
                        if status == 'success':
                            content = '感谢您的反馈！'
                        else:
                            content = '最近你没有问我什么问题呢~'
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    else:
                        status, sparql, content, approach_type = web.config.query.get_response(recMsg.Content)
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        web.config.recorder.dump_to_mongodb(status=status,
                                                     sparql=sparql,
                                                     question=recMsg.Content,
                                                     answer=content,
                                                     user_id=toUser,
                                                     approach_type=approach_type)
                        # print('User:{0}\nQuestion:{1}\nAnswer:{2}\n\n\n'.format(toUser, recMsg.Content, content))
                        return replyMsg.send()

                elif recMsg.MsgType == 'image':
                    mediaId = recMsg.MediaId
                    replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                    return replyMsg.send()
                elif recMsg.MsgType == 'event':
                    if recMsg.Event == 'subscribe':
                        content = '你好！我是CADAL小书虫，对中国古代编年史略有研究。你可以问我古代人物的基本信息，亲属关系，非亲属关系，作品，职位等相关问题。\n\n' \
                                  '例如：\n' \
                                  '1. 李白是什么时候出生的？\n' \
                                  '2. 欧阳修有几个儿子？\n' \
                                  '3. 苏轼的爸爸是谁？\n' \
                                  '4. 李世民的谥号是什么？\n' \
                                  '5. 朱元璋去过什么地方？\n' \
                                  '6. 周敦颐的籍贯在哪？\n' \
                                  '7. 朱棣活了多久？\n' \
                                  '8. 纳兰性德是哪个民族的？\n' \
                                  '9. 关汉卿是哪个朝代的？\n' \
                                  '10. 杜甫当过什么官？\n' \
                                  '11. 韩愈在哪当的府尹？\n' \
                                  '12. 黄庭坚有什么作品？\n' \
                                  '13. 司马懿的职业是什么？\n' \
                                  '14. 柳宗元是怎么入仕的？\n' \
                                  '15. 白居易认识哪些人？\n' \
                                  '16. 李商隐和白居易是什么关系？\n' \
                                  '17. 哪些人和欧阳修是朋友关系？\n\n\n' \
                                  '如果你认为我的答案是错误的(指答非所问，答案不全不算错误)，请输入数字1，帮助我及时纠正。'
                        replyMsg = reply.TextMsg(toUser, fromUser, content)
                        return replyMsg.send()
                    else:
                        return reply.Msg().send()
                else:
                    print(recMsg.MsgType)
                    return reply.Msg().send()
            else:
                print("暂且不处理")
                return reply.Msg().send()
        except Exception as Argment:
            return Argment


class QA:
    def GET(self):
        data = web.input()
        client_ip = web.ctx['ip']
        question = data['question']
        status, sparql, content, approach_type = web.config.query.get_response(question)
        web.config.recorder.dump_to_mongodb(status=status, sparql=sparql, question=question, answer=content,
                                            user_id=client_ip, approach_type=approach_type)
        return content


class FeedBack:
    def GET(self):
        client_ip = web.ctx['ip']
        web.config.recorder.dump_wrong_record(user_id=client_ip)
