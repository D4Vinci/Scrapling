---
title: "Extrae datos de productos de Shopify con Python"
description: "Extrae el catálogo de una tienda Shopify con ShopifySpider. Indica la URL, recopila las variantes de los productos y consulta los campos de cada elemento."
---

# Plantillas de spiders para plataformas {#platform-spider-templates}

Las plantillas generales resuelven *patrones* de rastreo, como seguir enlaces o recorrer mapas del sitio. Las plantillas para plataformas están pensadas para *plataformas* que usan la misma estructura de datos en muchos sitios independientes. El spider ya sabe dónde buscar los datos. Solo necesitas indicar el dominio.

## ShopifySpider {#shopifyspider}

`ShopifySpider` extrae todos los productos de una tienda Shopify mediante su API JSON, sin usar el HTML del sitio.

```python
from scrapling.spiders import ShopifySpider

class MyStore(ShopifySpider):
    target_website = "example.com"

result = MyStore().start()
print(result.items[0])
```

Asigna el dominio de la tienda a `target_website`. Si está vacío, el spider usa el primer valor de `start_urls` y, si tampoco hay uno, el de `allowed_domains`. Si los tres están vacíos, lanza `ValueError`. Las URL completas se convierten a su dominio de forma automática.

### Cómo funciona {#how-it-works}

1. Recorre las páginas de `https://<store>/collections.json`, con 250 colecciones por página, que es el límite de la plataforma.
2. Para cada colección que indica que tiene productos, recorre las páginas de `/collections/<handle>/products.json`.
3. Entrega un elemento por variante de producto, sin repetir las variantes que aparecen en varias colecciones.

### Campos de cada elemento {#item-fields}

| Campo | Origen |
|-------|--------|
| `name` | Título del producto, más el título de la variante si no es la predeterminada |
| `price` | Precio de la variante, como cadena y tal como lo devuelve Shopify |
| `category` | Identificador de la colección con cada palabra en mayúscula inicial (`summer-sale` se convierte en `Summer Sale`) |
| `brand` | Proveedor del producto |
| `identifier` | ID de la variante |
| `sku` | SKU de la variante, o `""` si la tienda no lo define |
| `stock` | `None` si la variante está disponible, o `0` si está agotada |
| `image_url` | Primera imagen del producto, o `""` |
| `url` | Página del producto dentro de la colección |
| `description` | Contenido de `body_html` del producto, sin las etiquetas HTML |
| `old_price` | `compare_at_price` si es un precio real anterior a la oferta; en caso contrario, `""` |
| `barcode` | Código de barras de la variante, o `""` (la mayoría de las tiendas no lo ofrecen en estos endpoints) |

Estos campos no son obligatorios. Redefine `_process_product()` en tu subclase para cambiar la estructura del elemento o extraer otros campos de los datos del producto.

### Notas y límites {#notes-and-limits}

- Los endpoints JSON solo muestran los productos publicados en el canal de la tienda en línea. Por eso, `products_count` puede ser mayor que el número de productos que realmente se pueden obtener. El spider solo usa un valor distinto de cero como señal para consultar la colección, nunca como un total esperado.
- Es probable que esta plantilla no funcione en tiendas con protecciones adicionales o con contraseña. Si es posible hacerla funcionar, tendrás que redefinir bastantes partes por tu cuenta.
- Se mantienen todas las funciones de `Spider`: configuración de concurrencia, esperas, respeto de robots.txt, puntos de guardado y hooks del ciclo de vida.

### Qué puede ser una plantilla para plataformas {#what-qualifies-as-a-platform-template}

Se aceptan plantillas para plataformas que ofrecen una estructura uniforme y legible por programas en muchos sitios independientes, como Shopify. Los spiders para un solo sitio no forman parte de la biblioteca, por muy popular que sea ese sitio.
