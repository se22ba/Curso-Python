# Mapa Vecinal — Blog de Seguridad Vecinal

Blog comunitario donde cada entrada es un reporte de un incidente de
seguridad (robo, hurto, vandalismo, actividad sospechosa) geolocalizado
en un mapa interactivo. Proyecto final del curso de Django.

> **¿Solo necesitás verificar que el proyecto funciona, sin instalar
> nada?** Ver [`VERIFICACION_MANUAL.md`](./VERIFICACION_MANUAL.md):
> una guía paso a paso pensada para perfiles no técnicos, que solo
> requiere un navegador y la URL pública del proyecto.

## Funcionalidades

- **Panel de administración**: gestión de entradas del blog, perfiles
  de usuario y mensajes de contacto desde `/admin/`.
- **Perfiles de usuario**: cada usuario tiene un perfil público con
  biografía, barrio y avatar, editable por su propietario.
- **Registro, login y logout**: autenticación completa con Django Auth.
- **Páginas públicas**: listado y detalle de entradas del blog (con
  mapa interactivo), página "Acerca de" y "Contacto", todas accesibles
  sin necesidad de cuenta.
- **Formularios con validación**: registro, login, contacto y
  publicación de entradas, todos con validación de datos.
- **Mapa interactivo**: cada entrada del blog se geolocaliza con
  Leaflet + OpenStreetMap (sin costo, sin API key).
- **Administración de usuarios extendida**: el panel admin muestra,
  para cada usuario, su fecha de alta y cuántas entradas publicó, y
  permite editar su perfil (biografía, barrio, avatar) desde la misma
  pantalla.
- **Protección contra spam**: límite de publicaciones por usuario
  (cooldown entre entradas + tope diario) y sistema de reportes
  comunitarios que oculta automáticamente una entrada tras varios
  reportes de usuarios distintos.

## Estructura

```
mapa_delito/
├── config/                  # settings, urls, wsgi
├── incidentes/               # entradas del blog (CRUD + mapa + búsqueda)
│   ├── models.py               # Incidente + ReporteIncidente
│   ├── forms.py
│   ├── views.py                # incluye rate limiting y reportar_incidente
│   ├── admin.py
│   ├── tests.py
│   ├── management/commands/cargar_datos_ejemplo.py
│   └── templates/incidentes/
├── usuarios/                 # registro, login, logout, perfil
│   ├── models.py              # Perfil + signal de creación automática
│   ├── forms.py
│   ├── views.py
│   ├── admin.py                # UserAdmin extendido con inline de Perfil
│   ├── tests.py
│   ├── management/commands/crear_superusuario_inicial.py
│   └── templates/usuarios/
├── paginas/                  # Acerca de + Contacto
│   ├── models.py               # MensajeContacto
│   ├── forms.py
│   ├── views.py
│   ├── tests.py
│   └── templates/paginas/
├── templates/base.html
├── static/css/base.css
├── manage.py
├── requirements.txt
├── requirements-dev.txt
├── build.sh                  # script de build para Render
├── Procfile                   # comando de arranque para Render/Heroku-like
├── render.yaml                 # Blueprint de Render (deploy con un click)
├── VERIFICACION_MANUAL.md       # guía de pruebas para perfiles no técnicos
├── .env.example
└── .gitignore
```

## 1. Instalación local

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Variables de entorno

```bash
cp .env.example .env
```

Generar una `SECRET_KEY` nueva:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Pegar el resultado en `.env`:

| Variable        | Ejemplo                  | Notas                                          |
|------------------|---------------------------|---------------------------------------------------|
| `SECRET_KEY`     | (generada con el comando) | Obligatoria.                                       |
| `DEBUG`          | `True`                    | `True` solo en desarrollo local.                    |
| `ALLOWED_HOSTS`  | `localhost,127.0.0.1`     | Lista separada por comas, sin espacios.            |

Si falta `SECRET_KEY`, el proyecto falla al arrancar con un mensaje
explícito en lugar de un error críptico.

## 3. Migraciones

```bash
python manage.py migrate
```

Por defecto usa SQLite si no hay `DATABASE_URL` definida (ver sección
de despliegue para producción con Postgres).

## 4. Superusuario

```bash
python manage.py createsuperuser
```

## 5. Datos de ejemplo

```bash
python manage.py cargar_datos_ejemplo
```

Crea 5 entradas de ejemplo geolocalizadas en distintos puntos de CABA
(con categorías y severidades variadas) y un usuario de demo:

| Usuario       | Contraseña      |
|----------------|-------------------|
| `vecino_demo`  | `VecinoDemo123`   |

## 6. Ejecutar

```bash
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/` — redirige al blog (`/incidentes/`).

## URLs principales

| Ruta                         | Descripción                                    | Acceso                              |
|--------------------------------|---------------------------------------------------|-----------------------------------------|
| `/`                             | Redirige al blog                                    | Público                                  |
| `/incidentes/`                  | Listado de entradas + mapa interactivo              | Público                                  |
| `/incidentes/<id>/`             | Detalle de una entrada                              | Público                                  |
| `/incidentes/nuevo/`            | Publicar nueva entrada                              | Requiere login                           |
| `/incidentes/<id>/editar/`      | Editar entrada                                      | Login + ser el autor                     |
| `/incidentes/<id>/eliminar/`    | Eliminar entrada                                    | Login + ser el autor                     |
| `/usuarios/registro/`           | Crear cuenta                                         | Público                                  |
| `/usuarios/login/`              | Iniciar sesión                                       | Público                                  |
| `/usuarios/logout/`             | Cerrar sesión                                        | Login                                    |
| `/usuarios/perfil/<username>/`  | Ver perfil público                                   | Público                                  |
| `/usuarios/perfil/editar/`      | Editar mi perfil                                     | Login                                    |
| `/acerca-de/`                   | Página estática                                       | Público                                  |
| `/contacto/`                    | Formulario de contacto                                | Público                                  |
| `/admin/`                       | Panel de administración                               | Superusuario / staff                    |

## Búsqueda dinámica

El listado del blog permite filtrar por título (`icontains`), categoría
y severidad, combinados con AND:

```
/incidentes/?titulo=robo
/incidentes/?categoria=vandalismo
/incidentes/?titulo=plaza&severidad=alta
```

## Mapa interactivo

Implementado con [Leaflet](https://leafletjs.com/) y tiles de
OpenStreetMap, cargados vía CDN (sin necesidad de API key ni costo):

- En el listado, cada entrada se muestra como un marcador coloreado
  según su severidad (verde = baja, ámbar = media, rojo = alta), con
  un popup que enlaza al detalle.
- Al crear o editar una entrada, el formulario muestra un mapa donde
  se fija la ubicación haciendo click; los campos de latitud/longitud
  se completan automáticamente y son de solo lectura.
- En el detalle, se muestra un mapa centrado en la ubicación exacta
  del incidente.
- Los tres mapas (listado, formulario, detalle) cargan Leaflet sin el
  atributo `integrity` (verificación criptográfica de subrecurso): un
  hash desactualizado respecto a lo que sirve el CDN bloquea la carga
  del script de forma silenciosa, dejando el mapa vacío sin ningún
  error visible. Si la librería no llega a cargar por cualquier otro
  motivo de red, se muestra un mensaje explícito en el recuadro del
  mapa en lugar de un espacio vacío sin explicación.

## Moderación y protección contra spam

- **Límite de publicaciones (rate limiting)**: un usuario no puede
  publicar más de una entrada cada 5 minutos, ni más de 5 entradas
  por día. Si excede alguno de los dos límites, el formulario muestra
  un mensaje claro indicando cuándo puede volver a intentarlo.
- **Reportes comunitarios**: cualquier usuario logueado (que no sea
  el autor) puede reportar una entrada desde su página de detalle.
  Tras 3 reportes de usuarios distintos, la entrada se oculta
  automáticamente del mapa y del listado público, pero el autor y el
  staff siguen pudiendo verla (para que el autor sepa qué pasó, y el
  staff pueda revisarla desde `/admin/`). Un mismo usuario no puede
  reportar la misma entrada dos veces.
- **Revisión desde el admin**: `IncidenteAdmin` muestra el estado
  "oculto por reportes" en el listado y permite revertirlo
  manualmente (por si los reportes fueron maliciosos o erróneos), y
  cada entrada incluye en línea el detalle de quién la reportó y
  cuándo.

## Seguridad

- `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` se leen desde variables de
  entorno, nunca hardcodeadas en el código.
- Contraseñas validadas con los validadores estándar de Django
  (longitud mínima, similitud con datos del usuario, contraseñas
  comunes, no completamente numéricas).
- CSRF habilitado en todos los formularios POST (incluyendo logout y
  reportar una entrada, que requieren POST en lugar de un link GET).
- Solo el autor de una entrada puede editarla o eliminarla
  (`UserPassesTestMixin` personalizado), devolviendo `403` si otro
  usuario lo intenta.
- Una entrada oculta por reportes devuelve `404` a cualquier visitante
  que no sea el autor o staff, incluso si tiene el link directo.
- En producción (`DEBUG=False`) se activan automáticamente:
  redirección forzada a HTTPS, cookies de sesión y CSRF marcadas como
  seguras, HSTS, protección contra MIME-sniffing y `X-Frame-Options: DENY`.

## Pruebas

```bash
pip install -r requirements-dev.txt
python manage.py test
```

78 tests cubriendo las tres apps con **100% de cobertura de líneas**
(medido con `coverage`, no estimado):

```bash
coverage run --source='incidentes,usuarios,paginas' manage.py test
coverage report -m
```

Cubren, entre otros casos:
- Modelos (`__str__`, ordenamiento, `get_absolute_url`).
- Validación de formularios (rangos de coordenadas, longitud mínima
  de mensaje, formato de email).
- Acceso público vs. protegido en cada vista.
- Que un usuario no pueda editar ni eliminar entradas de otro
  (403 explícito).
- Búsqueda dinámica por título, categoría y severidad.
- Creación automática de `Perfil` al registrarse (signal).
- Registro, login (incluyendo `?next=`), logout (incluyendo que
  requiere `POST`).
- El comando `cargar_datos_ejemplo`, incluyendo que correrlo dos veces
  no duplica datos.
- Rate limiting: cooldown entre publicaciones, tope diario, y que una
  publicación pasado el cooldown se permite con normalidad.
- Sistema de reportes: que el autor no pueda reportar su propia
  entrada, que un usuario no pueda reportar dos veces, ocultamiento
  automático al alcanzar el umbral de reportes, y que una entrada
  oculta devuelva 404 a terceros pero siga visible para el autor y
  para staff.
- Admin de usuarios: que el listado muestre la cantidad de entradas
  publicadas, y que la edición de un usuario incluya el inline de
  `Perfil`.

## Despliegue en Render (URL pública)

El proyecto incluye `render.yaml`, así que se puede desplegar como
**Blueprint** sin configurar nada manualmente:

1. Subir el proyecto a un repositorio de GitHub.
2. Entrar a [render.com](https://render.com) y crear una cuenta
   gratuita (no pide tarjeta).
3. Ir a **New > Blueprint**, conectar el repositorio de GitHub.
4. Render detecta `render.yaml` automáticamente y propone crear:
   - Un **Web Service** gratuito (ejecuta `build.sh` y luego
     `gunicorn config.wsgi:application`).
   - Una base de datos **PostgreSQL** gratuita (Render free tier tiene
     filesystem efímero, así que SQLite perdería los datos en cada
     redeploy; por eso el proyecto usa `DATABASE_URL` automáticamente
     si está presente).
5. Confirmar la creación. Render genera `SECRET_KEY` automáticamente
   (ver `render.yaml`) y conecta la base de datos sin pasos manuales.
6. Esperar a que termine el build (instala dependencias, corre
   `collectstatic` y `migrate` según `build.sh`).
7. Una vez desplegado, Render entrega una URL pública del estilo
   `https://mapa-vecinal.onrender.com`.
8. El superusuario y los datos de ejemplo se crean automáticamente en
   el propio build (ver siguiente sección): no es necesario usar la
   **Shell** de Render, que solo está disponible en planes pagos.

### Crear el superusuario sin usar Shell (plan gratuito)

El acceso a Shell en Render requiere un plan pago. En el plan
gratuito, `build.sh` corre `python manage.py crear_superusuario_inicial`
en cada deploy, que lee estas variables de entorno y crea el
superusuario solo si todavía no existe (no duplica ni cambia la
contraseña si ya está creado):

1. En el dashboard de Render, abrí tu Web Service → pestaña
   **Environment**.
2. Agregá estas variables:

   | Key | Value |
   |---|---|
   | `DJANGO_SUPERUSER_USERNAME` | el usuario que quieras |
   | `DJANGO_SUPERUSER_EMAIL` | un email cualquiera |
   | `DJANGO_SUPERUSER_PASSWORD` | una contraseña segura |
   | `CARGAR_DATOS_EJEMPLO` | `True` (opcional, carga las 5 entradas de ejemplo) |

3. Guardá. Render redeploya automáticamente al guardar variables de
   entorno; si no lo hace solo, forzalo con **Manual Deploy → Deploy
   latest commit**.
4. Revisá los **Logs** del deploy: deberías ver la línea
   `Superusuario '<tu usuario>' creado correctamente.`
5. Iniciá sesión en `[tu-url]/admin/` con esas credenciales.

Si en el futuro necesitás cambiar la contraseña de ese superusuario,
no alcanza con cambiar la variable de entorno (el comando es
idempotente a propósito y no la va a sobreescribir). Usá en su lugar
`python manage.py changepassword <usuario>` desde una Shell si tenés
plan pago, o borrá el usuario desde `/admin/` con otra cuenta de
superusuario y dejá que el build lo recree con la nueva contraseña.

### Notas sobre el plan gratuito de Render

- El servicio gratuito **se duerme tras 15 minutos sin tráfico** y
  tarda unos segundos en reactivarse con la primera visita; es
  comportamiento esperado del free tier, no un error del proyecto.
- La base de datos Postgres gratuita expira a los 30 días; para una
  entrega académica esto no debería ser un problema, pero si necesitás
  mantenerla más tiempo, recreala desde el dashboard de Render.

## Despliegue manual (sin Blueprint)

Si preferís configurar el servicio a mano en lugar de usar
`render.yaml`:

1. **New > Web Service**, conectar el repo.
2. Build command: `./build.sh`
3. Start command: `gunicorn config.wsgi:application`
4. Variables de entorno a configurar manualmente:
   - `SECRET_KEY`: generar una con el comando de la sección 2.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `DATABASE_URL`: si creás una base Postgres en Render, copiar su
     "Internal Connection String" acá.
   - `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`,
     `DJANGO_SUPERUSER_PASSWORD`: para que el build cree el
     superusuario automáticamente (ver sección anterior).

## Decisiones de diseño

- **`Incidente` como entrada de blog**: cada entrada tiene título,
  cuerpo (descripción), categoría, fecha y autor —la anatomía estándar
  de un post de blog— con el agregado de coordenadas geográficas. El
  mapa es una capa de visualización sobre el mismo contenido, no un
  modelo de datos distinto.
- **Coordenadas como `DecimalField`, no `FloatField`**: evita errores
  de redondeo de punto flotante en datos de geolocalización, donde la
  precisión importa.
- **Selección de ubicación por click en el mapa**, no tipeada a mano:
  los campos de latitud/longitud son de solo lectura en el formulario;
  JavaScript los completa al hacer click en el mapa de Leaflet,
  evitando errores de tipeo en coordenadas.
- **`UserPassesTestMixin` personalizado (`EsAutorMixin`)** en lugar de
  filtrar el queryset por autor: permite devolver `403 Forbidden`
  explícito cuando un usuario autenticado intenta editar contenido de
  otro, en vez de un `404` ambiguo que no distingue "no existe" de
  "no tenés permiso".
- **Signal `post_save` para crear el `Perfil` automáticamente**: evita
  el error clásico de `RelatedObjectDoesNotExist` al acceder a
  `usuario.perfil` si el perfil no se crea en el mismo momento que el
  `User`.
- **`MensajeContacto` persistido en base de datos** en lugar de enviar
  un email: no requiere configurar un servidor SMTP para la entrega
  académica, y permite revisar los mensajes desde el panel admin.
- **`DATABASE_URL` con fallback a SQLite**: el mismo `settings.py`
  funciona en desarrollo local (SQLite, sin configuración) y en
  producción (Postgres, vía la variable que Render inyecta
  automáticamente), sin necesidad de archivos de settings separados.
- **WhiteNoise para archivos estáticos**: evita depender de un
  servicio externo (S3, CDN propio) para servir CSS en producción;
  suficiente para el alcance de este proyecto.
- **`verbose_name`/`verbose_name_plural` explícitos en cada modelo**:
  sin esto, Django pluraliza agregando una simple "s" al nombre de la
  clase, lo que en español da resultados incorrectos como "Perfils"
  o "Mensaje contactos". Definirlos a mano asegura que el panel de
  administración se lea correctamente ("Perfiles", "Mensajes de
  contacto", "Entradas del blog").
- **Guía de verificación manual separada del README técnico**: el
  README está pensado para quien va a instalar y ejecutar el proyecto
  (requiere terminal, Python, variables de entorno); `VERIFICACION_MANUAL.md`
  está pensado para quien solo necesita confirmar que el proyecto
  desplegado funciona, usando únicamente un navegador. Mezclar ambos
  públicos en un solo documento hace que cualquiera de los dos tenga
  que saltarse información que no le sirve.
- **Creación del superusuario vía variables de entorno en el build**,
  no vía Shell: el acceso a Shell en Render requiere un plan pago, así
  que `crear_superusuario_inicial` lee credenciales desde el entorno
  y crea el usuario en cada deploy si todavía no existe. Esto además
  hace que el proyecto se recupere solo si la base gratuita de
  Postgres llegara a reiniciarse, sin pasos manuales adicionales.
- **Rate limiting en la vista, no en el formulario**: `IncidenteForm`
  se reutiliza tanto para crear como para editar. Si el límite de
  publicaciones se validara en el `clean()` del form, también se
  aplicaría al editar una entrada existente, lo cual no tiene
  sentido. Por eso la validación vive en `IncidenteCreateView.form_valid()`,
  que es donde corresponde semánticamente.
- **Ocultamiento automático en lugar de borrado** ante reportes
  comunitarios: el campo `oculto_por_reportes` retira la entrada de
  la vista pública sin destruir el dato, permitiendo que un admin
  revierta la decisión si los reportes fueron maliciosos o erróneos.
  El autor y el staff siguen viendo la entrada oculta; un visitante
  con el link directo recibe `404`, no un mensaje que confirme la
  existencia del contenido oculto.
- **`unique_together` en `ReporteIncidente`** en lugar de validar la
  duplicación a mano: la base de datos garantiza que un usuario no
  pueda reportar la misma entrada dos veces, sin necesidad de una
  consulta adicional antes de cada insert.
- **Sin `integrity` en los `<script>`/`<link>` de Leaflet**: un hash
  de Subresource Integrity desactualizado respecto a lo que sirve el
  CDN bloquea la carga del recurso sin ningún error visible en la
  página — el mapa queda vacío sin pista de qué falló. Para una
  librería pública y estable como Leaflet, el riesgo que mitiga ese
  hash es mucho menor que el costo de que se rompa silenciosamente.

## Reproducir en otra máquina

```bash
git clone <url-del-repo>
cd mapa_delito
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# completar SECRET_KEY en .env (ver sección "Variables de entorno")
python manage.py migrate
python manage.py createsuperuser
python manage.py cargar_datos_ejemplo
python manage.py runserver
```
