# ScraperAPI

Esta aplicación es una API desarrollada con **FastAPI** que permite recibir una categoría del blog de Xepelin y un webhook, realizar scraping sobre los artículos de dicha categoría y luego enviar los resultados a una hoja de cálculo de Google Sheets. Al finalizar el proceso, se notifica al webhook entregado.

## ¿Qué hace esta aplicación?

- Recibe una categoría del blog de Xepelin (`https://xepelin.com/blog/`) y un webhook.
- Realiza scraping de todos los artículos de la categoría.
- Extrae la siguiente información:
  - Título del artículo
  - Categoría
  - Nombre del autor
  - Cargo del autor (Este campo reemplaza fecha de publicación que no se encontró al momento de hacer la App)
  - Tiempo estimado de lectura
- Escribe los resultados en una hoja de cálculo de Google Sheets.
- Envía una notificación al webhook entregado, incluyendo:
  - Link al documento con los resultados
  - Correo de contacto

## Endpoints disponibles

### POST /blog-scraper

Este endpoint espera un JSON con los siguientes campos:

```json
{
  "category": "Pymes y Negocios",
  "webhook": "https://webhook.site/tu-url",
  "email": "ejemplo@email.com"
}
```

- `category`: **(obligatorio)** nombre de la categoría del blog.
- `webhook`: **(obligatorio)** URL válida a la que se notificará una vez terminado el scraping.
- `email`: *(opcional)* correo de quien solicita la operación. Si no se incluye, se usará un correo por defecto configurado por la aplicación.

La respuesta al webhook se envía con el siguiente formato:

```json
{
  "email": "ejemplo@email.com",
  "link": "https://docs.google.com/spreadsheets/d/ID_SHEET"
}
```

### GET /slugs

Este endpoint devuelve el mapa actualizado de slugs del blog. Internamente, la aplicación realiza scraping periódico de los encabezados del sitio principal del blog de Xepelin, lo que permite **adaptarse dinámicamente a nuevas categorías** sin necesidad de actualizar manualmente la aplicación.

### GET /docs

Contiene documentación interactiva de la API, nativa de FastAPI. 

## Manejo del Scraping en Segundo Plano

Actualmente, el proceso de scraping se ejecuta como una tarea en segundo plano utilizando `BackgroundTasks` de FastAPI. Esto permite que el endpoint `/blog-scraper` responda rápidamente al usuario mientras el scraping y posterior carga en Google Sheets se realiza de forma asíncrona. Esta decisión fue tomada por tiempo y rapidez de implementación, dado que es liviano e integrado a FastApi.

Con más tiempo y para escalar de manera robusta, se implementaría ejecución del scraping en un **worker** dedicado. Esto se podría lograr mediante:

- **Celery** como gestor de tareas distribuidas.
- **Redis** como broker de mensajes.

Esto permitiría tanto escalar en caso de necesitarlo y también manejar mejor múltiples solicitudes.

Para esto habría que:
- Separar el `run_scraping_flow` como una tarea registrada en Celery.
- Configurar un broker (Redis).
- Ajustar el endpoint para que encole la tarea (`delay()` o `apply_async`) en lugar de usar `BackgroundTasks`.
- Agregar un proceso adicional en el `Dockerfile` o `docker-compose.yml` para levantar el worker de Celery junto a la app.

Esta estructura sería más robusta en entornos productivos donde se espera scraping más intensivo.


## Cómo levantar en local

Esta aplicación está **contenedorizada**, por lo que puedes levantarla usando Docker. Debes crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
GOOGLE_CREDS_PATH=
GOOGLE_SPREADSHEET_URL=
REQUEST_EMAIL=
```
