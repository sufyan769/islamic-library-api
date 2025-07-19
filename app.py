from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=os.environ.get('DB_PORT')
    )
    return conn

# المسار الرئيسي (جرب هذا أولاً)
@app.route('/')
def home():
    return jsonify({"message": "Hello from Islamic Library API! It's deployed!"})

# مثال لمسار يجلب بعض البيانات (تحتاج إلى تعديله ليناسب قاعدة بياناتك)
@app.route('/test_db')
def test_db_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();") # أمر SQL بسيط لاختبار الاتصال
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"message": "Database connection successful!", "db_version": db_version[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
