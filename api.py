import json
import time
import hashlib
import hmac
import base64
import uuid

# Declare empty header dictionary
global apiHeader 
apiHeader = {}

def make_header():
    global apiHeader 
    global apiBody
    # open token
    token = '96-chars-token' # copy and paste from the SwitchBot app V6.14 or later
    # secret key
    secret = '32-chars-key' # copy and paste from the SwitchBot app V6.14 or later
    nonce = uuid.uuid4()
    t = int(round(time.time() * 1000))
    string_to_sign = '{}{}{}'.format(token, t, nonce)

    string_to_sign = bytes(string_to_sign, 'utf-8')
    secret = bytes(secret, 'utf-8')

    sign = base64.b64encode(hmac.new(secret, msg=string_to_sign,digestmod=hashlib.sha256).digest())
    # solely for debug purposes, hence commented out
    # print ('Authorization: {}'.format(token))
    # print ('t: {}'.format(t))
    # print ('sign: {}'.format(str(sign, 'utf-8')))
    # print ('nonce: {}'.format(nonce))

    #Build api header JSON
    apiHeader['Authorization']=token
    apiHeader['Content-Type']='application/json'
    apiHeader['charset']='utf8'
    apiHeader['t']=str(t)
    apiHeader['sign']=str(sign, 'utf-8')
    apiHeader['nonce']=str(nonce)
