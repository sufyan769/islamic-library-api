import psycopg2
import json
from psycopg2 import extras
import os

# معلومات الاتصال بقاعدة البيانات على Render
# استبدل القيم هنا بالمعلومات الحقيقية من صفحة Info على Render
# إذا كنت تستخدم ملف .env محلي، يمكنك تحميلها منه
DB_HOST = "dpg-ditq6riqnbc73kecd0-a.frankfurt-postgres.render.com" # من Hostname
DB_NAME = "islamic_db_edix" # من Database
DB_USER = "myprojectuser" # من Username
DB_PASSWORD = "YOUR_DB_PASSWORD" # استبدل بكلمة المرور الحقيقية
DB_PORT = "5432" # من Port

# اسم ملف JSON الذي يحتوي على الفتاوى (يجب أن يكون في نفس مجلد هذا السكريبت)
JSON_FILE_PATH = 'fatwas_binbaz_sample.json'
TABLE_NAME = 'fatwas_binbaz' # اسم الجدول الذي أنشأناه

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def load_fatwas_data_to_db():
    conn = None
    cur = None
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            fatwas_data = json.load(f)

        conn = get_db_connection()
        cur = conn.cursor()

        # لإدخال بيانات متعددة بكفاءة
        # ON CONFLICT (id) DO NOTHING; يتجنب إدخال نفس الفتوى إذا كانت موجودة بالفعل
        insert_query = f"INSERT INTO {TABLE_NAME} (question, answer) VALUES %s ON CONFLICT (id) DO NOTHING;"

        values = []
        for item in fatwas_data:
            # التأكد من أن المفتاحين 'question' و 'answer' موجودين
            question_text = item.get('question', '')
            answer_text = item.get('answer', '')
            if question_text and answer_text: # تأكد أن البيانات ليست فارغة
                values.append((question_text, answer_text))

        if values:
            extras.execute_values(cur, insert_query, values)
            conn.commit()
            print(f"Successfully loaded {len(values)} fatwas into '{TABLE_NAME}' table.")
        else:
            print("No valid fatwas found in the JSON file to load.")

    except FileNotFoundError:
        print(f"Error: JSON file '{JSON_FILE_PATH}' not found. Please ensure it's in the same directory as this script.")
    except Exception as e:
        print(f"Error loading data: {e}")
        if conn:
            conn.rollback() # التراجع عن أي تغييرات في حالة الخطأ
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    load_fatwas_data_to_db()
