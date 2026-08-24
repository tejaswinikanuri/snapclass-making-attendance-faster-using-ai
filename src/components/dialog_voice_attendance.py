import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendance_result import show_attendance_result

@st.dialog("Voice Attendance")
def dialog_voice_attendance(selected_subject_id):
    st.write("Record audio of students saying I am present. Then AI will recognise the students")

    audio_data = st.audio_input("Record classroom audio")

    if audio_data is not None:
        st.session_state["voice_audio_bytes"] = audio_data.getvalue()
    
    if st.button("Analyze Audio", type="primary", width="stretch"):
        with st.spinner("Processing audio data"):
            enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
            enrolled_students = enrolled_res.data
            if not enrolled_students:
                st.warning("No Students enrolled in this Course!")
                return
            candidates_dict = { 
                s["students"]['student_id']: s["students"]['voice_embedding'] 
                for s in enrolled_students if s["students"].get("voice_embedding")
            }

            if not candidates_dict:
                st.warning("No Students have voice embeddings!")
                return

            audio_bytes = st.session_state.get("voice_audio_bytes")
            st.write("DEBUG audio bytes:", len(audio_bytes) if audio_bytes else None)
            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)
            st.write("DEBUG detected scores:", detected_scores)
            results, attendance_to_log = [], []
            cur_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'], 0)

                is_present = score > 0
                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Source": score if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })

                attendance_to_log.append({
                    "student_id": student['student_id'],
                    "subject_id": selected_subject_id,
                    "timestamp": cur_timestamp,
                    "ispresent": bool(is_present)
                })
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)
    
    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
