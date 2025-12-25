import sqlite3
import os
import random
from flask import Flask, render_template, request, jsonify, redirect

app = Flask(__name__)

# Veritabanı dosyasını kalıcı olacak klasöre ('/app/data') koyuyoruz
DB_FOLDER = '/app/data'
DB_FILE = os.path.join(DB_FOLDER, 'colors.db')

def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Renkleri ve açıyı saklayacak tablo
    c.execute('''CREATE TABLE IF NOT EXISTS favorites 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  color1 TEXT, color2 TEXT, angle INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def generate_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

@app.route('/')
def index():
    # 1. Yeni rastgele renkler üret (Anlık)
    current_colors = {
        'color1': generate_hex(),
        'color2': generate_hex(),
        'angle': random.randint(0, 360)
    }
    
    # 2. Kayıtlı favorileri veritabanından çek (Kalıcı)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, color1, color2, angle FROM favorites ORDER BY id DESC")
    favorites = c.fetchall()
    conn.close()

    return render_template('index.html', current=current_colors, favorites=favorites)

# API: Favorilere Ekle
@app.route('/save', methods=['POST'])
def save_color():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO favorites (color1, color2, angle) VALUES (?, ?, ?)", 
              (data['color1'], data['color2'], data['angle']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# API: Favoriden Sil
@app.route('/delete/<int:id>')
def delete_color(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
