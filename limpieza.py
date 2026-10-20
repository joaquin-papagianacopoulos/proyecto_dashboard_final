import json
import pandas as pd


def sacar_items(pedidos):
    filas = []
    for i in range(len(pedidos)):
        pedido = pedidos.iloc[i]
        for item in json.loads(pedido["items"]):
            filas.append({
                "id_pedido": pedido["id"],
                "producto": item["nombre"],
                "precio": item["precio"],
                "precio_original": item.get("precioOriginal"),
                "cantidad": item["cantidad"],
            })
    return pd.DataFrame(filas)


def cargar_y_limpiar(ruta="datos/pedidos.csv"):
    datos = pd.read_csv(ruta)
    resumen = {"filas_originales": len(datos)}

    estados_malos = ["eliminado", "cancelado"]
    resumen["eliminados_cancelados"] = int(datos["estado"].isin(estados_malos).sum())
    datos = datos[~datos["estado"].isin(estados_malos)]

    resumen["total_cero"] = int((datos["total"] <= 0).sum())
    datos = datos[datos["total"] > 0]

    resumen["vendedor_sin_asignar"] = int((datos["vendedor"] == "-").sum())
    datos["vendedor"] = datos["vendedor"].replace("-", "Sin asignar")

    resumen["zona_vacia"] = int(datos["zona"].isna().sum())
    datos["zona"] = datos["zona"].fillna("Sin zona")

    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos["periodo"] = datos["fecha"].dt.strftime("%Y-%m")
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    datos["dia_semana"] = datos["fecha"].dt.dayofweek.apply(lambda d: dias[d])

    resumen["pedidos_web"] = int((datos["origen"] == "web").sum())

    pedidos = datos[["id", "cliente_nombre", "vendedor", "fecha", "periodo", "dia_semana",
                     "total", "estado", "zona", "armado", "a_reparto", "deuda_generada", "origen"]]
    pedidos = pedidos.rename(columns={"id": "id_pedido"}).reset_index(drop=True)

    lineas = sacar_items(datos)
    lineas = lineas[lineas["id_pedido"].isin(pedidos["id_pedido"])]

    lineas["producto"] = lineas["producto"].str.replace(r"^[-*\s]+", "", regex=True).str.strip()
    lineas["marca"] = lineas["producto"].str.split().str[0]
    lineas["precio_original"] = lineas["precio_original"].fillna(lineas["precio"])
    lineas["ingreso"] = lineas["precio"] * lineas["cantidad"]
    lineas["descuento"] = (lineas["precio_original"] - lineas["precio"]).clip(lower=0) * lineas["cantidad"]

    datos_pedido = pedidos[["id_pedido", "fecha", "periodo", "vendedor", "zona", "cliente_nombre"]]
    lineas = lineas.merge(datos_pedido, on="id_pedido")

    resumen["filas_finales"] = len(pedidos)
    resumen["lineas"] = len(lineas)
    return pedidos, lineas.reset_index(drop=True), resumen
