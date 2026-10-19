from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# مجلد حفظ ملفات المودات المرفوعة
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# إنشاء قاعدة البيانات للتحكم في المودات
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# الصفحة الرئيسية - عرض جميع المودات
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mods ORDER BY id DESC')
    mods_data = cursor.fetchall()
    conn.close()
    return render_template('index.html', mods=mods_data)

# صفحة إضافة مود جديد
@app.route('/add', methods=['GET', 'POST'])
def add_mod():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        file = request.files['file']
        
        if file and file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO mods (title, description, category, filename) VALUES (?, ?, ?, ?)',
                           (title, description, category, file.filename))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
            
    return render_template('add_mod.html')

# رابط تحميل المود
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # تشغيل الخادم المحلي
    app.run(host='0.0.0.0', port=5000, debug=True)
