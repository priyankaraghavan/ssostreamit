
import streamlit as st
import app.utils as utils
import os
import Login


base_url = "http://localhost:8501"
#set env variables
CLIENT_ID = os.getenv("clientid")
CLIENT_SECRET= os.getenv("clientsecret")
TENANT_ID= os.getenv("tenantid")
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ["User.Read"]
REDIRECT_PATH=f'/Shield' 



def main():
   
    # ------------------ Streamlit Page Configuration ------------------ #   
    st.set_page_config(
        page_title="Shield",
        page_icon=":shield:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Create three columns
    col1, col2 = st.columns([1,3])

    with col1:  
        st.image("app/shield.png", use_column_width=True)

    with col2:
        st.title("Shield Landing Page")
        st.markdown(
        """
        Shield is a Streamlit app that demonstrates how to secure your Streamlit app with Azure AD.
        """
        )
        if "access_token" not in st.session_state:
            if 'code' not in st.query_params:
                st.switch_page("Login.py")                
      
        utils.getuserdetailsanddisplay(CLIENT_ID, CLIENT_SECRET, SCOPE, base_url,REDIRECT_PATH, AUTHORITY, st)     
        #Hide Deploy button 
        utils.hidestreamlotdeploybutton(st)  

if __name__ == "__main__":
    main()