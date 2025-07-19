from flask import Flask, jsonify
import psycopg2
import os
from flask_cors import CORS

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

# المسار لعرض جميع الفتاوى (أو جزء منها مؤقتاً)
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

# المسار لعرض فتوى واحدة حسب الـ ID
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

if __name__ == '__main__':
    app.run(debug=True)
