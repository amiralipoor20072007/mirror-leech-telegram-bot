from threading import Thread
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from bot.helper.ext_utils.bot_utils import get_readable_message

from bot.helper.mirror_utils.download_utils.aria2_download import add_aria2c_download

# creating the flask app
APi = Flask(__name__)
# creating an API object
api = Api(APi)
  
# making a class for a particular resource
# the get, post methods correspond to get and post requests
# they are automatically mapped by flask_restful.
# other methods include put, delete, etc.
class Input(Resource):
  
    # corresponds to the GET request.
    # this function is called whenever there
    # is a GET request for this resource
    def get(self):
  
        return jsonify({'message': 'hello world'})
  
    # Corresponds to POST request
    def post(self):
        data:dict
        data = request.get_json()
        chat_id = data.get('chat_id')

        if data.get('ServerHash',''):
            ServerHash = data.get('ServerHash','')
            link,filename,auth = data.get('link') , data.get('filename') , data.get('auth')
            Thread(target=add_aria2c_download,args=(link,chat_id,ServerHash,filename,auth)).start()
            return
        if chat_id:
            msg , button = get_readable_message()
            return jsonify({'msg': msg})
        
        return

api.add_resource(Input, '/')