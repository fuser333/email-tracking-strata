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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configuración SMTP (usar variables de entorno en producción)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'mail.spacemail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SMTP_USER = os.getenv('SMTP_USER', 'ceo@h3l.ai')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'dexfan-zinhyW-2quxba')
NOTIFY_EMAIL = os.getenv('NOTIFY_EMAIL', 'info@h3l.ai')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'ceo@h3l.ai')

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

def enviar_notificacion_embajador(data):
    """Envía email a info@h3l.ai cuando alguien llena el formulario"""
    try:
        # Crear mensaje HTML
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #3B82F6, #A855F7); border-radius: 10px;">
        <h1 style="color: #fff; text-align: center; margin-bottom: 20px;">🎁 Nuevo Embajador Strata</h1>
    </div>

    <div style="max-width: 600px; margin: 20px auto; padding: 30px; background: #fff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #3B82F6; border-bottom: 3px solid #A855F7; padding-bottom: 10px;">Información del Embajador</h2>

        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff; width: 40%;">Nombre:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('nombre', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Email:</td>
                <td style="padding: 10px; background: #f9fafb;"><a href="mailto:{data.get('email', '')}" style="color: #3B82F6;">{data.get('email', 'N/A')}</a></td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Teléfono:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('telefono', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Cargo:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('cargo', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Organización:</td>
                <td style="padding: 10px; background: #f9fafb;"><strong>{data.get('organizacion', 'N/A')}</strong></td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Tipo:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('tipo_org', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Profesión/Sector:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('profesion', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Nº Miembros:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('num_miembros', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold; background: #f0f9ff;">Ciudad:</td>
                <td style="padding: 10px; background: #f9fafb;">{data.get('ciudad', 'N/A')}</td>
            </tr>
        </table>

        <div style="margin-top: 30px; padding: 20px; background: #ecfdf5; border-left: 4px solid #059669; border-radius: 5px;">
            <h3 style="color: #059669; margin-top: 0;">Plan de Promoción:</h3>
            <p style="white-space: pre-wrap; color: #333;">{data.get('plan_promocion', 'No especificado')}</p>
        </div>

        <div style="margin-top: 30px; padding: 15px; background: #fef3c7; border-left: 4px solid #F59E0B; border-radius: 5px;">
            <p style="margin: 0; color: #92400E;"><strong>Tracking ID:</strong> {data.get('tracking_id', 'N/A')}</p>
            <p style="margin: 5px 0 0 0; color: #92400E;"><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>

        <div style="margin-top: 30px; text-align: center;">
            <a href="https://email-tracking-strata.onrender.com/dashboard"
               style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #3B82F6, #A855F7); color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold;">
                Ver Dashboard Completo
            </a>
        </div>
    </div>

    <div style="max-width: 600px; margin: 20px auto; text-align: center; color: #666; font-size: 12px;">
        <p>Email automático del sistema de tracking Strata</p>
        <p>© 2026 H3L AI Solutions - <a href="https://strata.h3l.ai" style="color: #3B82F6;">strata.h3l.ai</a></p>
    </div>
</body>
</html>
"""

        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Strata Embajadores <{FROM_EMAIL}>"
        msg['To'] = NOTIFY_EMAIL
        msg['Subject'] = f"🎁 Nuevo Embajador: {data.get('organizacion', 'Sin nombre')} - {data.get('nombre', 'Desconocido')}"
        msg['Reply-To'] = data.get('email', FROM_EMAIL)

        # Adjuntar HTML
        msg.attach(MIMEText(html_body, 'html'))

        # Enviar
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [NOTIFY_EMAIL], msg.as_string())
        server.quit()

        print(f"✅ Email enviado a {NOTIFY_EMAIL} - Embajador: {data.get('nombre')}")
        return True

    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

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

    # Enviar notificación por email a info@h3l.ai
    try:
        enviar_notificacion_embajador(data)
    except Exception as e:
        print(f"⚠️ Error al enviar notificación: {e}")
        # No fallar si el email no se envía, continuar normalmente

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
