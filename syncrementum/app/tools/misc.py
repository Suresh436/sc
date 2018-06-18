import base64
import os
import pickle

from InstagramAPI import InstagramAPI, requests
from flask_login import current_user

from app.config import HASH_SECTIONS, HASH_PBKDF2_INDEX, PBKDF2_ITERATIONS, HASH_SALT_INDEX, PBKDF2_SALT_BYTES, \
    PBKDF2_HASH_ALGORITHM
from app.logger_setup import errorlog
from hash import crypt

"""Collection of miscellaneous tools to be used through the platform"""


def check_ra_pwd(password, dbhash):
    # split database hash into list
    params = str(dbhash).split(':')
    if len(params) < HASH_SECTIONS:
        return ''
    # base64 decode for encoded crypted hash pasword
    decoded_val = base64.b64decode(params[HASH_PBKDF2_INDEX])

    # get crypted hash password using PBKDF2 library
    encrypt_pass = crypt(password, params[HASH_SALT_INDEX],PBKDF2_ITERATIONS)
    # match both passwords
    get_match = match_password(decoded_val, encrypt_pass)
    return get_match


def create_ra_hash(password):
    # create salt using random numbers
    salt = base64.b64encode(os.urandom(PBKDF2_SALT_BYTES))
    # get crypted hash password using PBKDF2 library
    encrypt_pass = crypt(password, salt, PBKDF2_ITERATIONS)
    # create database hash using salt, algo, crypted password and iterations
    script_response = PBKDF2_HASH_ALGORITHM + ":" + str(PBKDF2_ITERATIONS) + ":" + salt + ":" + base64.b64encode(encrypt_pass)
    # return the response
    return script_response


def match_password(a, b):
    # set response = 0
    response = '0'
    # get length of password
    get_pwd_length = len(a) + 1
    # find difference
    diff = len(a) ^ len(b)
    for index in range(0, get_pwd_length):

        if index >= len(a) or index >= len(b):
            break
        diff |= ord(a[index]) ^ ord(b[index])
    if diff == 0:
        response = '1'
    return response


def get_insta_object(access_token, get_proxy, existUser=None):
    try:
        if existUser is None:
            existUser = current_user
        with open('ista_data.pkl', 'rb') as input:
            insta_object = pickle.load(input)
        if existUser.id in insta_object and insta_object[existUser.id].rank_token:
            insta_object = insta_object[existUser.id]
            insta_object.getProfileData()
            prof_data = insta_object.LastJson
            if prof_data['status'] == 'ok':
                return insta_object
            else:
                return insta_login(access_token, get_proxy, existUser)
        else:
            return insta_login(access_token, get_proxy, existUser)
    except Exception as err:
        errorlog.error('Instagram Login Failed', details=str(err))
        return "error"


def insta_logout():
    try:
        with open('ista_data.pkl', 'rb') as input:
            InstaAPI = pickle.load(input)
        InstaAPI.rank_token = ''
        InstaAPI.logout()
        with open('ista_data.pkl', 'wb') as output:
            pickle.dump(InstaAPI, output, pickle.HIGHEST_PROTOCOL)
    except Exception as err:
        errorlog.error('Instagram Logout Failed', details=str(err))


def insta_login(access_token, get_proxy, existUser=None):
    try:
        if existUser is None:
            existUser = current_user
        insta_usr_detail = access_token.split('@')
        instauser_name = base64.b64decode(insta_usr_detail[0]) if insta_usr_detail[0] else ''
        instauser_pwd = base64.b64decode(insta_usr_detail[1]) if insta_usr_detail[1] else ''
        InstaAPI = InstagramAPI(
            instauser_name,
            instauser_pwd
        )
        if get_proxy:
            proxy_username = get_proxy.username if get_proxy.username else None
            proxy_password = get_proxy.password if get_proxy.password else None
            if proxy_username is not None:
                prox = proxy_username+':'+proxy_password+'@'+get_proxy.ip_address+':'+str(get_proxy.port)
            else:
                prox = get_proxy.ip_address+':'+str(get_proxy.port)
            InstaAPI.setProxy(prox)
        login_res = InstaAPI.login(True)
        insta_object = dict()
        insta_object[existUser.id] = InstaAPI
        if login_res:
            with open('ista_data.pkl', 'wb') as output:
                pickle.dump(insta_object, output, pickle.HIGHEST_PROTOCOL)
            return insta_object[existUser.id]
        else:
            code_obj = dict()
            error_message = InstaAPI.LastJson
            code_obj[str(existUser.id)+'_code'] = InstaAPI
            if 'two_factor_info' in error_message:
                with open('ista_data.pkl', 'wb') as output:
                    pickle.dump(code_obj, output, pickle.HIGHEST_PROTOCOL)
                return "code_required"
            elif 'error_type' in error_message and error_message['error_type'] == 'checkpoint_challenge_required':
                challenge_obj = dict()
                challenge_obj[str(existUser.id) + '_challenge'] = InstaAPI
                with open('ista_data.pkl', 'wb') as output:
                    pickle.dump(challenge_obj, output, pickle.HIGHEST_PROTOCOL)
                return error_message
            errorlog.error('Instagram Login Failed', details=InstaAPI.LastJson)
            return "error"

    except Exception as err:
        errorlog.error('Instagram Login Failed', details=str(err))
        return "error"


def two_factor_login(access_token, get_proxy, verif_code, user_detail):
    try:
        with open('ista_data.pkl', 'rb') as input:
            code_obj = pickle.load(input)
        if str(user_detail.id)+'_code' in code_obj:
            i_obj = code_obj[str(user_detail.id)+'_code']
            login_res = i_obj.twoFactorLogin(verif_code, i_obj.LastJson['two_factor_info']['two_factor_identifier'])
            if login_res:
                insta_object = dict()
                insta_object[user_detail.id] = i_obj
                with open('ista_data.pkl', 'wb') as output:
                    pickle.dump(insta_object, output, pickle.HIGHEST_PROTOCOL)
                return insta_object[user_detail.id]
            else:
                errorlog.error('Two Factor  Login Failed', details=i_obj.LastJson)
                return 'invalid_code'
        else:
            return insta_login(access_token, get_proxy)

    except Exception as err:
        errorlog.error('Two Factor Login Failed', details=str(err))
        return "error"


def challenge_req(choice, user_detail):
    try:
        with open('ista_data.pkl', 'rb') as input:
            code_challenge = pickle.load(input)
        if str(user_detail.id)+'_challenge' in code_challenge:
            i_obj = code_challenge[str(user_detail.id)+'_challenge']
            api_url = i_obj.LastJson
            login_res = i_obj.sendChallengeCode(int(choice), api_url['challenge']['api_path'][1:])
            if login_res:
                challenge_obj = dict()
                challenge_obj[str(user_detail.id) + '_challenge_code'] = i_obj
                challenge_obj['api_url'] = api_url['challenge']['api_path']
                with open('ista_data.pkl', 'wb') as output:
                    pickle.dump(challenge_obj, output, pickle.HIGHEST_PROTOCOL)
                return challenge_obj[str(user_detail.id) + '_challenge_code']
            else:
                errorlog.error('Challenge Request Failed', details=i_obj.LastJson)
                return 'code_not_sent'
        else:
            return 'code_not_sent'

    except Exception as err:
        errorlog.error('Challenge Request Failed', details=str(err))
        return 'code_not_sent'


def challenge_security_code(security_code, user_detail):
    try:
        with open('ista_data.pkl', 'rb') as input:
            code_challenge = pickle.load(input)
        if str(user_detail.id)+'_challenge_code' in code_challenge:
            i_obj = code_challenge[str(user_detail.id)+'_challenge_code']
            login_res = i_obj.LoginWithSecurityCode(security_code, code_challenge['api_url'][1:])
            if login_res:
                insta_object = dict()
                insta_object[user_detail.id] = i_obj
                with open('ista_data.pkl', 'wb') as output:
                    pickle.dump(insta_object, output, pickle.HIGHEST_PROTOCOL)
                return insta_object[user_detail.id]
            else:
                errorlog.error('Validate Challenge Code Failed', details=i_obj.LastJson)
                return 'invalid_security_code'
        else:
            return 'invalid_security_code'

    except Exception as err:
        errorlog.error('Validate Challenge Code Failed', details=str(err))
        return "error"


def get_states():
    states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }
    try:
        return states
    except:
        return False


