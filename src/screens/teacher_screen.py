import streamlit as st
from src.components.footer import footer_dashboard, footer_home
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout


def teacher_screen():
    
    style_background_dashboard()
    style_base_layout()

    if "teacher_login_type" not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type=="register":
        teacher_screen_register()
    footer_dashboard()


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
        st.button("Login", key="loginbtn", shortcut="control+enter", icon=":material/passkey:", icon_position='left', width="stretch")

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
    teacher_conf_pass = st.text_input("Enter password", type='password', placeholder="Confirm your password")
    st.divider()

    btncol1, btncol2 = st.columns(2)
    with btncol1:
        st.button("Register Now", type="primary", key="registerbtn", shortcut="control+enter", width="stretch", icon=":material/passkey:", icon_position='left')                   
        
    with btncol2:
        if st.button("Login Instead", key="loginbtn", icon=":material/passkey:", icon_position='left', width="stretch"):
            st.session_state.teacher_login_type = "login"
        

    footer_dashboard