#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py crear_superusuario_inicial

if [ "$CARGAR_DATOS_EJEMPLO" = "True" ]; then
    python manage.py cargar_datos_ejemplo
fi
