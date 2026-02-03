#!/usr/bin/env python3
"""
Email Tracking + Formulario Embajador - STRATA
Similar a email-tracking-h3l-imagemia pero para Strata
"""

from flask import Flask, request, send_file, render_template_string, jsonify, redirect
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
    """Formulario para embajadores Strata"""
    tracking_id = request.args.get('id', '')
    
    html = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formulario Embajador Strata</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #3B82F6 0%, #A855F7 50%, #DB2777 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 {
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(to right, #3B82F6, #A855F7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }
        .logo p { color: #666; font-size: 14px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1.5px; }
        h2 { color: #333; font-size: 24px; margin-bottom: 10px; text-align: center; }
        .subtitle { color: #666; text-align: center; margin-bottom: 30px; font-size: 15px; line-height: 1.6; }
        .highlight-box {
            background: linear-gradient(135deg, #A855F7, #DB2777);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }
        .highlight-box h3 { font-size: 18px; margin-bottom: 10px; }
        .highlight-box p { font-size: 32px; font-weight: bold; margin: 10px 0; }
        .highlight-box small { font-size: 13px; opacity: 0.9; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #333; font-weight: 600; margin-bottom: 8px; font-size: 14px; }
        label .required { color: #DB2777; }
        input, select, textarea {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.3s;
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #3B82F6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        textarea { resize: vertical; min-height: 100px; }
        .checkbox-group {
            display: flex;
            align-items: start;
            gap: 12px;
            margin-top: 20px;
            padding: 16px;
            background: #f9fafb;
            border-radius: 8px;
        }
        .checkbox-group input[type="checkbox"] { width: auto; margin-top: 2px; cursor: pointer; }
        .checkbox-group label { margin: 0; font-weight: 400; font-size: 13px; color: #666; line-height: 1.6; }
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #F97316, #DB2777);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(249, 115, 22, 0.3); }
        button:active { transform: translateY(0); }
        .success { display: none; text-align: center; padding: 40px; }
        .success svg { width: 80px; height: 80px; margin-bottom: 20px; }
        .success h3 { color: #059669; font-size: 24px; margin-bottom: 12px; }
        .success p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>STRATA</h1>
            <p>Programa Embajadores</p>
        </div>

        <div id="formulario">
            <h2>¡Felicidades! 🎉</h2>
            <p class="subtitle">
                Has sido seleccionado para ser <strong>Embajador Oficial de Strata</strong>.
                Completa tus datos para activar tu cuenta gratuita.
            </p>

            <div class="highlight-box">
                <h3>🎁 Tu Beneficio como Embajador</h3>
                <p>Plan Base GRATIS</p>
                <small>Valor: $239.88/año • Acceso completo a Strata</small>
            </div>

            <form id="embajadorForm" method="POST" action="/submit-embajador">
                <input type="hidden" name="tracking_id" value="''' + tracking_id + '''">
                
                <div class="form-group">
                    <label>Nombre completo <span class="required">*</span></label>
                    <input type="text" name="nombre" required placeholder="Ej: Ing. Carlos Mendoza García">
                </div>

                <div class="form-group">
                    <label>Email <span class="required">*</span></label>
                    <input type="email" name="email" required placeholder="tu@email.com">
                </div>

                <div class="form-group">
                    <label>Teléfono / WhatsApp <span class="required">*</span></label>
                    <input type="tel" name="telefono" required placeholder="+593 99 123 4567">
                </div>

                <div class="form-group">
                    <label>Cargo / Posición <span class="required">*</span></label>
                    <select name="cargo" required>
                        <option value="">Selecciona...</option>
                        <option value="presidente">Presidente</option>
                        <option value="vicepresidente">Vicepresidente</option>
                        <option value="director">Director/a</option>
                        <option value="gerente">Gerente General</option>
                        <option value="secretario">Secretario/a</option>
                        <option value="tesorero">Tesorero/a</option>
                        <option value="vocal">Vocal</option>
                        <option value="otro">Otro cargo directivo</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Organización <span class="required">*</span></label>
                    <input type="text" name="organizacion" required placeholder="Ej: Colegio de Ingenieros Civiles de Pichincha">
                </div>

                <div class="form-group">
                    <label>Tipo de organización <span class="required">*</span></label>
                    <select name="tipo_org" required>
                        <option value="">Selecciona...</option>
                        <option value="colegio">Colegio Profesional</option>
                        <option value="camara">Cámara de Comercio/Construcción</option>
                        <option value="asociacion">Asociación Gremial</option>
                        <option value="universidad">Universidad</option>
                        <option value="empresa">Empresa Privada</option>
                        <option value="otro">Otro</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Profesión / Sector <span class="required">*</span></label>
                    <input type="text" name="profesion" required placeholder="Ej: Ingeniería Civil, Derecho, Medicina">
                </div>

                <div class="form-group">
                    <label>Número de miembros/empleados aproximado</label>
                    <input type="number" name="num_miembros" placeholder="Ej: 250" min="1">
                </div>

                <div class="form-group">
                    <label>Ciudad</label>
                    <input type="text" name="ciudad" placeholder="Ej: Quito">
                </div>

                <div class="form-group">
                    <label>¿Cómo planeas promover Strata entre tus miembros?</label>
                    <textarea name="plan_promocion" placeholder="Ej: Email a todos los agremiados, presentación en asamblea mensual, etc."></textarea>
                </div>

                <div class="checkbox-group">
                    <input type="checkbox" id="acepto" name="acepto" required>
                    <label for="acepto">
                        Acepto ser <strong>Embajador Oficial de Strata</strong> y comprometerme a promover la plataforma entre los miembros de mi organización. Entiendo que recibiré el Plan Base gratuito ($19.99/mes) mientras mantenga mi rol activo como embajador.
                    </label>
                </div>

                <button type="submit">🚀 Activar Mi Cuenta de Embajador</button>
            </form>
        </div>

        <div id="success" class="success">
            <svg viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 12l2 2 4-4"/>
            </svg>
            <h3>¡Solicitud Enviada!</h3>
            <p>
                Gracias por unirte al programa de embajadores Strata.<br><br>
                Nuestro equipo revisará tu solicitud y te contactará en las próximas 24-48 horas para activar tu cuenta gratuita.<br><br>
                <strong>Revisa tu email</strong> (incluye spam) para más información.
            </p>
        </div>
    </div>
</body>
</html>'''
    return render_template_string(html)

@app.route('/submit-embajador', methods=['POST'])
def submit_embajador():
    """Guardar submission de embajador"""
    data = request.form
    
    # Guardar en CSV
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
    
    # Redirigir a página de éxito
    return redirect(f'/formulario-embajador?id={data.get("tracking_id", "")}&success=1')

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
