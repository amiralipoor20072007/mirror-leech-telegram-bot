from os import path as ospath, listdir, rename, makedirs
from requests import post as rpost
from shutil import move

from bot import Interval, aria2, DOWNLOAD_DIR, download_dict, download_dict_lock, LOGGER, DATABASE_URL, config_dict, status_reply_dict_lock
from bot.helper.ext_utils.bot_utils import get_readable_file_size
from bot.helper.ext_utils.fs_utils import get_path_size
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.mirror_utils.status_utils.split_status import SplitStatus


class MirrorLeechListener:
    def __init__(self, bot,ServerHash:str,Chat_id:str, isZip=False, extract=False, isQbit=False, isLeech=False, pswd=None, tag=None, select=False, seed=False, sameDir={}):
        self.bot = bot
        self.Hash = ServerHash
        self.chat_id = Chat_id
        self.extract = extract
        self.isZip = isZip
        self.isQbit = isQbit
        self.isLeech = isLeech
        self.pswd = pswd
        self.tag = tag
        self.seed = seed
        self.newDir = ""
        self.dir = f"{DOWNLOAD_DIR}{self.chat_id}"
        self.select = select
        self.isPrivate = True
        self.suproc = None
        self.queuedUp = False
        self.sameDir = sameDir

    def clean(self):
        try:
            with status_reply_dict_lock:
                Interval[0].cancel()
                Interval.clear()
            aria2.purge()
            # delete_all_messages()
        except:
            pass

    def onDownloadStart(self):
        if not self.isPrivate and config_dict['INCOMPLETE_TASK_NOTIFIER'] and DATABASE_URL:
            DbManger().add_incomplete_task(self.message.chat.id, self.message.link, self.tag)

    def onDownloadComplete(self):
        with download_dict_lock:
            if len(self.sameDir) > 1:
                self.sameDir.remove(self.Hash)
                folder_name = listdir(self.dir)[-1]
                path = f"{self.dir}/{folder_name}"
                des_path = f"{DOWNLOAD_DIR}{list(self.sameDir)[0]}/{folder_name}"
                makedirs(des_path, exist_ok=True)
                for subdir in listdir(path):
                    sub_path = f"{self.dir}/{folder_name}/{subdir}"
                    if subdir in listdir(des_path):
                        sub_path = rename(sub_path, f"{self.dir}/{folder_name}/1-{subdir}")
                    move(sub_path, des_path)
                del download_dict[self.Hash]
                return
            download = download_dict[self.Hash]
            self.name = name = str(download.name()).replace('/', '')
            gid = download.gid()
        LOGGER.info(f"Download completed: {name}")
        if name == "None" or self.isQbit or not ospath.exists(f"{self.dir}/{name}"):
            self.name = name = listdir(self.dir)[-1]
        m_path = f"{self.dir}/{self.name}"
        size = get_path_size(m_path)
        size_str = get_readable_file_size(size)
        LOGGER.info(f'{m_path}')
        # rpost('http://masteryxi.ga:2052',json={'Hash':self.Hash,'Link':f'http://45.159.149.18/{self.chat_id}/{name}','Size':size_str})
        self.upload(m_path,size,size_str)

    def onDownloadError(self, error):
        rpost('http://masteryxi.ga:2052',json={'Hash':self.Hash,'text':error,'sendMessage':True})
        self.TaskCompleted()

    def TaskCompleted(self):
        with download_dict_lock:
            if self.Hash in download_dict.keys():
                del download_dict[self.Hash]


    def upload(self,path,size,size_str):
        with download_dict_lock:
            download_dict[self.Hash] = SplitStatus(self.name, size, self.Hash,self)
        upload = rpost('https://api.bayfiles.com/upload', files = {'file': open(path,'rb')})
        link = upload.json()["data"]["file"]["url"]["full"]
        self.onUploadComplete(size_str,link)

    def onUploadComplete(self,size,link):
        rpost('http://masteryxi.ga:2052',json={'Hash':self.Hash,'Link':link,'Size':size})
        self.TaskCompleted()

        '''
        if not self.isPrivate and config_dict['INCOMPLETE_TASK_NOTIFIER'] and DATABASE_URL:
            DbManger().rm_complete_task(self.message.link)
        msg = f"<b>Name: </b><code>{escape(name)}</code>\n\n<b>Size: </b>{size}"
        if self.isLeech:
            msg += f'\n<b>Total Files: </b>{folders}'
            if typ != 0:
                msg += f'\n<b>Corrupted Files: </b>{typ}'
            msg += f'\n<b>cc: </b>{self.tag}\n\n'
            if not files:
                sendMessage(msg, self.bot, self.message)
            else:
                fmsg = ''
                for index, (link, name) in enumerate(files.items(), start=1):
                    fmsg += f"{index}. <a href='{link}'>{name}</a>\n"
                    if len(fmsg.encode() + msg.encode()) > 4000:
                        sendMessage(msg + fmsg, self.bot, self.message)
                        sleep(1)
                        fmsg = ''
                if fmsg != '':
                    sendMessage(msg + fmsg, self.bot, self.message)
            if self.seed:
                if self.newDir:
                    clean_target(self.newDir)
                with queue_dict_lock:
                    if self.uid in non_queued_up:
                        non_queued_up.remove(self.uid)
                return
        else:
            msg += f'\n\n<b>Type: </b>{typ}'
            if typ == "Folder":
                msg += f'\n<b>SubFolders: </b>{folders}'
                msg += f'\n<b>Files: </b>{files}'
            msg += f'\n\n<b>cc: </b>{self.tag}'
            buttons = ButtonMaker()
            buttons.buildbutton("☁️ Drive Link", link)
            LOGGER.info(f'Done Uploading {name}')
            if INDEX_URL:= config_dict['INDEX_URL']:
                url_path = rutils.quote(f'{name}')
                share_url = f'{INDEX_URL}/{url_path}'
                if typ == "Folder":
                    share_url += '/'
                    buttons.buildbutton("⚡ Index Link", share_url)
                else:
                    buttons.buildbutton("⚡ Index Link", share_url)
                    if config_dict['VIEW_LINK']:
                        share_urls = f'{INDEX_URL}/{url_path}?a=view'
                        buttons.buildbutton("🌐 View Link", share_urls)
            sendMessage(msg, self.bot, self.message, buttons.build_menu(2))
            if self.seed:
                if self.isZip:
                    clean_target(f"{self.dir}/{name}")
                elif self.newDir:
                    clean_target(self.newDir)
                with queue_dict_lock:
                    if self.uid in non_queued_up:
                        non_queued_up.remove(self.uid)
                return
        clean_download(self.dir)
        with download_dict_lock:
            if self.uid in download_dict.keys():
                del download_dict[self.uid]
            count = len(download_dict)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        with queue_dict_lock:
            if self.uid in non_queued_up:
                non_queued_up.remove(self.uid)

        start_from_queued()

    def onUploadError(self, error):
        clean_download(self.dir)
        if self.newDir:
            clean_download(self.newDir)
        with download_dict_lock:
            if self.uid in download_dict.keys():
                del download_dict[self.uid]
            count = len(download_dict)
            if self.uid in self.sameDir:
                self.sameDir.remove(self.uid)
        sendMessage(f"{self.tag} {escape(error)}", self.bot, self.message)
        if count == 0:
            self.clean()
        else:
            update_all_messages()

        if not self.isPrivate and config_dict['INCOMPLETE_TASK_NOTIFIER'] and DATABASE_URL:
            DbManger().rm_complete_task(self.message.link)

        with queue_dict_lock:
            if self.uid in queued_up:
                del queued_up[self.uid]
            if self.uid in non_queued_up:
                non_queued_up.remove(self.uid)

        self.queuedUp = False
        start_from_queued()'''
