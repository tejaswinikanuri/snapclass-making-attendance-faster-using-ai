import streamlit as st


def teacher_screen():
    st.header("Teacher Screen")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("home portal"):
            st.session_state['login_type'] = None
            st.rerun()

    with col2:
        if st.button("student portal"):
            st.session_state['login_type'] = 'student'
            st.rerun()