import streamlit as st
from src.database.config import supabase
from src.components.footer import footer_dashboard, footer_home
from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects
from src.components.dialog_create_subject import dialog_create_subject 
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import dialog_share_subject
from src.components.dialog_add_photos import dialog_add_photos
import numpy as np
from src.pipelines.face_pipeline import predict_attendance
from datetime import datetime
import pandas as pd
from src.components.dialog_attendace_result import dialog_attendace_result

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
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
     
    with col1:
        header_dashboard()

    with col2:
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()
    st.space()
    

    if 'cur_teacher_tab' not in st.session_state:
        st.session_state.cur_teacher_tab = "take_attendance"

    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.cur_teacher_tab == "take_attendance" else "tertiary"
        
        if st.button("Take Attendance", type=type1, width="stretch", icon=':material/ar_on_you:'):
            st.session_state.cur_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.cur_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width="stretch", icon=':material/book_ribbon:'):
            st.session_state.cur_teacher_tab = "manage_subjects"
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.cur_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=type3, width="stretch", icon=':material/cards_stack:'):
            st.session_state.cur_teacher_tab = "attendance_records"
            st.rerun()

    st.divider()
    if st.session_state.cur_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.cur_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.cur_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()




def teacher_tab_take_attendance():
    st.header("hi teacher_tab_take_attendance")


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    col1, col2 = st.columns(2)

    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button("Create a New Subject", width="content"):
            dialog_create_subject(teacher_id)

    #List all subjects
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                dialog_share_subject(sub['name'], sub['subject_code'], sub['section'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats=stats,
            footer_callback=share_btn
        )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")




def teacher_tab_attendance_records():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You haven't created any subjects yet. Create one to take attendance.")
        return

    subject_options = {f"{sub['name']} - {sub['subject_code']}": sub['subject_id'] for sub in subjects}
    col1, col2 = st.columns([3,1], vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))

    with col2:
        if st.button("Add Photos", type='primary', icon=':material/photo_prints:', width="stretch"):
            dialog_add_photos()

    selected_subject_id = subject_options[selected_subject_label]
    st.divider()

    if st.session_state.attendance_images:
        st.subheader("Added Photos")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, caption=f"Photo {idx+1}", width='stretch')

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("Clear All Photos", width="stretch", type="tertiary", icon=":material/delete:"):
                st.session_state.attendance_images = []
                st.rerun()
        
        with c2:
            has_photo = bool(st.session_state.attendance_images)
            if st.button("Run Face Analysis", width="stretch", type="secondary", icon=":material/analytics:"):
                with st.spinner("Deep scanning classroom photos..."):
                    all_detected_ids = {}

                    for idx, img in enumerate(st.session_state.attendance_images):
                        img_np = np.array(img.convert('RGB'))
                        detected, _, _ = predict_attendance(img_np)
                        
                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)
                                all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")
                    
                    enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
                    enrolled_students = enrolled_res.data
                    if not enrolled_students:
                        st.warning("No Students enrolled in this Course!")
                    else:
                        results, attendance_to_log = [], []
                        cur_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                        for node in enrolled_students:
                            student = node['students']
                            sources = all_detected_ids.get(int(student['student_id']), [])

                            is_present = len(sources) > 0
                            results.append({
                                "Name": student['name'],
                                "ID": student['student_id'],
                                "Source": ", ".join(sources) if is_present else "-",
                                "Status": "✅ Present" if is_present else "❌ Absent"
                            })

                            attendance_to_log.append({
                                "student_id": student['student_id'],
                                "subject_id": selected_subject_id,
                                "timestamp": cur_timestamp,
                                "is_present": bool(is_present)
                            })
                
                    dialog_attendace_result(pd.DataFrame(results), attendance_to_log)

        with c3:
            if st.button("Use Voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
                dialog_voice_attendance()
                       


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
        
