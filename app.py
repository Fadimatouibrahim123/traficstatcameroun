from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

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
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        df = df.dropna(how='all')
        stats, numeric_cols = compute_stats(df)
        charts = df_to_charts(df, numeric_cols)
        preview = df.head(10).to_dict(orient='records')
        columns = df.columns.tolist()

        return jsonify({
            'success': True,
            'filename': filename,
            'rows': len(df),
            'columns': columns,
            'numeric_cols': numeric_cols,
            'stats': stats,
            'charts': charts,
            'preview': preview
        })
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
        preview = df.head(10).to_dict(orient='records')
        return jsonify({
            'success': True,
            'filename': 'Saisie manuelle',
            'rows': len(df),
            'columns': df.columns.tolist(),
            'numeric_cols': numeric_cols,
            'stats': stats,
            'charts': charts,
            'preview': preview
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sample')
def sample():
    np.random.seed(42)
    n = 120
    df = pd.DataFrame({
        'Heure': np.tile(np.arange(0, 24), 5),
        'Vehicules_par_heure': np.random.randint(20, 500, n),
        'Vitesse_moyenne_kmh': np.random.normal(45, 15, n).clip(5, 130).round(1),
        'Accidents': np.random.poisson(0.3, n),
        'Duree_embouteillage_min': np.random.exponential(12, n).round(1),
        'Taux_occupation_pct': np.random.uniform(10, 100, n).round(1),
    })
    stats, numeric_cols = compute_stats(df)
    charts = df_to_charts(df, numeric_cols)
    preview = df.head(10).to_dict(orient='records')
    return jsonify({
        'success': True,
        'filename': 'Données exemple — TradiStatCameroun',
        'rows': len(df),
        'columns': df.columns.tolist(),
        'numeric_cols': numeric_cols,
        'stats': stats,
        'charts': charts,
        'preview': preview
    })

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
