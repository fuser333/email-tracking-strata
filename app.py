#!/usr/bin/env python3
"""
Email Tracking + Formulario Embajador - STRATA
Similar a email-tracking-h3l-imagemia pero para Strata
"""

from flask import Flask, request, send_file, render_template_string, jsonify, redirect, send_from_directory
from datetime import datetime
import csv
import os
from io import BytesIO

app = Flask(__name__)

# Archivo para guardar submissions
SUBMISSIONS_FILE = 'embajadores_strata.csv'

# Inicializar CSV si no existe
if not os.path.exists(SUBMISSIONS_FILE):
    with open(SUBMISSIONS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'timestamp', 'nombre', 'email', 'telefono', 'cargo', 
            'organizacion', 'tipo_org', 'profesion', 'num_miembros',
            'ciudad', 'plan_promocion', 'tracking_id', 'ip_address'
        ])

# Pixel de tracking (1x1 transparente)
TRACKING_PIXEL = BytesIO(
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
    b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
)

@app.route('/')
def index():
    return redirect('https://strata.h3l.ai')

@app.route('/track/<tracking_id>')
def track(tracking_id):
    """Pixel de tracking para emails"""
    # Guardar tracking
    with open('tracking_strata.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            tracking_id,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        ])
    
    TRACKING_PIXEL.seek(0)
    return send_file(TRACKING_PIXEL, mimetype='image/gif')

@app.route('/formulario-embajador')
def formulario_embajador():
    """Formulario para embajadores Strata con EmailJS"""
    return send_from_directory('.', 'formulario_emailjs.html')

@app.route('/submit-embajador', methods=['POST'])
def submit_embajador():
    """Guardar submission de embajador (solo CSV, email lo envía EmailJS)"""
    data = request.form

    try:
        # Guardar en CSV para el dashboard
        with open(SUBMISSIONS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                data.get('nombre', ''),
                data.get('email', ''),
                data.get('telefono', ''),
                data.get('cargo', ''),
                data.get('organizacion', ''),
                data.get('tipo_org', ''),
                data.get('profesion', ''),
                data.get('num_miembros', ''),
                data.get('ciudad', ''),
                data.get('plan_promocion', ''),
                data.get('tracking_id', ''),
                request.remote_addr
            ])

        print(f"✅ Embajador guardado en CSV: {data.get('nombre')} - {data.get('organizacion')}")
        return jsonify({'success': True, 'message': 'Datos guardados correctamente'})

    except Exception as e:
        print(f"❌ Error guardando en CSV: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Dashboard para ver submissions"""
    # Leer CSV
    submissions = []
    if os.path.exists(SUBMISSIONS_FILE):
        with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
    
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Embajadores Strata</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .header {{ background: linear-gradient(to right, #3B82F6, #A855F7); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        h1 {{ font-size: 24px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ color: #666; font-size: 14px; margin-bottom: 8px; }}
        .stat-card p {{ font-size: 32px; font-weight: bold; color: #3B82F6; }}
        table {{ width: 100%; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #3B82F6; color: white; padding: 12px; text-align: left; font-size: 13px; }}
        td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 13px; }}
        tr:hover {{ background: #f9fafb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Dashboard Embajadores Strata</h1>
        <p style="margin-top: 8px; font-size: 14px; opacity: 0.9;">Programa de Embajadores Oficiales</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>Total Solicitudes</h3>
            <p>{len(submissions)}</p>
        </div>
        <div class="stat-card">
            <h3>Hoy</h3>
            <p>{len([s for s in submissions if s.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))])}</p>
        </div>
    </div>
    
    <table>
        <tr>
            <th>Fecha</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Organización</th>
            <th>Cargo</th>
            <th>Teléfono</th>
        </tr>'''
    
    for s in reversed(submissions[-50:]):  # Últimos 50
        html += f'''
        <tr>
            <td>{s.get('timestamp', '')[:16]}</td>
            <td>{s.get('nombre', '')}</td>
            <td>{s.get('email', '')}</td>
            <td>{s.get('organizacion', '')}</td>
            <td>{s.get('cargo', '')}</td>
            <td>{s.get('telefono', '')}</td>
        </tr>'''
    
    html += '''
    </table>
</body>
</html>'''
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
