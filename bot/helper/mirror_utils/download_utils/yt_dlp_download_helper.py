# from os import path as ospath, listdir
# from random import SystemRandom
# from string import ascii_letters, digits
# from logging import getLogger
# from yt_dlp import YoutubeDL, DownloadError
# from threading import RLock
# from re import search as re_search

# from bot import download_dict_lock, download_dict, config_dict, non_queued_dl, non_queued_up, queued_dl, queue_dict_lock
# from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
# from bot.helper.telegram_helper.message_utils import sendMessage, sendStatusMessage
# from ..status_utils.yt_dlp_download_status import YtDlpDownloadStatus
# from bot.helper.mirror_utils.status_utils.queue_status import QueueStatus

# LOGGER = getLogger(__name__)


# class MyLogger:
#     def __init__(self, obj):
#         self.obj = obj

#     def debug(self, msg):
#         # Hack to fix changing extension
#         if not self.obj.is_playlist:
#             if match := re_search(r'.Merger..Merging formats into..(.*?).$', msg) or \
#                         re_search(r'.ExtractAudio..Destination..(.*?)$', msg):
#                 LOGGER.info(msg)
#                 newname = match.group(1)
#                 newname = newname.rsplit("/", 1)[-1]
#                 self.obj.name = newname

#     @staticmethod
#     def warning(msg):
#         LOGGER.warning(msg)

#     @staticmethod
#     def error(msg):
#         if msg != "ERROR: Cancelling...":
#             LOGGER.error(msg)


# class YoutubeDLHelper:
#     def __init__(self, listener):
#         self.name = ""
#         self.is_playlist = False
#         self._last_downloaded = 0
#         self.__size = 0
#         self.__progress = 0
#         self.__downloaded_bytes = 0
#         self.__download_speed = 0
#         self.__eta = '-'
#         self.__listener = listener
#         self.__gid = ""
#         self.__is_cancelled = False
#         self.__downloading = False
#         self.__resource_lock = RLock()
#         self.opts = {'progress_hooks': [self.__onDownloadProgress],
#                      'logger': MyLogger(self),
#                      'usenetrc': True,
#                      'cookiefile': 'cookies.txt',
#                      'allow_multiple_video_streams': True,
#                      'allow_multiple_audio_streams': True,
#                      'noprogress': True,
#                      'allow_playlist_files': True,
#                      'overwrites': True,
#                      'trim_file_name': 200}

#     @property
#     def download_speed(self):
#         with self.__resource_lock:
#             return self.__download_speed

#     @property
#     def downloaded_bytes(self):
#         with self.__resource_lock:
#             return self.__downloaded_bytes

#     @property
#     def size(self):
#         with self.__resource_lock:
#             return self.__size

#     @property
#     def progress(self):
#         with self.__resource_lock:
#             return self.__progress

#     @property
#     def eta(self):
#         with self.__resource_lock:
#             return self.__eta

#     def __onDownloadProgress(self, d):
#         self.__downloading = True
#         if self.__is_cancelled:
#             raise ValueError("Cancelling...")
#         if d['status'] == "finished":
#             if self.is_playlist:
#                 self._last_downloaded = 0
#         elif d['status'] == "downloading":
#             with self.__resource_lock:
#                 self.__download_speed = d['speed']
#                 if self.is_playlist:
#                     downloadedBytes = d['downloaded_bytes']
#                     chunk_size = downloadedBytes - self._last_downloaded
#                     self._last_downloaded = downloadedBytes
#                     self.__downloaded_bytes += chunk_size
#                 else:
#                     if d.get('total_bytes'):
#                         self.__size = d['total_bytes']
#                     elif d.get('total_bytes_estimate'):
#                         self.__size = d['total_bytes_estimate']
#                     self.__downloaded_bytes = d['downloaded_bytes']
#                     self.__eta = d.get('eta', '-')
#                 try:
#                     self.__progress = (self.__downloaded_bytes / self.__size) * 100
#                 except:
#                     pass

#     def __onDownloadStart(self, from_queue):
#         with download_dict_lock:
#             download_dict[self.__listener.uid] = YtDlpDownloadStatus(self, self.__listener, self.__gid)
#         if not from_queue:
#             self.__listener.onDownloadStart()
#             sendStatusMessage(self.__listener.message, self.__listener.bot)
#             LOGGER.info(f'Download with YT_DLP: {self.name}')
#         else:
#             LOGGER.info(f'Start Queued Download with YT_DLP: {self.name}')

#     def __onDownloadComplete(self):
#         self.__listener.onDownloadComplete()

#     def __onDownloadError(self, error):
#         self.__is_cancelled = True
#         self.__listener.onDownloadError(error)

#     def extractMetaData(self, link, name, args, get_info=False):
#         if args:
#             self.__set_args(args)
#         if get_info:
#             self.opts['playlist_items'] = '0'
#         if link.startswith(('rtmp', 'mms', 'rstp')):
#             self.opts['external_downloader'] = 'ffmpeg'
#         with YoutubeDL(self.opts) as ydl:
#             try:
#                 result = ydl.extract_info(link, download=False)
#                 if get_info:
#                     return result
#                 elif result is None:
#                     raise ValueError('Info result is None')
#             except Exception as e:
#                 if get_info:
#                     raise e
#                 return self.__onDownloadError(str(e))
#         if 'entries' in result:
#             for entry in result['entries']:
#                 if not entry:
#                     continue
#                 elif 'filesize_approx' in entry:
#                     self.__size += entry['filesize_approx']
#                 elif 'filesize' in entry:
#                     self.__size += entry['filesize']
#                 if name == "":
#                     outtmpl_ = '%(series,playlist_title,channel)s%(season_number& |)s%(season_number&S|)s%(season_number|)02d'
#                     self.name = ydl.prepare_filename(entry, outtmpl=outtmpl_)
#                 else:
#                     self.name = name
#         else:
#             outtmpl_ ='%(title,fulltitle,alt_title)s%(season_number& |)s%(season_number&S|)s%(season_number|)02d%(episode_number&E|)s%(episode_number|)02d%(height& |)s%(height|)s%(height&p|)s%(fps|)s%(fps&fps|)s%(tbr& |)s%(tbr|)d.%(ext)s'
#             realName = ydl.prepare_filename(result, outtmpl=outtmpl_)
#             if name == "":
#                 self.name = realName
#             else:
#                 ext = realName.rsplit('.', 1)[-1]
#                 self.name = f"{name}.{ext}"

#     def __download(self, link, path):
#         try:
#             with YoutubeDL(self.opts) as ydl:
#                 try:
#                     ydl.download([link])
#                     if self.is_playlist and (not ospath.exists(path) or len(listdir(path)) == 0):
#                         self.__onDownloadError("No video available to download from this playlist. Check logs for more details")
#                         return
#                 except DownloadError as e:
#                     if not self.__is_cancelled:
#                         self.__onDownloadError(str(e))
#                     return
#             if self.__is_cancelled:
#                 raise ValueError
#             self.__onDownloadComplete()
#         except ValueError:
#             self.__onDownloadError("Download Stopped by User!")

#     def add_download(self, link, path, name, qual, playlist, args, from_queue=False):
#         if playlist:
#             self.opts['ignoreerrors'] = True
#             self.is_playlist = True
#         self.__gid = ''.join(SystemRandom().choices(ascii_letters + digits, k=10))
#         self.__onDownloadStart(from_queue)
#         if qual.startswith('ba/b-'):
#             mp3_info = qual.split('-')
#             qual = mp3_info[0]
#             rate = mp3_info[1]
#             self.opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': rate}]
#         self.opts['format'] = qual
#         self.extractMetaData(link, name, args)
#         if self.__is_cancelled:
#             return
#         if self.is_playlist:
#             self.opts['outtmpl'] = f"{path}/{self.name}/%(title,fulltitle,alt_title)s%(season_number& |)s%(season_number&S|)s%(season_number|)02d%(episode_number&E|)s%(episode_number|)02d%(height& |)s%(height|)s%(height&p|)s%(fps|)s%(fps&fps|)s%(tbr& |)s%(tbr|)d.%(ext)s"
#         elif not args:
#             self.opts['outtmpl'] = f"{path}/{self.name}"
#         else:
#             folder_name = self.name.rsplit('.', 1)[0]
#             self.opts['outtmpl'] = f"{path}/{folder_name}/{self.name}"
#             self.name = folder_name
#         if config_dict['STOP_DUPLICATE'] and self.name != 'NA' and not self.__listener.isLeech:
#             LOGGER.info('Checking File/Folder if already in Drive...')
#             sname = self.name
#             if self.__listener.isZip:
#                 sname = f"{self.name}.zip"
#             if sname:
#                 smsg, button = GoogleDriveHelper().drive_list(name, True)
#                 if smsg:
#                     self.__onDownloadError('File/Folder already available in Drive.\n')
#                     sendMessage('Here are the search results:', self.__listener.bot, self.__listener.message, button)
#                     return
#         all_limit = config_dict['QUEUE_ALL']
#         dl_limit = config_dict['QUEUE_DOWNLOAD']
#         if all_limit or dl_limit:
#             added_to_queue = False
#             with queue_dict_lock:
#                 dl = len(non_queued_dl)
#                 up = len(non_queued_up)
#                 if (all_limit and dl + up >= all_limit and (not dl_limit or dl >= dl_limit)) or (dl_limit and dl >= dl_limit):
#                     added_to_queue = True
#                     queued_dl[self.__listener.uid] = ['yt', link, path, name, qual, playlist, args, self.__listener]
#             if added_to_queue:
#                 LOGGER.info(f"Added to Queue/Download: {self.name}")
#                 with download_dict_lock:
#                     download_dict[self.__listener.uid] = QueueStatus(self.name, self.__size, self.__gid, self.__listener, 'Dl')
#                 self.__listener.onDownloadStart()
#                 sendStatusMessage(self.__listener.message, self.__listener.bot)
#                 return
#         with queue_dict_lock:
#             non_queued_dl.add(self.__listener.uid)
#         self.__download(link, path)

#     def cancel_download(self):
#         self.__is_cancelled = True
#         LOGGER.info(f"Cancelling Download: {self.name}")
#         if not self.__downloading:
#             self.__onDownloadError("Download Cancelled by User!")

#     def __set_args(self, args):
#         args = args.split('|')
#         for arg in args:
#             xy = arg.split(':', 1)
#             karg = xy[0].strip()
#             if karg == 'format':
#                 continue
#             varg = xy[1].strip()
#             if varg.startswith('^'):
#                 varg = int(varg.split('^')[1])
#             elif varg.lower() == 'true':
#                 varg = True
#             elif varg.lower() == 'false':
#                 varg = False
#             elif varg.startswith(('{', '[', '(')) and varg.endswith(('}', ']', ')')):
#                 varg = eval(varg)
#             self.opts[karg] = varg
