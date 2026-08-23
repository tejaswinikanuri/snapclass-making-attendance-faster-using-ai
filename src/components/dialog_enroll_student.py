import streamlit as st
from src.database.config import supabase
import time
from src.database.db import enroll_student_to_subject

@st.dialog("Enroll in a Subject")
def dialog_enroll_student():
    st.write("Enter the subject code provided by your teacher to enroll")
    join_code = st.text_input("Subject Code", placeholder="CSE3004")
    join_section = st.text_input("Subject Slot", placeholder="E2 or L1+L2")
    
    if st.button("Enroll Now", type="primary", width="stretch"):
        if join_code and join_section:
            res = supabase.table("subjects").select("subject_id, name, subject_code, section").eq("subject_code", join_code.strip()).eq("section", join_section.strip()).execute()
            
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data["student_id"]

                check = supabase.table("subject_students").select("*").eq("student_id", student_id).eq("subject_id", subject["subject_id"]).execute()
                if check.data:
                    st.warning("Already enrolled in this subject!")
                else:
                    enroll_student_to_subject(subject["subject_id"], student_id)
                    st.success("Enrolled Successfully!")
                    time.sleep(1)
                    st.rerun()

            else:
                st.warning("Please enter a valid subject code!")
                            


