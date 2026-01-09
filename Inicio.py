# Importaciones
import streamlit as st
import pandas as pd
from db import run_query
from auth import check_login
from lib import productos, dataframe_to_pdf

# Configuración de la página
if not check_login():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    st.stop()

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

st.set_page_config(
    page_title="Sistema ERP",
    page_icon=":data:",
    layout="wide"
)

col1, col2 = st.columns(2)

with col1:
    st.title("🏠 Menú principal")
    st.markdown("""
    Bienvenido a la aplicación.
    Selecciona una sección desde el menú lateral.
    """)

with col2:
    st.subheader("Estado de la base de datos")
    row = run_query("select now() as ahora;", fetch="one")
    st.write("Conexión exitosa ✅", row["ahora"])

clientes = []
proveedores = []
encabezados = []
detalle = []

query_inventario = """
SELECT
    d.sku,
    SUM(CASE WHEN e.transaccion = 2 THEN d.cantidad ELSE 0 END) AS entradas,
    SUM(CASE WHEN e.transaccion = 1 THEN d.cantidad ELSE 0 END) AS salidas,
    SUM(
        CASE
            WHEN e.transaccion = 2 THEN d.cantidad
            WHEN e.transaccion = 1 THEN -d.cantidad
            ELSE 0
        END
    ) AS stock_actual
FROM detalles d
JOIN encabezados e ON d.id_transaccion = e.id_transaccion
WHERE e.estado != 'Anulada'
GROUP BY d.sku
ORDER BY d.sku;
"""

inventario = []

st.subheader("Inventario Actual")

inventario = pd.DataFrame(inventario)
inventario["productos"] = inventario["sku"].map(productos)
inventario = inventario[["sku", "productos", "entradas", "salidas", "stock_actual"]]

st.dataframe(inventario, width="stretch", column_config={
    "sku": "SKU",
    "productos": "Producto",
    "entradas": "Entradas",
    "salidas": "Salidas",
    "stock_actual": "Stock Actual"
})

pdf = dataframe_to_pdf(inventario)

st.download_button(
    label="📄 Descargar Inventario en PDF",
    data=pdf,
    file_name="inventario_actual.pdf",
    mime="application/pdf"
)

