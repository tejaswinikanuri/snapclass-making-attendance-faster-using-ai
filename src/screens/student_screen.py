import streamlit as st


def student_screen():
    st.header("Student Screen")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("teacher portal"):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    with col2:
        if st.button("home portal"):
            st.session_state['login_type'] = None
            st.rerun()