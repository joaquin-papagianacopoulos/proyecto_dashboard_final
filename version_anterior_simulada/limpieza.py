import pandas as pd


def cargar_y_limpiar(ruta="datos/ventas_crudo.csv"):
    datos = pd.read_csv(ruta)
    resumen = {"filas_originales": len(datos)}

    datos = datos.drop_duplicates()
    resumen["duplicados"] = resumen["filas_originales"] - len(datos)

    datos["region"] = datos["region"].str.strip().str.capitalize()

    resumen["descuentos_nulos"] = int(datos["descuento"].isna().sum())
    datos["descuento"] = datos["descuento"].fillna(0)

    resumen["vendedores_nulos"] = int(datos["vendedor"].isna().sum())
    datos["vendedor"] = datos["vendedor"].fillna("Sin asignar")

    datos["cantidad"] = datos["cantidad"].abs()
    filas_antes = len(datos)
    datos = datos[datos["cantidad"] <= 200]
    resumen["cantidades_absurdas"] = filas_antes - len(datos)

    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos["anio"] = datos["fecha"].dt.year
    datos["mes"] = datos["fecha"].dt.month
    datos["periodo"] = datos["fecha"].dt.to_period("M").dt.to_timestamp()

    datos["ingreso"] = datos["precio_unitario"] * datos["cantidad"] * (1 - datos["descuento"])
    datos["costo"] = datos["costo_unitario"] * datos["cantidad"]
    datos["ganancia"] = datos["ingreso"] - datos["costo"]

    resumen["filas_finales"] = len(datos)
    return datos.reset_index(drop=True), resumen
