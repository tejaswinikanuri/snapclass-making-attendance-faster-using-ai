from src.database.config import supabase
import bcrypt

def hash_pass(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

# checks if teacher username exits, return true or false
def check_teacher_exists(username): 
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0


def create_teacher(username, name, password):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {"name": new_name, "face_embedding": face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table("students").insert(data).execute()
    return response.data

def create_subject(sub_id, sub_name, section, teacher_id):
    data = {"subject_code": sub_id, "name": sub_name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects