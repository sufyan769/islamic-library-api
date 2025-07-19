from flask import Flask, jsonify
import psycopg2
import os
from flask_cors import CORS # تم استيراد Flask-CORS

app = Flask(__name__)
CORS(app) # تم تمكين CORS لجميع المسارات في التطبيق

# تعريف دالة الاتصال بقاعدة البيانات
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT")
    )
    return conn

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
        # إذا فشل الاتصال، أرجع رسالة خطأ
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
