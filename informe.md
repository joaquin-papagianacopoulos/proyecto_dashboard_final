# Informe: Dashboard de ventas de una distribuidora de bebidas

Trabajo final de Streamlit - Integrantes: Joaquin Papagianacopoulos, Agustin Pellegrino, Santiago Martire

## 1. Objetivo

Armar un dashboard que le sirva al dueño de una distribuidora de bebidas para responder tres preguntas: qué productos nos dan más plata, en qué momento del año y en qué zonas vendemos más, y dónde estamos perdiendo ganancia.

## 2. El dataset

No encontramos datos reales de una distribuidora, así que **generamos un dataset simulado** con el script `generar_datos.py`. Lo armamos con comportamientos parecidos a la realidad (más cerveza en verano, más vino en diciembre, etc.) y le agregamos errores a propósito para poder practicar la limpieza.

Tiene 2253 filas (2023 y 2024) y estas columnas: id de venta, fecha, región, categoría, producto, precio unitario, costo unitario, cantidad, descuento, vendedor y medio de pago.

## 3. Tratamiento de datos

La limpieza está en `limpieza.py`. Los problemas que encontramos y qué hicimos:

| Problema | Cantidad | Solución |
|---|---|---|
| Filas duplicadas | 40 | Se eliminaron con `drop_duplicates` |
| Regiones mal escritas ("centro ", "NORTE", " sur") | 80 | Se sacaron espacios y se unificó el formato |
| Descuentos vacíos | 60 | Se completaron con 0 (asumimos que no hubo descuento) |
| Vendedores vacíos | 45 | Se marcaron como "Sin asignar" para no perder la venta |
| Cantidades negativas | 8 | Se pasaron a positivo (error de carga) |
| Cantidades absurdas (5000 unidades) | 5 | Se eliminaron las filas |

Después creamos columnas nuevas: año, mes, ingreso (precio x cantidad menos descuento), costo y ganancia (ingreso menos costo).

Resultado final: 2208 filas limpias.

## 4. Storytelling

**Planteo.** La distribuidora creció en 2024, pero ¿creció bien?

**Hallazgo 1: Los vinos son el negocio.** Los vinos generan el 53% de los ingresos totales (unos $81,7 millones de $154,5 millones), con una cantidad de unidades parecida a la de las otras categorías (la cerveza es la que más unidades vende). Lo que pasa es que cada botella de vino vale mucho más. Si el vino tiene un problema, toda la empresa lo siente.

**Hallazgo 2: Noviembre y diciembre son los meses clave.** Un mes normal factura alrededor de $11,8 millones, pero noviembre llega a $17,3 millones y diciembre a $20,8 millones. Hay que tener stock y camiones listos antes de esos meses.

**Hallazgo 3: La región Sur explotó.** Pasó de $10,8 millones en 2023 a $24,7 millones en 2024 (más del doble). Ahora casi alcanza a la región Centro, que se mantuvo casi igual. Es la zona donde más conviene invertir.

**Hallazgo 4: Las aguas dejan más margen y las gaseosas menos.** Las aguas tienen un margen de 42,7% y las gaseosas solo 30%. Además las cervezas casi duplicaron sus ingresos en 2024 (de $9,3 a $16,3 millones), mientras que las gaseosas subieron solo 8%, menos que la inflación simulada, o sea que en realidad retrocedieron.

**Hallazgo 5: Los descuentos se comen la ganancia.** Una venta sin descuento deja en promedio $30.300 de ganancia; con 15% de descuento deja $17.800, un 41% menos. Conviene revisar a quién se le da el descuento más alto.

**Aclaración.** Los precios de 2024 incluyen una suba del 25% que pusimos en el dataset para simular inflación. Por eso el crecimiento de ingresos de 2024 (+38%) es en parte aumento de precios y no solo más ventas.

**Conclusión.** La empresa crece, pero depende mucho del vino y de las fiestas de fin de año. Recomendamos reforzar la zona Sur, empujar las aguas por su margen y poner un límite a los descuentos altos.

## 5. Cómo está armado el dashboard

- Filtros en la barra lateral: año, región y categoría.
- Cuatro indicadores arriba: ingresos, ganancia, margen y cantidad de ventas.
- Cuatro pestañas: Evolución, Productos, Regiones y vendedores, y Datos (con el detalle de la limpieza y botón para descargar el CSV).
- Gráficos hechos con Plotly.

## 6. Cómo ejecutarlo

```
pip install -r requirements.txt
streamlit run app.py
```
