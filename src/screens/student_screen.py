import streamlit as st
from src.components.footer import footer_dashboard, footer_home
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_attendance, get_student_subjects, unenroll_student_to_subject
import time
from src.components.dialog_enroll_student import dialog_enroll_student
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with col1:
        header_dashboard()

    with col2:
        st.subheader(f"""Welcome, {student_data['name']}""")
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()
    st.space()

    c1, c2 = st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")

    with c2:
        if st.button("Enroll in a Subject", type="primary", width="stretch"):
            dialog_enroll_student()

    st.divider()

    with st.spinner("Loading your Subjects..."):
        subjects = get_student_subjects(student_data['student_id'])
        logs = get_student_attendance(student_data['student_id'])


    stats_map = {}
    for log in logs:
        sid = log["subject_id"]
        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended":0}
        stats_map[sid]["total"] += 1

        if log.get("ispresent"):
            stats_map[sid]["attended"] += 1

    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):
        sub = sub_node["subjects"]
        sid = sub["subject_id"]

        stats = stats_map.get(sid, {"total":0, "attended":0})
        def unenroll_button():
            if st.button("Unenroll from this subject", type="tertiary", width="stretch", icon=":material/delete_forever:"):
                unenroll_student_to_subject(sid, student_data['student_id'])
                st.toast(f"Unenrolled from {sub['name']} Successfully!")
                st.rerun()
        
        with cols[i%2]:
            subject_card(
                name=sub['name'], 
                code=sub["subject_code"], 
                section=sub["section"],
                stats=[
                    ('🗓️', "Total", stats['total']),
                    ('✅', "Attended", stats['attended']),
                ],
                footer_callback=unenroll_button
            )


    footer_dashboard()

def student_screen():
    style_background_dashboard()
    style_base_layout()

    if st.session_state.get("is_logged_in", False):
        student_dashboard()
        return

    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with col1:
        header_dashboard()

    with col2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header("Login using Face ID", text_alignment="center")
    st.space()
    st.space()

    if "show_registration" not in st.session_state:
        st.session_state.show_registration = False

    photo_source = st.camera_input("Position your face in the center")

    if photo_source and not st.session_state.show_registration:
        img = np.array(Image.open(photo_source))

        with st.spinner("AI is scanning..."):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("Face not found!")
            elif num_faces > 1:
                st.warning("Multiple faces found!")
            else:
                student = None
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                if student:
                    st.session_state.is_logged_in = True
                    st.session_state.user_role = "student"
                    st.session_state.student_data = student
                    st.toast(f"Welcome Back! {student['name']}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("Face not recognised! You might be a new student!")
                    st.session_state.show_registration = True

    if st.session_state.show_registration:
        with st.container(border=True):
            st.header("Register New Profile")
            new_name = st.text_input("Enter your name", placeholder="E.g. Tejaswini Kanuri")
            st.subheader("Optional: Voice Enrollment")
            st.info("Enroll your voice for only attendance")

            audio_data = None
            try:
                audio_data = st.audio_input("Record a short phrase like I am present, My name is Akash.")
            except Exception as e:
                st.error("Audio Data Failed!")

            # DEBUG: show widget state on every rerun, before any button click
            print(f"[DEBUG] render pass -> audio_data is None: {audio_data is None}")
            st.caption(f"🐛 DEBUG: audio_data = {audio_data!r}")

            if st.button("Create Account", type="primary"):
                print("[DEBUG] Create Account button clicked")
                st.write("🐛 DEBUG: button clicked, new_name =", repr(new_name))
                st.write("🐛 DEBUG: audio_data at click time =", repr(audio_data))

                if new_name:
                    with st.spinner("Creating profile.."):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        print(f"[DEBUG] encodings found: {bool(encodings)}")

                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data is not None:
                                raw_bytes = audio_data.read()
                                print(f"[DEBUG] audio bytes read, length = {len(raw_bytes)}")
                                st.write(f"🐛 DEBUG: audio byte length = {len(raw_bytes)}")

                                voice_emb = get_voice_embedding(raw_bytes)
                                print(f"[DEBUG] voice_emb result: {'None' if voice_emb is None else f'list of len {len(voice_emb)}'}")
                                st.write(f"🐛 DEBUG: voice_emb = {'None' if voice_emb is None else f'<{len(voice_emb)} floats>'}")

                                if voice_emb is None:
                                    st.warning("Couldn't process your voice sample — continuing without it.")
                            else:
                                print("[DEBUG] audio_data was None at click time — skipping voice pipeline entirely")
                                st.info("No voice sample recorded — skipping voice enrollment.")

                            st.write("🐛 DEBUG: about to call create_student with voice_embedding =",
                                      "None" if voice_emb is None else f"<{len(voice_emb)} floats>")

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                            print(f"[DEBUG] create_student response: {response_data}")

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = "student"
                                st.session_state.student_data = response_data[0]
                                st.session_state.show_registration = False
                                st.toast(f"Profile Created! Hi {new_name}!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Couldn't capture your facial features for registration")
                else:
                    st.warning("Please enter your name")

    footer_dashboard()