import streamlit as st
import pandas as pd
from datetime import datetime
from db import run_query
from lib import productos, bodegas

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.switch_page("Inicio.py")

st.set_page_config(
    page_title="Movimientos de Inventario",
    layout="centered",
    page_icon="🍎"
)

defaults = {
    "carrito": [],
    "tipo_movimiento": "",
    "fecha_venta": datetime.now(),
    "tipo_venta": "",
    "punto_venta": "",
    "envio_venta": "",
    "cliente": "",
    "observaciones_venta": "",
    "fecha_compra": datetime.now(),
    "envio_compra": "",
    "punto_compra": "",
    "proveedor": "",
    "observaciones_compra": "",
    "fecha_transferencia": datetime.now(),
    "envio_transferencia": "",
    "bodega_entrada": "",
    "bodega_salida": "",
    "observaciones_transferencia": "",
    "sku": "",
    "cantidad": 1,
    "precio": 0,
    "subtotal": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Obtener las bases de datos
clientes = {}
proveedores = {}
encabezados = {}
detalle = {}

st.title("Formulario de Registro de Movimientos")

registro, cliente, proveedor, producto = st.tabs(["Registro", "Crear Cliente", "Crear Proveedor", "Crear Producto"])

with registro:
    ###############################
    # SECCIÓN 1: ENCABEZADO
    ###############################
    st.selectbox("Tipo de movimiento", ["Venta", "Compra", "Transferencia"], key="tipo_movimiento")
    
    st.subheader("Datos de la transacción")

    if st.session_state.tipo_movimiento == "Venta":
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        
        c1.date_input("Fecha de la venta", value=datetime.now(), key="fecha_venta")
        c2.text_input("No. Envío", key="envio_venta")
        c3.selectbox("Tipo de Venta", ["", "Venta al contado", "Venta al crédito"], key="tipo_venta")
        c4.selectbox("Punto de venta", ["", *bodegas], key="punto_venta")

        opciones_clientes = {None: ""} | {c["id_cliente"]: c["nombre"] for c in clientes}
        st.selectbox("Cliente", opciones_clientes, format_func=lambda x: opciones_clientes[x], key="cliente")

        st.text_area("Observaciones", key="observaciones_venta")

    if st.session_state.tipo_movimiento == "Compra":
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        
        c1.date_input("Fecha de la compra", value=datetime.now(), key = "fecha_compra")
        c2.text_input("No. Envío", key="envio_compra")
        c3.selectbox("Punto de compra", ["", *bodegas], key="punto_compra")

        opciones_proveedores = {None: ""} | {p["id_proveedor"]: p["nombre"] for p in proveedores}
        c4.selectbox("Proveedor", opciones_proveedores, format_func=lambda x: opciones_proveedores[x], key="proveedor")

        st.text_area("Observaciones", key="observaciones_compra")

    if st.session_state.tipo_movimiento == "Transferencia":
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)
        
        c1.date_input("Fecha de la transferencia", value=datetime.now(), key="fecha_transferencia")
        c2.text_input("No. Envío", key="envio_transferencia")
        c3.selectbox("Bodega de entrada", ["", *bodegas], key="bodega_entrada")
        c4.selectbox("Bodega de salida", ["", *bodegas], key="bodega_salida")
        st.text_area("Observaciones", key="observaciones_transferencia")

    st.divider()

    ###############################
    # SECCIÓN 2: DETALLE
    ###############################

    st.subheader("Detalle de la transacción")

    if st.session_state.tipo_movimiento == "Venta" or st.session_state.tipo_movimiento == "Compra":
        with st.expander("Agregar Producto"):
            c1, c2, c3 = st.columns(3)
            
            c1.selectbox("Producto", productos.keys(), format_func=lambda x: productos[x], key="sku")
            prod_nom = productos[st.session_state.sku]
            c2.number_input("Cantidad", min_value=1, value=1, step=1, key="cantidad")
            c3.number_input("Precio", min_value=0, value=0, step=5, key="precio")
            prod_subtotal = st.session_state.cantidad * st.session_state.precio

            st.write("Subtotal:", f"GTQ {prod_subtotal}")

            if st.button("Agregar Producto"):
                st.session_state.carrito.append({"sku": st.session_state.sku, "nombre": prod_nom, "cantidad": st.session_state.cantidad, "precio": st.session_state.precio, "subtotal": prod_subtotal})
                st.rerun()

        if st.session_state.carrito:
            df = pd.DataFrame(st.session_state.carrito)

            total = df["subtotal"].sum()

            st.subheader("Carrito")
            st.dataframe(df, width="stretch", column_config={
                "sku": "SKU",
                "nombre": "Producto",
                "cantidad": "Cantidad",
                "precio": "Precio",
                "subtotal": "Subtotal"
            })

            st.markdown(f"### 💰 Total: **Q {total:,.2f}**")
        else:
            st.info("No hay productos en el carrito")

    elif st.session_state.tipo_movimiento == "Transferencia":
        with st.expander("Agregar Producto"):
            c1, c2 = st.columns(2)
            
            c1.selectbox("Producto", productos.keys(), format_func=lambda x: productos[x], key="sku")
            prod_nom = productos[st.session_state.sku]
            c2.number_input("Cantidad", min_value=1, value=1, step=1, key="cantidad")

            if st.button("Agregar Producto"):
                st.session_state.carrito.append({"sku": st.session_state.sku, "nombre": prod_nom, "cantidad": st.session_state.cantidad})
                st.rerun()

        if st.session_state.carrito:
            df = pd.DataFrame(st.session_state.carrito)

            total = df["cantidad"].sum()

            st.subheader("Carrito")
            st.dataframe(df, width="stretch", column_config={
                "sku": "SKU",
                "nombre": "Producto",
                "cantidad": "Cantidad"
            })

            st.markdown(f"### 💰 Total: **{total:,} Cajas**")
        else:
            st.info("No hay productos en el carrito")

    c1, c2, c3 = st.columns(3)

    if c1.button("💾 Guardar"):

        tipo_movimiento = st.session_state.tipo_movimiento
        

        if st.session_state.tipo_movimiento == "Venta":
            query = "INSERT INTO encabezados (tipo_movimiento, fecha, total, punto_venta, persona, no_envio, estado, observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_transaccion"

        elif st.session_state.tipo_movimiento == "Compra":
            query = "INSERT INTO encabezados (tipo_movimiento, fecha, total, punto_compra, persona, no_envio, observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_transaccion"
        elif st.session_state.tipo_movimiento == "Transferencia":
            query = "INSERT INTO encabezados (tipo_movimiento, fecha, total, punto_venta, punto_compra, no_envio, observaciones) VALUES (%s, %s, %s, %s, %s, %s %s) RETURNING id_transaccion"
        

        if transaccion == 1 or transaccion == 2: # Venta o Compra
            
            if transaccion == 1:
                row = run_query("INSERT INTO encabezados (fecha, no_envio, transaccion, tipo_venta, metodo_pago, bodega_origen, id_cliente, total, observaciones, estado, factura) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_transaccion", (fecha, envio, int(transaccion), tipo, pago, bodega, int(cliente), float(total), observaciones, estado, bool(factura)), fetch="one")
            
            if transaccion == 2:
                row = run_query("INSERT INTO encabezados (fecha, no_envio, transaccion, bodega_destino, id_proveedor, total, observaciones, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_transaccion", (fecha, envio, int(transaccion), bodega, int(proveedor), float(total), observaciones, estado), fetch="one")

            id_transaccion = row["id_transaccion"]

            for item in st.session_state.carrito:
                run_query("INSERT INTO detalles (id_transaccion, fecha, sku, cantidad, precio, subtotal) VALUES (%s, %s, %s, %s, %s, %s)", (id_transaccion, fecha, str(item["sku"]), int(item["cantidad"]), float(item["precio"]), float(item["subtotal"])), fetch="none")

        if transaccion == 3: # Transferencia
            row = run_query("INSERT INTO encabezados (fecha, no_envio, transaccion, bodega_origen, bodega_destino, total, observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_transaccion", (fecha, envio, int(transaccion), bodega_entrada, bodega_salida, float(total), observaciones), fetch="one")
            id_transaccion = row["id_transaccion"]

            for item in st.session_state.carrito:
                run_query("INSERT INTO detalles (id_transaccion, fecha, sku, cantidad) VALUES (%s, %s, %s, %s)", (id_transaccion, fecha, str(item["sku"]), int(item["cantidad"])), fetch="none")    

        st.success("Transacción guardada exitosamente")

        st.session_state.carrito = []
        st.rerun()
        
    if c2.button("🧹 Vaciar detalle"):
        st.session_state.carrito = []
        st.rerun()

    if c3.button("🗑️ Quitar último producto"):
        st.session_state.carrito.pop()
        st.rerun()

    st.info("Recargar página para reiniciar el formulario")
