import streamlit as st
from src.database.db import create_attendance


def show_attendance_result(df, logs):
    st.write("Please review attendance before confirming")
    st.dataframe(df, hide_index=True, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Discard", width="stretch"):
            st.session_state.attendance_images = []
            st.session_state.voice_attendance_results = None
            st.rerun()
    with col2:
        if st.button("Confirm & Save", type="primary", width="stretch"):
            try:
                create_attendance(logs)
                st.toast("Attendance taken!")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error("Sync Failed!")


@st.dialog("Attendance Reports")
def dialog_attendance_result(df, logs):
    show_attendance_result(df, logs)
  