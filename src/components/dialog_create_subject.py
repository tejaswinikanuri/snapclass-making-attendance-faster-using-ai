import streamlit as st
from src.database.db import create_subject

@st.dialog("Create New Subject")
def dialog_create_subject(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="CSE3004")
    sub_name = st.text_input("Subject Name", placeholder="Digital Image Processing")
    section = st.text_input("Section (Slot)", placeholder="A2")

    if st.button("Create Subject Now", type="primary", width="stretch"):
        if sub_id and sub_name and section:
            try:
                create_subject(sub_id, sub_name, section, teacher_id)
                st.toast("Subject Created Successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill all the fields")

