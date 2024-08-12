import streamlit as st
from streamlit_multipage import MultiPage
import os
import msal
import app.utils as utils

base_url = "http://localhost:8501"
#set env variables
CLIENT_ID = os.getenv("clientid")
CLIENT_SECRET= os.getenv("clientsecret")
TENANT_ID= os.getenv("tenantid")
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ["User.Read"]
REDIRECT_PATH = f'/Shield' 

# Initialize MSAL
app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
)

# Define a callback route for Azure AD to redirect to
def auth_callback():
    if 'code' not in st.query_params.keys():
        st.error('No code in query parameters. Authentication failed.')
        return None

    code = st.query_params['code'][0]
    response = utils.get_token_response_from_code(code,CLIENT_ID,CLIENT_SECRET,SCOPE,base_url,REDIRECT_PATH, AUTHORITY,st)
    access_token = utils.get_access_token_FromResponse(response)
    refresh_token = utils.get_refresh_token_FromResponse(response)
    if 'error' in  response:
        str= response['error']+ response.get('error_description')
        st.write(str)
        return None
    else:
        st.success("Login successful!")
        if st.button("Logout"):
            logout()
        st.session_state['refresh_token'] = refresh_token 
        return access_token

# Define a login function
def login():    
    if 'access_token' not in st.session_state:
        auth_url = app.get_authorization_request_url(SCOPE, redirect_uri=base_url+REDIRECT_PATH)
        st.markdown(f'[Sign in with Azure AD]({auth_url})')
    else:
        st.success('You are signed in.')


    if st.query_params and 'code' in st.query_params:
       st.session_state['access_token'] = auth_callback

# Define a logout function
def logout():
    st.session_state.pop("access_token", None)
    st.experimental_rerun()


def main():

    # ------------------ Streamlit Page Configuration ------------------ #   
    
    st.set_page_config(
        page_title="Login",
        page_icon=":shield:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Create two columns
    col1, col2 = st.columns([1, 3])
    with col1:  
        st.image("app/shield.png", use_column_width=True)
    with col2:
        st.title("Shield me Home Page!")
        st.markdown(
            """
            Shield is a Streamlit app that demonstrates how to secure your Streamlit app with Azure AD.
            """
        )
      
    app = MultiPage()  
    app.st = st     

    
    if "access_token" not in st.session_state:
        with col2:           
            login()
    else:
        access_token= st.session_state['access_token']
        userinfo= utils.get_user_info(access_token)
             
        if "displayName" in userinfo:
            with col2:              
                st.write("Welcome"+" "+userinfo["displayName"]+". Please navigate to through the sidebar (navigation bar) to view our features. Enjoy!")                
                if st.button("Logout"):
                    logout()   
    #Hide Deploy button 
    utils.hidestreamlotdeploybutton(st)
             
       
    

if __name__ == "__main__":
    main()
  
    
