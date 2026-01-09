import streamlit as st

def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    credentials = st.secrets["credentials"]

    st.set_page_config(page_title="Login", page_icon=":lock:", layout="centered")

    col1, col2, col3 = st.columns(3)
    
    col3.image(
        "https://www.guatemalagbc.org/wp-content/uploads/2024/07/spectrum-1-800x600-1.png",
        width=180
    )

    col1.markdown(
        "<h2 style='text-align: center;'>Gestor de Horarios</h2>",
        unsafe_allow_html=True
    )

    st.markdown("## 🔐 Login")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar", type="primary", use_container_width=True):
        if username in credentials and credentials[username] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.success("Bienvenido")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    return False
