import msal
import base64
import json
import requests
import logging
import time


Errormessage_not_loggedin="Please login first! Click on the 'Sign in with Azure AD' button to login."

def get_token_response_from_code(auth_code,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH,AUTHORITY,st):
    try:
        app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
        result = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPE, redirect_uri=base_url+REDIRECT_PATH)
        return result
    except Exception as e:
        st.write(e)
        return None
    
def get_access_token_FromResponse(response):
    if 'access_token' in response:
        return response['access_token']
    else:
        return None
    
def get_refresh_token_FromResponse(response):
    if 'refresh_token' in response:
        return response['refresh_token']
    else:
       return None


def get_refresh_token(refresh_token,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH,AUTHORITY):
    try:
        app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
        result = app.acquire_token_by_refresh_token(refresh_token, scopes=SCOPE, redirect_uri=base_url+REDIRECT_PATH)
        return result
    except Exception as e:        
        return None
    
def get_user_info(token):
    try:
        headers = {
            "Authorization": "Bearer " + token
        }
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        user_info = response.json()
        if "displayName" not in user_info:
            raise Exception("Token is invalid")
        return user_info
    except Exception as e:
        logging.error(e)
        return None

def check_if_token_expired(session_state):
    # Get the current time as a Unix epoch timestamp
    current_time_epoch = int(time.time())   
    if 'expiredTime' in session_state: 
        expiredtime= session_state['expiredTime']
        # Check if the current time is greater than the expiration time
        if current_time_epoch > expiredtime:
            return True
    else:
        return False
    

#write some code for jwt decode
def jwt_decode_getPayload(token):
    try:
        token_parts = token.split('.')
        payload = token_parts[1]
        # fix padding
        payload += '=' * (4 - (len(payload) % 4))
        # decode base64
        decoded = base64.b64decode(payload).decode('utf-8')
        dict=json.loads(decoded)
        return dict
    except Exception as e:
        return None
    
def jwt_decode_getExpirationTime(dict):
    try:
        iat=dict['iat']
        exp= dict['exp']
        expiredTime= int((exp-iat)/60)
        return expiredTime
    except Exception as e:
        return None
    
def jwt_decode_getEXP(dict):
    try:
        exp=dict['exp']
        return exp
    except Exception as e:
        return None
    

def getuserdetailsanddisplay(CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH,AUTHORITY,st):
    if "access_token" not in st.session_state:
        if 'code' in st.query_params:
            code = st.query_params['code']
            if code:
                response = get_token_response_from_code(code,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH, AUTHORITY,st)
                access_token = get_access_token_FromResponse(response)                
                if access_token is not None:
                    st.session_state['access_token'] = access_token  
        else:            
            return Errormessage_not_loggedin         
    if 'access_token' in st.session_state:    
        access_token= st.session_state['access_token']
        userinfo= get_user_info(access_token)
        #if userinfo is None:
        #    regenerate_token()
        if "displayName" in userinfo:
            st.write("Welcome "+userinfo["displayName"] + "!")
            #activate refresh token
            if 'expiredTime' not in st.session_state:
                payload= jwt_decode_getPayload(access_token)   
                expiredTime= jwt_decode_getEXP(payload)
                st.session_state['expiredTime'] = expiredTime
            

def regenerate_token(session_state,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH,AUTHORITY,refresh_token):
    expired= check_if_token_expired()
    if expired is True:
        response=get_refresh_token(refresh_token,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH, AUTHORITY)
        access_token = get_access_token_FromResponse(response)
        session_state['access_token'] = access_token
        session_state['refresh_token'] = get_refresh_token_FromResponse(response)
        payload= jwt_decode_getPayload(access_token)   
        expiredTime= jwt_decode_getExpirationTime(payload)
        session_state['expiredTime'] = expiredTime
    
def hidestreamlotdeploybutton(st):
    st.markdown("""
    <style>
        .stDeployButton {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
        [data-testid="stStatusWidget"] {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)