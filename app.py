import streamlit as st
import plotly.express as px
from limpieza import cargar_y_limpiar

st.set_page_config(page_title="Dashboard Ventas - Distribuidora de Bebidas", layout="wide")


@st.cache_data
def traer_datos():
    return cargar_y_limpiar()


datos, resumen = traer_datos()

meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

st.title("Ventas de una distribuidora de bebidas 2023-2024")
st.write("Dashboard para analizar que se vende, donde se vende y cuanto ganamos.")

st.sidebar.header("Filtros")
anios = st.sidebar.multiselect("Año", sorted(datos["anio"].unique()), default=sorted(datos["anio"].unique()))
regiones = st.sidebar.multiselect("Region", sorted(datos["region"].unique()), default=sorted(datos["region"].unique()))
categorias = st.sidebar.multiselect("Categoria", sorted(datos["categoria"].unique()), default=sorted(datos["categoria"].unique()))

filtrado = datos[
    datos["anio"].isin(anios)
    & datos["region"].isin(regiones)
    & datos["categoria"].isin(categorias)
]

if filtrado.empty:
    st.warning("No hay datos con los filtros elegidos.")
    st.stop()

ingresos = filtrado["ingreso"].sum()
ganancia = filtrado["ganancia"].sum()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingresos", "$ {:,.0f}".format(ingresos))
col2.metric("Ganancia", "$ {:,.0f}".format(ganancia))
col3.metric("Margen", "{:.1f} %".format(ganancia / ingresos * 100))
col4.metric("Cantidad de ventas", "{:,}".format(len(filtrado)))

tab1, tab2, tab3, tab4 = st.tabs(["Evolucion", "Productos", "Regiones y vendedores", "Datos"])

with tab1:
    st.subheader("Los ingresos tienen estacionalidad")
    por_mes = filtrado.groupby("periodo")["ingreso"].sum().reset_index()
    grafico = px.line(por_mes, x="periodo", y="ingreso", markers=True,
                      labels={"periodo": "Mes", "ingreso": "Ingresos ($)"})
    st.plotly_chart(grafico, width="stretch")
    st.write("Las ventas se disparan en noviembre y diciembre por las fiestas. El resto del año se mantienen bastante parejas.")

    st.subheader("Que categoria vende mas en cada mes")
    tabla = filtrado.groupby(["mes", "categoria"])["ingreso"].sum().reset_index()
    tabla["mes"] = tabla["mes"].apply(lambda m: meses[m - 1])
    grafico = px.bar(tabla, x="mes", y="ingreso", color="categoria",
                     category_orders={"mes": meses},
                     labels={"mes": "Mes", "ingreso": "Ingresos ($)", "categoria": "Categoria"})
    st.plotly_chart(grafico, width="stretch")

with tab2:
    izq, der = st.columns(2)

    with izq:
        st.subheader("Ingresos por categoria")
        por_categoria = filtrado.groupby("categoria")["ingreso"].sum().reset_index()
        grafico = px.pie(por_categoria, names="categoria", values="ingreso")
        st.plotly_chart(grafico, width="stretch")

    with der:
        st.subheader("Margen de ganancia por categoria")
        margen = filtrado.groupby("categoria")[["ingreso", "ganancia"]].sum().reset_index()
        margen["margen"] = margen["ganancia"] / margen["ingreso"] * 100
        grafico = px.bar(margen, x="categoria", y="margen",
                         labels={"categoria": "Categoria", "margen": "Margen (%)"})
        st.plotly_chart(grafico, width="stretch")

    st.subheader("Top 10 productos por ganancia")
    top = filtrado.groupby("producto")["ganancia"].sum().sort_values().tail(10).reset_index()
    grafico = px.bar(top, x="ganancia", y="producto", orientation="h",
                     labels={"producto": "Producto", "ganancia": "Ganancia ($)"})
    st.plotly_chart(grafico, width="stretch")

    st.subheader("Los descuentos afectan la ganancia")
    por_descuento = filtrado.groupby("descuento")["ganancia"].mean().reset_index()
    por_descuento["descuento"] = (por_descuento["descuento"] * 100).astype(int).astype(str) + " %"
    grafico = px.bar(por_descuento, x="descuento", y="ganancia",
                     labels={"descuento": "Descuento", "ganancia": "Ganancia promedio por venta ($)"})
    st.plotly_chart(grafico, width="stretch")

with tab3:
    st.subheader("Crecimiento de cada region")
    por_region = filtrado.groupby(["anio", "region"])["ingreso"].sum().reset_index()
    por_region["anio"] = por_region["anio"].astype(str)
    grafico = px.bar(por_region, x="region", y="ingreso", color="anio", barmode="group",
                     labels={"region": "Region", "ingreso": "Ingresos ($)", "anio": "Año"})
    st.plotly_chart(grafico, width="stretch")
    st.write("La region Sur es la que mas crecio entre 2023 y 2024.")

    izq, der = st.columns(2)

    with izq:
        st.subheader("Ganancia por vendedor")
        por_vendedor = filtrado.groupby("vendedor")["ganancia"].sum().sort_values().reset_index()
        grafico = px.bar(por_vendedor, x="ganancia", y="vendedor", orientation="h",
                         labels={"vendedor": "Vendedor", "ganancia": "Ganancia ($)"})
        st.plotly_chart(grafico, width="stretch")

    with der:
        st.subheader("Medios de pago")
        por_pago = filtrado.groupby("medio_pago")["ingreso"].sum().reset_index()
        grafico = px.pie(por_pago, names="medio_pago", values="ingreso")
        st.plotly_chart(grafico, width="stretch")

with tab4:
    st.subheader("Limpieza de datos realizada")
    st.write("Filas originales:", resumen["filas_originales"])
    st.write("Filas duplicadas eliminadas:", resumen["duplicados"])
    st.write("Descuentos vacios completados con 0:", resumen["descuentos_nulos"])
    st.write("Vendedores vacios marcados como 'Sin asignar':", resumen["vendedores_nulos"])
    st.write("Ventas con cantidad absurda eliminadas:", resumen["cantidades_absurdas"])
    st.write("Filas finales:", resumen["filas_finales"])

    st.subheader("Tabla de ventas filtrada")
    st.dataframe(filtrado.drop(columns=["periodo"]))
    st.download_button("Descargar CSV", filtrado.to_csv(index=False), "ventas_filtradas.csv")

