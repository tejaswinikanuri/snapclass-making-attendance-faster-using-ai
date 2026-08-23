import streamlit as st
from src.database.config import supabase
import time
from src.database.db import enroll_student_to_subject

@st.dialog("Quick Enrollment")
def dialog_auto_enroll(join_code, join_section):
    student_id = st.session_state.student_data['student_id']

    res = supabase.table("subjects").select("*").eq("subject_code", join_code).eq("section", join_section).execute()
    if not res.data:
        st.error("Subject Code not Found!")
        if st.button("Close"):
            st.query_params.clear()
            st.rerun()
        return 
    subject = res.data[0]
    check = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject["subject_id"]).execute()
    if check.data:
        st.info("Already enrolled in this subject!")
        if st.button("Got it!"):
            st.query_params.clear()
            st.rerun()
        return 
    st.markdown(f"Would you like to enroll in **{subject['name']}**?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("No thanks!"):
            st.query_params.clear()
            st.rerun()
      
    with col2:
        if st.button("Yes, Enroll me!", type='primary', width="stretch"):
            enroll_student_to_subject(subject["subject_id"], student_id)
            st.success("Enrolled Successfully!")
            time.sleep(1)
            st.query_params.clear()
            st.rerun()

    