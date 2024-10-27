import json
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *
from zlapi import Message, ThreadType, Mention, MessageStyle, MultiMsgStyle, MessageReaction
import time
from datetime import datetime
import threading

def ThanhNgocLoveThanhVy():
    try:
        with open('admin.json', 'r') as adminvip:
            adminzalo = json.load(adminvip)
            return set(adminzalo.get('idadmin', []))
    except FileNotFoundError:
        return set()
idadmin = ThanhNgocLoveThanhVy()

def save_group_ids(group_ids):
    with open('group.json', 'w') as group_file:
        json.dump({"group_ids": group_ids}, group_file, indent=4)

def load_mutenguoidung():
    try:
        with open('mute.json', 'r') as mute_file:
            data = json.load(mute_file)
            if isinstance(data, dict):
                return set(data.get('mutenguoidung', []))
            elif isinstance(data, list):
                return set(data)
            else:
                return set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_mutenguoidung(mutenguoidung):
    with open('mute.json', 'w') as mute_file:
        json.dump({'mutenguoidung': list(mutenguoidung)}, mute_file)

class ThanhNgocDzYeuThanhVy(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.isUndoLoop = False
        self.Group = False

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        list_link = ["🤫", "Mute", "Bố", "Bug"]
        try:
           if any(link in message for link in list_link):
             self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
           if "https://zalo.me/g/" in message_object.content['href']:
             self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
        except Exception as e:
            print("\033[1;36mStatus Bot Of Duong Ngoc Love Thanh Vy")
        print(f"\033[32m{message} \033[39m|\033[31m {author_id} \033[39m|\033[33m {thread_id}\033[0m\n")
        content = message_object.content if message_object and hasattr(message_object, 'content') else ""
        
        if not isinstance(message, str) and not self.isUndoLoop:
            return

        if isinstance(message, str):
            if message.startswith("!info"):
                user_id = None
                if message_object.mentions:
                    user_id = message_object.mentions[0]['uid']
                elif content[5:].strip().isnumeric():
                    user_id = content[5:].strip()
                else:
                    user_id = author_id
                user_info = self.fetchUserInfo(user_id)
                infozalo = self.checkinfo(user_id, user_info)
                self.replyMessage(Message(text=infozalo, parse_mode="HTML"), message_object, thread_id=thread_id, thread_type=thread_type)
                return

            elif message.startswith("Stop"):
                if author_id not in idadmin:
                    self.replyMessage(Message(text='🚫 Chỉ Thanh Vy 💓 Dương Ngọc Mới Được Sử Dụng.'), message_object, thread_id=thread_id, thread_type=thread_type)
                    return
                mutenguoidung = load_mutenguoidung()
                if message_object.mentions:
                    user_id = message_object.mentions[0]['uid']
                else:
                    user_id = author_id
                if user_id in mutenguoidung:
                    mutenguoidung.remove(user_id)
                    save_mutenguoidung(mutenguoidung)
                self.isUndoLoop = False
        
            elif message.startswith("Mute") or message.startswith("🤫") or message.startswith(" ") or "🤫" in message.lower():
                if author_id not in idadmin:
                    self.replyMessage(Message(text='🚫 Chỉ Thanh Vy 💓 Dương Ngọc Mới Được Sử Dụng.'), message_object, thread_id=thread_id, thread_type=thread_type)
                    return
                mutenguoidung = load_mutenguoidung()
                if message_object.mentions and len(message_object.mentions) > 0:
                    user_id = message_object.mentions[0]['uid']
                    mention = Mention(user_id, length=8, offset=12)
                    self.replyMessage(
                        Message(
                            text="Nín Họng Đi @TagName", mention=mention
                        ),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                else:
                    user_id = author_id
                    self.replyMessage(
                        Message(
                            text="Bạn Đã Tự Hủy🗿"
                        ),
                        message_object,
                        thread_id=thread_id,
                        thread_type=thread_type
                    )
                if user_id not in mutenguoidung:
                    mutenguoidung.add(user_id)
                    save_mutenguoidung(mutenguoidung)
                self.isUndoLoop = True
            elif message.startswith("Group"):
                if author_id not in idadmin:
                    return
                with open('group.json', 'r') as group_file:
                    group_config = json.load(group_file)
                    allowed_groups = set(group_config['group_ids'])
                sub_command = content.split(' ', 1)[1].strip() if len(content.split(' ', 1)) > 1 else ""
                if sub_command.lower().startswith("Add"):
                    new_group_id = sub_command[4:].strip()
                    if new_group_id and new_group_id not in allowed_groups:
                        allowed_groups.add(new_group_id)
                        save_group_ids(list(allowed_groups))
                        self.replyMessage(Message(text=f'✅ Mõm Group ID {new_group_id}'), message_object, thread_id=thread_id, thread_type=thread_type)
                        self.Group = True
                    else:
                        self.replyMessage(Message(text='🚫 Nhập ID Group Chuẩn Đi Admin Dz'), message_object, thread_id=thread_id, thread_type=thread_type)
                elif sub_command.lower().startswith("Remove"):
                    remove_group_id = sub_command[7:].strip()
                    if remove_group_id and remove_group_id in allowed_groups:
                        allowed_groups.remove(remove_group_id)
                        save_group_ids(list(allowed_groups))
                        self.replyMessage(Message(text=f'✅ Stop Mõm Group ID {remove_group_id}'), message_object, thread_id=thread_id, thread_type=thread_type)
                        self.Group = False
                    else:
                        self.replyMessage(Message(text='🚫 Nhập ID Group Chuẩn Đi Admin Dz'), message_object, thread_id=thread_id, thread_type=thread_type)
                    return
        if self.isUndoLoop:
            if author_id in idadmin:
                return
            with open('mute.json', 'r') as mute_file:
                mute_config = json.load(mute_file)
                mutenguoidung = set(mute_config['mutenguoidung'])
            if author_id in mutenguoidung:
                self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
        if self.Group:
            with open('group.json', 'r') as group_file:
                group_config = json.load(group_file)
                allowed_groups = set(group_config['group_ids'])
            if thread_type == ThreadType.GROUP and thread_id not in allowed_groups:
                return
            self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
            self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
            self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)
            self.deleteGroupMsg(msgId=message_object.msgId, clientMsgId=message_object.cliMsgId, ownerId=author_id, groupId=thread_id)

    def checkinfo(self, user_id, user_info):
        if 'changed_profiles' in user_info and user_id in user_info['changed_profiles']:
            profile = user_info['changed_profiles'][user_id]
            infozalo = f'''
<b>Tên: </b> {profile.get('displayName', '')}
<b>ID: </b> {profile.get('userId', '')}
            '''
            return infozalo
        else:
            return "Đếch Thấy Thằng Này."

imei = "9a85a056-1758-4880-9f80-045535b30247-c92baae71318dc81de51a663df2f8b4f"
session_cookies =({"__zi":"3000.SSZzejyD7zS_Wk-fXGO5s3FDehJB21sRRz-e-eSB7DKWtwt-XmjKqoJTvlo33bBL9TZc_W.1","__zi-legacy":"3000.SSZzejyD7zS_Wk-fXGO5s3FDehJB21sRRz-e-eSB7DKWtwt-XmjKqoJTvlo33bBL9TZc_W.1","_zlang":"vn","app.event.zalo.me":"8150780531193987476","zpsid":"QVkY.313334733.66.3tNTRTm3WKaH62nRq0E1IQbmythjCB9ww3IoUlPrE7enUrhftPNwKhi3WKa","zpw_sek":"SBoz.313334733.a0.En0wtvmhmNrHC6nllIl1VUS9f1Q-4UCP-dgD1_rZz0VgReX9vXkBKjfFk3VD5lnVuG6tnA_6kQOyAbS6Xqp1VG"})
ThanhNgocDzYeuThanhVy = ThanhNgocDzYeuThanhVy('api_key', 'secret_key', imei=imei, session_cookies=session_cookies)
ThanhNgocDzYeuThanhVy.listen()