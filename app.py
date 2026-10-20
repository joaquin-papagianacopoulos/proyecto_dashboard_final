import streamlit as st
import plotly.express as px
from limpieza import cargar_y_limpiar

st.set_page_config(page_title="Dashboard de Pedidos - Distribuidora", layout="wide")


@st.cache_data
def traer_datos():
    return cargar_y_limpiar()


pedidos, lineas, resumen = traer_datos()

st.title("Pedidos de una distribuidora de golosinas y bebidas")
st.write("Dashboard para analizar cuanto vendemos, a quien, que productos mueven el negocio y como trabaja el equipo.")

st.sidebar.header("Filtros")
periodos = st.sidebar.multiselect("Mes", sorted(pedidos["periodo"].unique()), default=sorted(pedidos["periodo"].unique()))
vendedores = st.sidebar.multiselect("Vendedor", sorted(pedidos["vendedor"].unique()), default=sorted(pedidos["vendedor"].unique()))
zonas = st.sidebar.multiselect("Zona", sorted(pedidos["zona"].unique()), default=sorted(pedidos["zona"].unique()))

pedidos_f = pedidos[
    pedidos["periodo"].isin(periodos)
    & pedidos["vendedor"].isin(vendedores)
    & pedidos["zona"].isin(zonas)
]
lineas_f = lineas[
    lineas["periodo"].isin(periodos)
    & lineas["vendedor"].isin(vendedores)
    & lineas["zona"].isin(zonas)
]

if pedidos_f.empty:
    st.warning("No hay datos con los filtros elegidos.")
    st.stop()

total = pedidos_f["total"].sum()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas", "$ {:,.0f}".format(total))
col2.metric("Pedidos", "{:,}".format(len(pedidos_f)))
col3.metric("Ticket promedio", "$ {:,.0f}".format(pedidos_f["total"].mean()))
col4.metric("Clientes distintos", "{:,}".format(pedidos_f["cliente_nombre"].nunique()))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Evolucion", "Productos", "Clientes y vendedores", "Operacion", "Datos"])

with tab1:
    st.subheader("Ventas por mes")
    por_mes = pedidos_f.groupby("periodo").agg(ventas=("total", "sum"), pedidos=("total", "count"),
                                               ticket=("total", "mean")).reset_index()
    grafico = px.bar(por_mes, x="periodo", y="ventas", labels={"periodo": "Mes", "ventas": "Ventas ($)"})
    grafico.update_xaxes(type="category")
    st.plotly_chart(grafico, width="stretch")
    st.write("Hay un salto en el tiempo: tenemos marzo y abril de 2025 y despues desde fines de abril de 2026.")

    izq, der = st.columns(2)

    with izq:
        st.subheader("Cantidad de pedidos por mes")
        grafico = px.bar(por_mes, x="periodo", y="pedidos", labels={"periodo": "Mes", "pedidos": "Pedidos"})
        grafico.update_xaxes(type="category")
        st.plotly_chart(grafico, width="stretch")

    with der:
        st.subheader("Ticket promedio por mes")
        grafico = px.bar(por_mes, x="periodo", y="ticket", labels={"periodo": "Mes", "ticket": "Ticket promedio ($)"})
        grafico.update_xaxes(type="category")
        st.plotly_chart(grafico, width="stretch")

    st.subheader("Ventas por dia de la semana")
    dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    por_dia = pedidos_f.groupby("dia_semana")["total"].sum().reset_index()
    grafico = px.bar(por_dia, x="dia_semana", y="total", category_orders={"dia_semana": dias},
                     labels={"dia_semana": "Dia", "total": "Ventas ($)"})
    st.plotly_chart(grafico, width="stretch")

with tab2:
    izq, der = st.columns(2)

    with izq:
        st.subheader("Top 10 productos por ingreso")
        top = lineas_f.groupby("producto")["ingreso"].sum().sort_values().tail(10).reset_index()
        grafico = px.bar(top, x="ingreso", y="producto", orientation="h",
                         labels={"producto": "Producto", "ingreso": "Ingreso ($)"})
        st.plotly_chart(grafico, width="stretch")

    with der:
        st.subheader("Top 10 marcas por ingreso")
        marcas = lineas_f.groupby("marca")["ingreso"].sum().sort_values().tail(10).reset_index()
        grafico = px.bar(marcas, x="ingreso", y="marca", orientation="h",
                         labels={"marca": "Marca", "ingreso": "Ingreso ($)"})
        st.plotly_chart(grafico, width="stretch")

    st.subheader("Top 10 productos por unidades vendidas")
    unidades = lineas_f.groupby("producto")["cantidad"].sum().sort_values().tail(10).reset_index()
    grafico = px.bar(unidades, x="cantidad", y="producto", orientation="h",
                     labels={"producto": "Producto", "cantidad": "Unidades"})
    st.plotly_chart(grafico, width="stretch")

    st.subheader("Descuentos otorgados")
    descuento = lineas_f["descuento"].sum()
    ingreso = lineas_f["ingreso"].sum()
    st.write("Se descontaron $ {:,.0f} en total, que es el {:.1f} % de lo que se vendio.".format(
        descuento, descuento / (ingreso + descuento) * 100))
    desc_marca = lineas_f.groupby("marca")["descuento"].sum().sort_values().tail(10).reset_index()
    grafico = px.bar(desc_marca, x="descuento", y="marca", orientation="h",
                     labels={"marca": "Marca", "descuento": "Descuento ($)"})
    st.plotly_chart(grafico, width="stretch")

with tab3:
    st.subheader("Top 10 clientes")
    por_cliente = pedidos_f.groupby("cliente_nombre")["total"].sum().sort_values()
    top10 = por_cliente.tail(10).reset_index()
    grafico = px.bar(top10, x="total", y="cliente_nombre", orientation="h",
                     labels={"cliente_nombre": "Cliente", "total": "Compras ($)"})
    st.plotly_chart(grafico, width="stretch")
    porcentaje = por_cliente.tail(10).sum() / total * 100
    st.write("Los 10 mejores clientes representan el {:.1f} % de las ventas.".format(porcentaje))

    izq, der = st.columns(2)

    with izq:
        st.subheader("Ventas por vendedor")
        por_vendedor = pedidos_f.groupby("vendedor")["total"].sum().reset_index()
        grafico = px.pie(por_vendedor, names="vendedor", values="total")
        st.plotly_chart(grafico, width="stretch")

    with der:
        st.subheader("Ticket promedio por vendedor")
        ticket = pedidos_f.groupby("vendedor")["total"].mean().reset_index()
        grafico = px.bar(ticket, x="vendedor", y="total",
                         labels={"vendedor": "Vendedor", "total": "Ticket promedio ($)"})
        st.plotly_chart(grafico, width="stretch")

with tab4:
    st.subheader("Armado, reparto y deuda")
    st.write("Estos datos se empezaron a registrar en septiembre de 2026, por eso antes figuran en cero.")
    recientes = pedidos_f[pedidos_f["periodo"] >= "2026-09"]

    if recientes.empty:
        st.info("Elegi septiembre u octubre de 2026 en el filtro de mes para ver esta seccion.")
    else:
        por_estado = recientes.groupby("periodo")[["armado", "a_reparto", "deuda_generada"]].mean() * 100
        por_estado = por_estado.reset_index().melt(id_vars="periodo", var_name="etapa", value_name="porcentaje")
        grafico = px.bar(por_estado, x="periodo", y="porcentaje", color="etapa", barmode="group",
                         labels={"periodo": "Mes", "porcentaje": "% de pedidos", "etapa": "Etapa"})
        st.plotly_chart(grafico, width="stretch")

    st.subheader("Estado de los pedidos")
    por_estado = pedidos_f.groupby("estado")["total"].agg(["count", "sum"]).reset_index()
    por_estado.columns = ["Estado", "Pedidos", "Monto ($)"]
    st.dataframe(por_estado)

    st.subheader("Pedidos hechos desde la web")
    st.write("Pedidos web recibidos:", int((pedidos_f["origen"] == "web").sum()))

with tab5:
    st.subheader("Limpieza de datos realizada")
    st.write("Pedidos originales:", resumen["filas_originales"])
    st.write("Pedidos eliminados o cancelados descartados:", resumen["eliminados_cancelados"])
    st.write("Pedidos con total en cero descartados:", resumen["total_cero"])
    st.write("Pedidos con vendedor '-' renombrados a 'Sin asignar':", resumen["vendedor_sin_asignar"])
    st.write("Pedidos sin zona completados con 'Sin zona':", resumen["zona_vacia"])
    st.write("Pedidos finales:", resumen["filas_finales"])
    st.write("Lineas de producto obtenidas de la columna items:", resumen["lineas"])

    st.subheader("Tabla de pedidos filtrada")
    st.dataframe(pedidos_f)
    st.download_button("Descargar CSV", pedidos_f.to_csv(index=False), "pedidos_filtrados.csv")
