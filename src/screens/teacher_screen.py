import streamlit as st
from src.components.footer import footer_dashboard, footer_home
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.database.db import check_teacher_exists, create_teacher, teacher_login

def teacher_screen():
    
    style_background_dashboard()
    style_base_layout()


    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif "teacher_login_type" not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type=="register":
        teacher_screen_register()
    footer_dashboard()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    st.header(f"""Welcome, {teacher_data['name']}""")

def register_teacher(teacher_username, teacher_name,  teacher_pass, teacher_confirm_pass):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken!"
    if teacher_pass != teacher_confirm_pass:
        return False, "Password doesn't match!"

    try:
        create_teacher(teacher_username, teacher_name, teacher_pass)
        return True, "Successfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"

def login_teacher(teacher_username, teacher_pass):
    if not teacher_username or not teacher_pass:
        return False 

    teacher = teacher_login(teacher_username, teacher_pass)
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    else:
        return False

    


def teacher_screen_login():
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
 
    with col1:
        header_dashboard()

    with col2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using password", text_alignment="center")
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder="@tejaswini")
    teacher_pass= st.text_input("Enter password", type='password', placeholder="Enter your password")
    st.divider()

    btncol1, btncol2 = st.columns(2)
    with btncol1:
        if st.button("Login", key="loginbtn", shortcut="control+enter", icon=":material/passkey:", icon_position='left', width="stretch"):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid username and password")

    with btncol2:
        if st.button("Register Instead", type="primary", key="registerbtn", width="stretch", icon=":material/passkey:", icon_position='left'):
            st.session_state.teacher_login_type = "register"

    footer_dashboard



def teacher_screen_register():
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
 
    with col1:
        header_dashboard()

    with col2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Register your teacher profile")
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder="@tejaswini")
    teacher_name = st.text_input("Enter name", placeholder="Tejaswini Kanuri")
    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter your password")
    teacher_confirm_pass = st.text_input("Enter password", type='password', placeholder="Confirm your password")
    st.divider()

    btncol1, btncol2 = st.columns(2)
    with btncol1:
        if st.button("Register Now", type="primary", key="registerbtn", shortcut="control+enter", width="stretch", icon=":material/passkey:", icon_position='left'):
            success, message = register_teacher(teacher_username, teacher_name,  teacher_pass, teacher_confirm_pass) 
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'   
                st.rerun()
            else:   
                st.error(message)           
        
    with btncol2:
        if st.button("Login Instead", key="loginbtn", icon=":material/passkey:", icon_position='left', width="stretch"):
            st.session_state.teacher_login_type = "login"
        

    footer_dashboard