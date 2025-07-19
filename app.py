from flask import Flask, jsonify
import psycopg2
import os
from flask_cors import CORS
import json # لإضافة قراءة ملفات JSON
from psycopg2 import extras # لتحميل بيانات متعددة بكفاءة

app = Flask(__name__)
CORS(app)

# دالة الاتصال بقاعدة البيانات
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT")
    )
    return conn

# دالة لإنشاء جدول fatwas_binbaz
def create_fatwas_table():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fatwas_binbaz (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            );
        """)
        conn.commit()
        print("Table 'fatwas_binbaz' created successfully or already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# دالة لتحميل البيانات من ملف JSON إلى قاعدة البيانات
# يجب أن يكون ملف fatwas_binbaz_sample.json في نفس مجلد app.py
@app.route('/load_fatwas_data')
def load_fatwas_data():
    conn = None
    cur = None
    try:
        # تأكد أن ملف fatwas_binbaz_sample.json موجود في نفس مجلد app.py
        with open('fatwas_binbaz_sample.json', 'r', encoding='utf-8') as f:
            fatwas_data = json.load(f)

        conn = get_db_connection()
        cur = conn.cursor()

        # لإدخال بيانات متعددة بكفاءة
        insert_query = "INSERT INTO fatwas_binbaz (question, answer) VALUES %s ON CONFLICT (id) DO NOTHING;"
        
        # تحضير البيانات للإدخال
        values = []
        for item in fatwas_data:
            values.append((item['question'], item['answer']))

        extras.execute_values(cur, insert_query, values)
        
        conn.commit()
        
        return jsonify({"message": f"Successfully loaded {len(fatwas_data)} fatwas into 'fatwas_binbaz' table."})
    except FileNotFoundError:
        return jsonify({"error": "fatwas_binbaz_sample.json not found. Please ensure it's in the same directory as app.py."}), 404
    except Exception as e:
        if conn:
            conn.rollback() # التراجع عن أي تغييرات في حالة الخطأ
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# المسار الرئيسي
@app.route('/')
def home():
    return jsonify({"message": "Hello from Islamic Library API! It's deployed!"})

# مسار لاختبار اتصال قاعدة البيانات
@app.route('/test_db')
def test_db_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"message": "Database connection successful!", "db_version": db_version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# المسار الجديد لعرض جميع الفتاوى (أو جزء منها مؤقتاً)
@app.route('/fatwas')
def get_all_fatwas():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # جلب أول 10 فتاوى فقط لتجنب تحميل كبير
        cur.execute("SELECT id, question, answer FROM fatwas_binbaz LIMIT 10;")
        fatwas = cur.fetchall()
        
        # تحويل النتائج إلى قائمة من القواميس
        fatwas_list = []
        for fatwa_id, question, answer in fatwas:
            fatwas_list.append({
                "id": fatwa_id,
                "question": question,
                "answer": answer
            })
        
        return jsonify(fatwas_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# المسار الجديد لعرض فتوى واحدة حسب الـ ID
@app.route('/fatwas/<int:fatwa_id>')
def get_single_fatwa(fatwa_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, question, answer FROM fatwas_binbaz WHERE id = %s;", (fatwa_id,))
        fatwa = cur.fetchone()
        
        if fatwa:
            return jsonify({
                "id": fatwa[0],
                "question": fatwa[1],
                "answer": fatwa[2]
            })
        else:
            return jsonify({"message": "Fatwa not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# هذا الجزء سيتم تشغيله عند بدء التطبيق
if __name__ == '__main__':
    create_fatwas_table() # استدعاء الدالة لإنشاء الجدول عند بدء التشغيل
    app.run(debug=True)
