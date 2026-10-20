# Informe: Dashboard de pedidos de una distribuidora

Trabajo final de Streamlit - Integrantes: Joaquin Papagianacopoulos, Santiago Martire, Agustin Pellegrino

## 1. Objetivo

Armar un dashboard para una distribuidora de golosinas y bebidas que permita responder: cuánto vendemos, cómo evoluciona mes a mes, qué productos y clientes sostienen el negocio, cómo rinde cada vendedor y cómo funciona el armado y reparto de pedidos.

## 2. El dataset

Usamos datos **reales** exportados de la base de pedidos de la distribuidora (archivo `datos/pedidos.csv`). Cada fila es un pedido y tiene 26 columnas: cliente, vendedor, fecha, total, estado, zona, datos de armado y reparto, origen (interno o web) y una columna `items` con el detalle de productos en formato JSON.

- 4790 pedidos, del 21/03/2025 al 20/10/2026.
- 358 clientes distintos.
- Hay un salto en el tiempo: tenemos marzo y abril de 2025 y después desde el 30/04/2026. Los pedidos de 2025 son datos históricos cargados todos juntos, sin vendedor ni zona.

## 3. Tratamiento de datos

La limpieza está en `limpieza.py`.

| Problema | Cantidad | Solución |
|---|---|---|
| Pedidos eliminados o cancelados | 81 | Se descartaron |
| Pedidos con total en cero | 29 | Se descartaron |
| Vendedor con valor "-" | 2072 | Se renombró a "Sin asignar" |
| Zona vacía | 2089 | Se completó con "Sin zona" |
| Columnas casi vacías (datos web, armado_log, etc.) | varias | No se usaron en el análisis |

Quedaron **4680 pedidos**.

Lo más importante fue la columna `items`: es un texto JSON con la lista de productos de cada pedido. La recorrimos con un `for` y la convertimos en una tabla propia de **101.881 líneas** (una por producto vendido), con producto, precio, precio original y cantidad. Después:

- Limpiamos los nombres de producto (le sacamos los símbolos `*` y `-` del principio).
- Creamos la **marca** tomando la primera palabra del nombre (por ejemplo FELFORT, ARC). Es una aproximación simple.
- Calculamos ingreso (precio x cantidad) y descuento (precio original menos precio, por cantidad).

Comprobamos que la suma de las líneas coincide con el total de los pedidos (diferencia menor a $1).

También agregamos columnas de mes y día de la semana a partir de la fecha.

## 4. Storytelling

**Planteo.** La distribuidora vende cerca de 450 pedidos por mes. ¿Dónde está el negocio y qué se puede mejorar?

**Hallazgo 1: El ticket promedio sube, la cantidad de pedidos no.** Entre mayo y septiembre de 2026 el pedido promedio pasó de $329.000 a $401.000 (+22%), mientras que la cantidad de pedidos se mantuvo entre 420 y 480 por mes. Crecemos vendiendo más por pedido, no atendiendo más pedidos. (Octubre aparece más bajo porque el mes está incompleto.)

**Hallazgo 2: El negocio es de lunes a viernes, con el viernes arriba.** Casi no hay pedidos sábado y domingo. El viernes concentra el 24% de las ventas.

**Hallazgo 3: Pocos productos y marcas pesan mucho.** Felfort (7,7% de los ingresos) y ARC (6,6%) son las marcas que más facturan. En unidades, lo que más sale son los Don Satur (grasa y agridulce), que son productos baratos pero de altísimo volumen. Entonces conviene mirar el top por ingreso y por unidades por separado, porque cuentan historias distintas.

**Hallazgo 4: La cartera de clientes está repartida.** Los 10 mejores clientes suman el 27% de las ventas y hay 358 clientes distintos. No dependemos de uno solo, aunque algunos clientes (estaciones de servicio, por ejemplo) compran montos muy grandes.

**Hallazgo 5: Los vendedores tienen perfiles distintos.** Cristian tiene el ticket promedio más alto ($479.000), Matias ($368.000) y Joaquin ($242.000). Cristian y Matias venden más plata por pedido; Joaquin hace muchos pedidos de menor monto.

**Hallazgo 6: Los descuentos son chicos.** Se descontó en total el 1,5% de lo que se hubiera vendido a precio original.

**Hallazgo 7: Armado y reparto se empezaron a medir en septiembre 2026.** En septiembre se registraba el armado en el 80% de los pedidos y en octubre en el 99%. El reparto subió de 49% a 95%. Es una mejora en el uso del sistema que permite medir la operación de ahora en adelante.

**Conclusión.** El negocio es estable en cantidad de pedidos y crece por ticket. Para seguir creciendo conviene sumar clientes nuevos y hacer que los vendedores con ticket bajo se acerquen al de los mejores, cuidando el stock de las marcas líderes.

## 5. Cómo está armado el dashboard

- Filtros en la barra lateral: mes, vendedor y zona.
- Cuatro indicadores: ventas, pedidos, ticket promedio y clientes distintos.
- Cinco pestañas: Evolución, Productos, Clientes y vendedores, Operación y Datos (con el detalle de la limpieza y descarga del CSV).
- Gráficos hechos con Plotly.

## 6. Cómo ejecutarlo

```
pip install -r requirements.txt
streamlit run app.py
```
