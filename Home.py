import streamlit as st
import yaml
import streamlit_authenticator as stauth
import bcrypt
import os

# Set page configuration
st.set_page_config(
    page_title="Smart Todo List - Login",
    page_icon="✅",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .login-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Load or create config file
if not os.path.exists('config.yaml'):
    config = {
        'credentials': {
            'usernames': {}
        }
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)
else:
    with open('config.yaml') as file:
        config = yaml.safe_load(file)

# Authentication
authenticator = stauth.Authenticate(
    config['credentials'],
    'todo_app_cookie',
    'todo_app_key',
    cookie_expiry_days=30
)

# Center align title
st.markdown("<h1 style='text-align: center;'>✨ Smart Todo List</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Manage your tasks efficiently</p>", unsafe_allow_html=True)
st.markdown("---")

# Login/Register interface in a container
with st.container():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        name, authentication_status, username = authenticator.login('Login', 'main')
        if st.session_state.authentication_status == False:
            st.error('Username/password is incorrect')
        elif st.session_state.authentication_status:
            st.success('Successfully logged in!')
            st.info('Please go to Dashboard page to manage your tasks')
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("registration_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Create Account")
            
            if submit_button:
                if new_username and new_password:
                    if new_username not in config['credentials']['usernames']:
                        config['credentials']['usernames'][new_username] = {
                            'password': bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode(),
                            'name': new_username
                        }
                        with open('config.yaml', 'w') as file:
                            yaml.dump(config, file, default_flow_style=False)
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.error("Please enter both username and password!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <small>© 2024 Smart Todo List App. Made with ❤️ using Streamlit.</small>
</div>
""", unsafe_allow_html=True) 