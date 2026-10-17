---
title: "Referencia de la API del servidor MCP de Scrapling"
description: "Consulta las herramientas del servidor MCP y sus modelos de solicitudes, respuestas y sesiones para extraer datos con HTTP o navegadores."
---

# Referencia del servidor MCP {#mcp-server-api-reference}

El **servidor MCP de Scrapling** ofrece dieciséis herramientas para extraer datos e interactuar con el navegador mediante Model Context Protocol (MCP). Integra Scrapling en asistentes y agentes de IA para extraer datos mediante conversaciones, con funciones para evitar la detección de bots.

Inicia el servidor MCP con este comando:

```bash
scrapling mcp
```

O importa la clase del servidor directamente:

```python
from scrapling.core.ai import ScraplingMCPServer

server = ScraplingMCPServer()
server.serve(http=False, host="127.0.0.1", port=8000)
```

Para usar tu propio ejecutable de navegador compatible con Chromium, pasa `executable_path`:

```python
server = ScraplingMCPServer(executable_path="/path/to/chromium")
```

## Modelo de respuesta {#response-model}

Las herramientas de obtención de páginas y solicitudes HTTP devuelven esta estructura, con una respuesta por llamada. Las herramientas de gestión de sesiones usan los modelos siguientes. `browser_screenshot` devuelve una imagen de la página o de un elemento, junto con la URL actual, como bloques de imagen y texto. `browser_extract` y `browser_actions` devuelven texto plano. Las dos herramientas de red devuelven JSON estructurado mediante los modelos siguientes. `browser_evaluate` devuelve el resultado como JSON dentro de un bloque de texto.

## ::: scrapling.core.ai.server.ResponseModel
    handler: python
    :docstring:

## Modelos de solicitudes de red {#network-request-models}

`browser_network_requests` devuelve `NetworkRequestsModel` con `requests`, `next_cursor`, `has_more` y `dropped_count`. Cada `NetworkRequestInfo` contiene `id`, `url`, `method`, `resource_type` y `status`. Para continuar, pasa `next_cursor` como `after_id`. `has_more` indica si hay más coincidencias en el historial actual.

`browser_network_request` devuelve `NetworkRequestModel` con `request_id`, `part`, `data` y `note`. Los resúmenes y las cabeceras son objetos. El contenido completo guardado se devuelve como una cadena, incluso si la respuesta contiene JSON. `note` explica si faltan datos del contenido o si las cabeceras están incompletas.

## ::: scrapling.core.ai._network_formatting.NetworkRequestInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.NetworkRequestsModel
    handler: python
    :docstring:

## ::: scrapling.core.ai._network_formatting.NetworkRequestModel
    handler: python
    :docstring:

## Modelos de sesiones {#session-models}

Clases de modelos para gestionar sesiones:

## ::: scrapling.core.ai.server.SessionInfo
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionCreatedModel
    handler: python
    :docstring:

## ::: scrapling.core.ai.server.SessionClosedModel
    handler: python
    :docstring:

## Clase del servidor MCP {#mcp-server-class}

La clase principal del servidor MCP ofrece las siguientes herramientas:

- **`make_request`**: Obtiene una URL por HTTP con imitación de navegador y cierre automático del cliente. Admite GET, POST, PUT y DELETE.
- **`browser_fetch_once`**: Obtiene una URL con un navegador sigiloso, ejecuta JavaScript, gestiona Cloudflare y cierra el navegador. Usa una sesión persistente si necesitas realizar acciones después o consultar el historial de red.

- **`browser_extract`**: Lee la página actual o un elemento como una instantánea para IA, HTML, Markdown o texto, sin recargar. Conserva los resultados de formularios y acciones. Las instantáneas incluyen roles, nombres, referencias, posiciones y tamaños de los elementos. La búsqueda con expresiones regulares devuelve las líneas coincidentes, el contexto cercano y los nodos padre.
- **`browser_actions`**: Encadena movimientos del ratón, acciones al pasar el cursor, clics, desplazamientos, llenado de campos, atajos de teclado, respuestas a diálogos y esperas en una llamada. Acepta o descarta alertas y confirmaciones, o escribe en diálogos de entrada. Puedes llenar una búsqueda, enviarla, esperar y abrir un resultado sin una llamada por paso.

    Los movimientos y clics admiten selectores, referencias de instantáneas o coordenadas. La herramienta espera a los elementos y los lleva a la vista. Admite movimientos por pasos, clics izquierdo, derecho y central, doble clic y desplazamiento en paneles anidados.

    Selecciona campos mediante selectores o referencias de instantáneas. Escribe texto, marca o desmarca casillas, selecciona botones de opción y elige una o varias opciones de listas nativas por su etiqueta. Sustituye o borra el texto, o escribe en la posición del cursor. Los atajos usan el foco actual. El modo lento añade pausas aleatorias entre los caracteres y las acciones.

    Espera al contenido o a que desaparezcan los indicadores de carga mediante selectores o referencias de instantáneas. También puedes esperar a eventos de carga, a que termine la actividad de red o durante un tiempo fijo.

- **`browser_evaluate`**: Ejecuta JavaScript en la página actual para extraer datos personalizados, calcular resultados, leer el estado de la aplicación o modificar el contenido. Admite scripts asíncronos y devuelve sus resultados como JSON.
- **`browser_network_requests`**: Busca solicitudes de navegador completadas entre pestañas, navegaciones y acciones. Encuentra llamadas API, errores HTTP y redirecciones guardadas. Oculta los recursos estáticos de forma predeterminada para reducir los resultados. Omite las solicitudes fallidas o incompletas. Devuelve datos estructurados con paginación.
- **`browser_network_request`**: Lee el resumen, las cabeceras, los datos enviados o el contenido de texto de una solicitud guardada como JSON estructurado, sin repetirla. Devuelve la parte elegida completa. Las respuestas guardadas siguen disponibles después de cambiar de página, incluidas las respuestas HTTP 4xx y 5xx. Las entradas aparecen cuando termina la captura. Consultar el historial o cerrar la sesión no espera a las capturas pendientes, que pueden perderse al navegar o cerrar. Los bytes proceden de Playwright y pueden ser distintos de los enviados por el servidor. El texto usa la decodificación UTF-8 de Playwright cuando es válida; en otro caso, usa el charset declarado. Solo se lee y guarda el contenido con un `Content-Type` de texto compatible. Para los tipos binarios, ausentes o desconocidos, se conservan los metadatos y las cabeceras sin leer el contenido. Esto no cambia la carga de la página. El historial tiene límites de tamaño. Una nota opcional explica si el contenido no es texto, es demasiado grande o no se puede leer. Lee los datos que necesitas antes de cerrar la sesión MCP.
- **`browser_fetch`**: Obtiene una página mediante una sesión de navegador sigiloso abierta y extrae HTML, Markdown, texto o una instantánea estructurada. Las instantáneas pueden cubrir toda la página o un elemento, e incluyen referencias, posiciones y tamaños para interactuar después.

## ::: scrapling.core.ai.server.ScraplingMCPServer
    handler: python
    :docstring:
