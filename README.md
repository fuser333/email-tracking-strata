# Email Tracking Strata

Servicio de tracking de emails y formulario de embajadores para Strata.

## Endpoints:

- `/track/<id>` - Pixel de tracking
- `/formulario-embajador?id=<tracking_id>` - Formulario embajador
- `/dashboard` - Ver submissions

## Deploy en Render:

1. Conectar este repo
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn app:app`
