# Guía de Verificación Manual

Esta guía está pensada para revisar que el proyecto funciona
correctamente **sin necesidad de conocimientos técnicos**. Solo hace
falta un navegador y la URL pública del proyecto desplegado en Render.

No es necesario instalar nada, ni abrir una terminal, ni leer código.
Cada fila de las tablas indica un paso a hacer con el mouse/teclado y
qué deberías ver como resultado.

> Reemplazá `[URL-PUBLICA]` por la dirección real del proyecto en
> Render, por ejemplo `https://mapa-vecinal.onrender.com`.

Si la página tarda 20-30 segundos en cargar la primera vez que la
abrís, es normal: el plan gratuito de Render "duerme" el sitio cuando
no recibe visitas y demora unos segundos en reactivarse con la
primera carga.

---

## 1. Panel de administración

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 1.1 | Ir a `[URL-PUBLICA]/admin/` | Una pantalla de login con los campos "Usuario" y "Contraseña" |
| 1.2 | Ingresar con el usuario administrador que te compartieron | Un panel con secciones como "Entradas del blog", "Perfiles", "Mensajes de contacto", "Usuarios" y "Grupos" |
| 1.3 | Hacer click en "Entradas del blog" | Una tabla con las entradas del blog ya cargadas (título, categoría, severidad, autor) |
| 1.4 | Hacer click en cualquier entrada de la lista | Un formulario con todos sus datos, editable desde ahí mismo |
| 1.5 | Volver atrás y hacer click en "Usuarios" (no en "Perfiles") | Una tabla con todas las cuentas registradas: usuario, email, si está activo, fecha de alta y cuántas entradas publicó cada una |
| 1.6 | Hacer click en cualquier usuario de esa lista | Un formulario con sus datos de cuenta, y más abajo una sección "Perfil" con biografía, barrio y avatar editables desde la misma pantalla |

✅ **Resultado esperado:** se puede entrar al panel, gestionar el contenido del blog, y ver/gestionar todos los usuarios registrados (no solo las entradas) sin errores.

> **Aclaración**: la página `/usuarios/perfil/<usuario>/` que ves dentro del sitio público (con el botón "Editar mi perfil") es la página de perfil de **ese usuario en particular**, no el panel de administración. El panel de administración real está siempre en `/admin/`.

---

## 2. Perfiles de usuario

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 2.1 | Ir a `[URL-PUBLICA]/usuarios/perfil/vecino_demo/` | Una página con el nombre de usuario y la lista de entradas que publicó |
| 2.2 | Iniciar sesión con usuario `vecino_demo` y contraseña `VecinoDemo123` (ver paso 3.2) | Quedás logueado, tu nombre de usuario aparece arriba a la derecha |
| 2.3 | Volver a `[URL-PUBLICA]/usuarios/perfil/vecino_demo/` estando logueado | Aparece un botón "Editar mi perfil" que antes no se veía |
| 2.4 | Hacer click en "Editar mi perfil" y completar el campo "Barrio" con cualquier texto, luego "Guardar cambios" | Te lleva de vuelta al perfil y el texto que escribiste aparece ahí |

✅ **Resultado esperado:** cada usuario tiene una página propia con datos editables, y solo puede editar la suya (probá entrando a `/usuarios/perfil/admin/` o el usuario que hayas creado — no debería aparecer el botón de editar si no es tu perfil).

---

## 3. Registro y autenticación

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 3.1 | Ir a `[URL-PUBLICA]/usuarios/registro/` | Un formulario para crear una cuenta nueva (usuario y contraseña, dos veces) |
| 3.2 | Completar con un usuario nuevo y dos contraseñas iguales, enviar | Te redirige a la pantalla de login |
| 3.3 | Iniciar sesión con el usuario que acabás de crear | Tu nombre de usuario aparece en la barra superior, y aparece el botón "Nueva entrada" |
| 3.4 | Hacer click en "Salir" (botón de cerrar sesión, arriba a la derecha) | Volvés a ver "Iniciar sesión" y "Crear cuenta" en la barra superior |
| 3.5 | Repetir el paso 3.2 con el mismo nombre de usuario que ya existe | El formulario muestra un error indicando que ese usuario ya existe, y no te deja avanzar |

✅ **Resultado esperado:** se puede crear una cuenta, iniciar sesión, cerrar sesión, y el sistema rechaza usuarios duplicados.

---

## 4. Páginas públicas

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 4.1 | Ir a `[URL-PUBLICA]/` (sin haber iniciado sesión) | Te redirige al blog, con un mapa interactivo y una lista de entradas, sin pedirte que inicies sesión |
| 4.2 | Hacer click en cualquier marcador del mapa | Aparece un globo con el título de la entrada y un link "Ver detalle" |
| 4.3 | Hacer click en "Ver detalle" o en el título de cualquier entrada de la lista | Se abre la página de esa entrada con toda la información (categoría, severidad, fecha, descripción, autor) y un mapa centrado en esa ubicación |
| 4.4 | Ir a `[URL-PUBLICA]/acerca-de/` | Una página de texto explicando de qué se trata el proyecto |
| 4.5 | Ir a `[URL-PUBLICA]/contacto/` | Un formulario de contacto |

✅ **Resultado esperado:** todo lo anterior se puede ver sin necesidad de iniciar sesión.

---

## 5. Formularios con validación

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 5.1 | Ir a `[URL-PUBLICA]/contacto/`, completar el campo "Email" con algo que no sea un email válido (por ejemplo, "hola"), enviar | El formulario no se envía y muestra un error señalando que el email no es válido |
| 5.2 | Completar el campo "Mensaje" con menos de 10 caracteres (por ejemplo, "hola"), enviar | El formulario muestra un error indicando que el mensaje es demasiado corto |
| 5.3 | Completar el formulario correctamente con todos los campos válidos, enviar | Aparece un mensaje de confirmación de que el mensaje fue enviado |
| 5.4 | Estando logueado, ir a `[URL-PUBLICA]/incidentes/nuevo/` e intentar enviar el formulario sin completar ningún campo | El formulario no se envía y marca en rojo los campos obligatorios faltantes |

✅ **Resultado esperado:** ningún formulario acepta datos inválidos o incompletos.

---

## 6. URL pública

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 6.1 | Abrir `[URL-PUBLICA]` desde el navegador de una computadora distinta a la del desarrollador, o desde el celular, sin estar conectado a la misma red | El sitio carga igual, confirmando que es accesible desde internet y no solo en red local |

✅ **Resultado esperado:** el proyecto es accesible públicamente, no solo en `localhost`.

---

## 7. Moderación y protección contra spam (funcionalidad extra)

Estos pasos requieren dos cuentas distintas. Podés usar `vecino_demo`
(ver paso 3.2 para crear la tuya) y una cuenta nueva que crees vos.

| Paso | Qué hacer | Qué deberías ver |
|---|---|---|
| 7.1 | Logueado con cualquier cuenta, publicá una entrada nueva en `[URL-PUBLICA]/incidentes/nuevo/` | La entrada se publica con éxito y te redirige a su detalle |
| 7.2 | Inmediatamente después, intentá publicar otra entrada nueva | El formulario rechaza la publicación con un mensaje indicando que debés esperar unos minutos |
| 7.3 | Entrá al detalle de una entrada que **no** sea tuya, estando logueado | Aparece un botón "Reportar esta entrada" |
| 7.4 | Hacé click en ese botón | Aparece un mensaje de confirmación ("Gracias, tu reporte fue registrado") y el botón desaparece, reemplazado por un texto que indica que ya la reportaste |
| 7.5 | Con dos cuentas más, reportá esa misma entrada (en total 3 reportes de usuarios distintos) | Al tercer reporte, la entrada deja de aparecer en el mapa y el listado público |
| 7.6 | Iniciá sesión con la cuenta que publicó esa entrada y volvé a su detalle (vas a necesitar el link directo) | El autor sigue pudiendo ver su propia entrada, aunque ya no aparezca en el listado |
| 7.7 | Desde un navegador sin iniciar sesión, intentá abrir el link directo de esa misma entrada oculta | El sitio muestra una página de "no encontrado" (404) |

✅ **Resultado esperado:** un usuario no puede saturar el blog con publicaciones seguidas, y la comunidad puede ocultar colaborativamente una entrada sospechosa sin que un admin tenga que intervenir manualmente en cada caso.

---

## Resumen para copiar al checklist de entrega

| Ítem | Verificado |
|---|---|
| Panel Admin | [ ] |
| Perfiles de Usuario | [ ] |
| Registro y Login | [ ] |
| Páginas Públicas | [ ] |
| Formularios con Validación | [ ] |
| URL Pública | [ ] |
