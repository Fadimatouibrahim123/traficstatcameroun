from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compute_stats(df):
    stats = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        s = df[col].dropna()
        stats[col] = {
            'count': int(s.count()),
            'mean': round(float(s.mean()), 2),
            'median': round(float(s.median()), 2),
            'std': round(float(s.std()), 2),
            'min': round(float(s.min()), 2),
            'max': round(float(s.max()), 2),
            'q1': round(float(s.quantile(0.25)), 2),
            'q3': round(float(s.quantile(0.75)), 2),
        }
    return stats, numeric_cols

def df_to_charts(df, numeric_cols):
    charts = {}
    for col in numeric_cols[:4]:
        s = df[col].dropna()
        counts, bins = np.histogram(s, bins=8)
        charts[col] = {
            'labels': [f"{round(bins[i],1)}-{round(bins[i+1],1)}" for i in range(len(bins)-1)],
            'values': counts.tolist()
        }
    return charts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Fichier vide'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format non supporté (CSV, XLSX seulement)'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    try:
        df = pd.read_csv(filepath) if filename.endswith('.csv') else pd.read_excel(filepath)
        df = df.dropna(how='all')
        stats, numeric_cols = compute_stats(df)
        charts = df_to_charts(df, numeric_cols)
        return jsonify({'success': True, 'filename': filename, 'rows': len(df),
            'columns': df.columns.tolist(), 'numeric_cols': numeric_cols,
            'stats': stats, 'charts': charts, 'preview': df.head(10).to_dict(orient='records')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manual', methods=['POST'])
def manual():
    data = request.json
    records = data.get('records', [])
    if not records:
        return jsonify({'error': 'Aucune donnée fournie'}), 400
    try:
        df = pd.DataFrame(records)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        stats, numeric_cols = compute_stats(df)
        charts = df_to_charts(df, numeric_cols)
        return jsonify({'success': True, 'filename': 'Saisie manuelle', 'rows': len(df),
            'columns': df.columns.tolist(), 'numeric_cols': numeric_cols,
            'stats': stats, 'charts': charts, 'preview': df.head(10).to_dict(orient='records')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample')
def sample():
    np.random.seed(42)
    n = 150
    villes = ['Yaoundé','Douala','Bafoussam','Garoua','Maroua','Bamenda','Ngaoundéré','Bertoua']
    axes = ['N1 Yaoundé–Douala','N3 Yaoundé–Bafoussam','N1 Douala–Bafoussam','N6 Bafoussam–Bamenda','N14 Douala–Limbé','Urbaine Yaoundé','Urbaine Douala']
    gravites = ['Léger','Moyen','Grave','Mortel']
    causes = ['Excès de vitesse','Alcool','Distraction','Mauvais état route','Défaillance mécanique','Surcharge']
    engins = ['Moto-taxi','Véhicule léger','Camion lourd','Bus/Car','Minibus']
    df = pd.DataFrame({
        'Ville': np.random.choice(villes, n),
        'Axe': np.random.choice(axes, n),
        'Heure': np.random.randint(0, 24, n),
        'Vehicules_impliques': np.random.randint(1, 6, n),
        'Blesses': np.random.randint(0, 10, n),
        'Deces': np.random.poisson(0.8, n),
        'Gravite': np.random.choice(gravites, n, p=[0.35,0.30,0.25,0.10]),
        'Engin': np.random.choice(engins, n, p=[0.43,0.22,0.14,0.09,0.12]),
        'Cause': np.random.choice(causes, n),
    })
    stats, numeric_cols = compute_stats(df)
    charts = df_to_charts(df, numeric_cols)
    return jsonify({'success': True, 'filename': 'Données exemple — TraficStatCameroun',
        'rows': len(df), 'columns': df.columns.tolist(), 'numeric_cols': numeric_cols,
        'stats': stats, 'charts': charts, 'preview': df.head(10).to_dict(orient='records')})

if __name__ == '__main__':
    app.run(debug=False)
