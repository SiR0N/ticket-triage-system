import streamlit as st
import requests
import sys
from pathlib import Path

# Agregar la raíz del proyecto al sys.path para evitar ModuleNotFoundError
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.models.schemas import TicketRequest, ProviderEnum
from src.core.logging_config import logger  # Importación del Logger

API_URL = "http://localhost:8000/api/v1"

# Configuración de la página
st.set_page_config(
    page_title="Triaje de Incidentes - LLM",
    page_icon="🎫",
    layout="wide"
)

# ==========================================
# GESTIÓN DE ESTADO Y SESIÓN (JWT)
# ==========================================
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Helper para construir cabeceras autenticadas
def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}


# ==========================================
# 🔐 PANTALLA 1: INICIO DE SESIÓN
# ==========================================
if st.session_state.access_token is None:
    st.title("🔐 Iniciar Sesión en Ticket Triage")
    st.write("Por favor, ingrese sus credenciales para continuar.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(key="login_form"):
            username = st.text_input("Correo Electrónico / Usuario")
            password = st.text_input("Contraseña", type="password")
            login_submit = st.form_submit_button("Iniciar Sesión")

            if login_submit:
                if not username or not password:
                    st.warning("⚠️ Por favor completa todos los campos.")
                else:
                    try:
                        login_data = {
                            "username": username,
                            "password": password
                        }
                        response = requests.post(f"{API_URL}/auth/login", data=login_data)

                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.access_token = data.get("access_token")
                            st.session_state.user_role = data.get("role")
                            st.session_state.user_email = username
                            
                            logger.info(f"Streamlit: Login exitoso para '{username}' [{st.session_state.user_role}]")
                            st.success("✅ Autenticación exitosa")
                            st.rerun()
                        else:
                            logger.warning(f"Streamlit: Intento fallido de login para '{username}' (HTTP {response.status_code})")
                            st.error("❌ Credenciales incorrectas o usuario no encontrado.")
                    except requests.exceptions.ConnectionError:
                        logger.error("Streamlit: No se pudo conectar con la API de FastAPI durante el login.")
                        st.error("🔌 No se pudo conectar con la API de FastAPI.")
                    except Exception as e:
                        logger.error(f"Streamlit: Error inesperado en el inicio de sesión: {e}")
                        st.error(f"❌ Error al iniciar sesión: {e}")

# ==========================================
# 🎫 PANTALLA 2: DASHBOARD (USUARIO AUTENTICADO)
# ==========================================
else:
    # --- BARRA LATERAL (INFORMACIÓN DE USUARIO Y LOGOUT) ---
    st.sidebar.title("👤 Perfil de Usuario")
    st.sidebar.write(f"**Email:** {st.session_state.user_email}")
    
    role_color = "🔴" if st.session_state.user_role == "ADMIN" else "🔵"
    st.sidebar.write(f"**Rol:** {role_color} {st.session_state.user_role}")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        logger.info(f"Streamlit: Sesión cerrada por el usuario '{st.session_state.user_email}'")
        st.session_state.access_token = None
        st.session_state.user_role = None
        st.session_state.user_email = None
        st.rerun()

    st.title("🎫 Triaje de Incidentes Corporativos")

    # --- NAVEGACIÓN BASADA EN ROLES ---
    if st.session_state.user_role == "ADMIN":
        tab_report, tab_stats = st.tabs(["📝 Reportar Incidencia", "📊 Estadísticas y Analítica (ADMIN)"])
    else:
        tab_report, = st.tabs(["📝 Reportar Incidencia"])

    # ==========================================
    # PESTAÑA 1: REPORTAR INCIDENCIA (USER y ADMIN)
    # ==========================================
    with tab_report:
        st.write("Ingrese la descripción del incidente para su clasificación automática mediante LLMs.")

        with st.form(key='triage_form'):
            description = st.text_area(
                "Descripción del Incidente", 
                height=150,
                placeholder="Ej: El servidor principal de la base de datos no responde desde las 09:00 AM..."
            )
            
            # Control de selección de modelo por rol
            provider_options = {p.value: p for p in ProviderEnum}
            
            if st.session_state.user_role == "ADMIN":
                selected_provider_label = st.selectbox(
                    "Proveedor / Modelo de LLM", 
                    options=list(provider_options.keys())
                )
                enum_provider = provider_options[selected_provider_label]
            else:
                # Usuario estándar predeterminado en Gemini (se asume ProviderEnum.GEMINI o valor equivalente)
                enum_provider = getattr(ProviderEnum, "GEMINI", list(ProviderEnum)[0])
            
            submit_button = st.form_submit_button(label='Clasificar Incidencia')

        if submit_button:
            if not description.strip():
                st.warning("⚠️ Por favor, ingrese una descripción válida del incidente.")
            else:
                with st.spinner("Procesando clasificación..."):
                    try:
                        ticket_request = TicketRequest(
                            description=description, 
                            provider=enum_provider
                        )
                        
                        logger.info(f"Streamlit: Usuario '{st.session_state.user_email}' solicitó triaje con proveedor '{enum_provider.value}'")
                        
                        response = requests.post(
                            f"{API_URL}/triage", 
                            json=ticket_request.model_dump(),
                            headers=get_auth_headers()
                        )

                        if response.status_code == 200:
                            data = response.json()
                            logger.info(f"Streamlit: Triaje exitoso devuelto para '{st.session_state.user_email}'")
                            st.success("✅ Incidencia clasificada con éxito.")
                            
                            st.subheader("📋 Resultado del Triaje")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Categoría", data['category'])
                            with col2:
                                st.metric("Urgencia", data['urgency'])
                            with col3:
                                st.metric("Departamento", data['department'])

                            st.markdown("---")
                            st.write(f"**Resumen:** {data['summary']}")
                            
                            with st.expander("💭 Ver razonamiento del modelo (Thought Process)"):
                                st.write(data['thought_process'])

                            # Métricas visibles únicamente para rol ADMIN
                            if st.session_state.user_role == "ADMIN":
                                st.markdown("---")
                                st.caption("⚡ **Métricas de Ejecución (Solo Admin):**")
                                m_col1, m_col2, m_col3 = st.columns(3)
                                with m_col1:
                                    st.metric("Latencia", f"{data['latency']:.2f} s")
                                with m_col2:
                                    st.metric("Tokens", data['tokens_consumed'])
                                with m_col3:
                                    st.metric("Proveedor", data['provider'])

                        elif response.status_code == 401:
                            logger.warning(f"Streamlit: Token expirado al intentar triaje para '{st.session_state.user_email}'")
                            st.error("🔒 Sesión expirada. Por favor, vuelva a iniciar sesión.")
                            st.session_state.access_token = None
                        else:
                            logger.error(f"Streamlit: Error de API ({response.status_code}): {response.text}")
                            st.error(f"❌ Error en la clasificación ({response.status_code}): {response.text}")
                    
                    except requests.exceptions.ConnectionError:
                        logger.error("Streamlit: Conexión rechazada con la API durante el triaje.")
                        st.error("🔌 No se pudo conectar con la API de FastAPI.")
                    except Exception as e:
                        logger.error(f"Streamlit: Excepción en la solicitud de triaje: {e}")
                        st.error(f"❌ Error en la solicitud: {str(e)}")

    # ==========================================
    # PESTAÑA 2: ESTADÍSTICAS Y GESTIÓN (SOLO ADMIN)
    # ==========================================
    if st.session_state.user_role == "ADMIN":
        with tab_stats:
            st.subheader("📊 Histórico y Reasignación de Tickets")

            try:
                stats_resp = requests.get(f"{API_URL}/stats", headers=get_auth_headers())
                tickets_resp = requests.get(f"{API_URL}/tickets", headers=get_auth_headers())

                if stats_resp.status_code == 200 and tickets_resp.status_code == 200:
                    stats = stats_resp.json()
                    tickets = tickets_resp.json()

                    if stats['total_tickets'] == 0:
                        st.info("ℹ️ No hay registros guardados en la base de datos.")
                    else:
                        # 1. KPIs Generales
                        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                        with kpi1:
                            st.metric("Total Tickets", stats['total_tickets'])
                        with kpi2:
                            st.metric("Latencia Media", f"{stats['avg_latency']} s")
                        with kpi3:
                            st.metric("Tokens Medios", stats['avg_tokens'])
                        with kpi4:
                            st.metric("Urgencia Común", stats['top_urgency'])

                        st.markdown("---")

                        # 2. Gráficos
                        g_col1, g_col2 = st.columns(2)
                        with g_col1:
                            st.write("##### 🏢 Incidencias por Departamento")
                            st.bar_chart(stats['tickets_by_department'])
                        with g_col2:
                            st.write("##### 🚨 Distribución de Urgencia")
                            st.bar_chart(stats['tickets_by_urgency'])

                        st.markdown("---")

                        # 3. Lista Interactiva de Tickets con Opción a Editar
                        st.write("##### 📑 Gestión y Reasignación Manual de Incidencias")

                        dept_options = ["Soporte TI", "Recursos Humanos", "Finanzas y Contabilidad", "Legal", "Mantenimiento y Servicios"]
                        urgency_options = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

                        for t in tickets:
                            with st.expander(f"Ticket #{t['id']} | {t['department_name']} | Urgencia: {t['urgency']} | Resumen: {t['summary'][:60]}..."):
                                
                                st.write(f"**Descripción Original:** {t['description']}")
                                st.write(f"**Fecha:** {t['created_at']}")
                                
                                with st.form(key=f"edit_form_{t['id']}"):
                                    col_dept, col_urg = st.columns(2)
                                    
                                    with col_dept:
                                        default_dept_idx = dept_options.index(t['department_name']) if t['department_name'] in dept_options else 0
                                        new_dept = st.selectbox(
                                            "Cambiar Departamento", 
                                            options=dept_options, 
                                            index=default_dept_idx,
                                            key=f"dept_select_{t['id']}"
                                        )

                                    with col_urg:
                                        default_urg_idx = urgency_options.index(t['urgency']) if t['urgency'] in urgency_options else 0
                                        new_urgency = st.selectbox(
                                            "Cambiar Urgencia", 
                                            options=urgency_options, 
                                            index=default_urg_idx,
                                            key=f"urg_select_{t['id']}"
                                        )

                                    update_btn = st.form_submit_button("💾 Guardar Cambios")

                                    if update_btn:
                                        payload = {
                                            "department_name": new_dept,
                                            "urgency": new_urgency
                                        }
                                        patch_resp = requests.patch(
                                            f"{API_URL}/tickets/{t['id']}", 
                                            json=payload,
                                            headers=get_auth_headers()
                                        )

                                        if patch_resp.status_code == 200:
                                            logger.info(f"Streamlit: Admin '{st.session_state.user_email}' actualizó Ticket #{t['id']} a Dept: {new_dept}, Urgencia: {new_urgency}")
                                            st.success(f"✅ Ticket #{t['id']} actualizado correctamente.")
                                            st.rerun()
                                        else:
                                            logger.error(f"Streamlit: Error al actualizar Ticket #{t['id']}: {patch_resp.text}")
                                            st.error(f"❌ Error al actualizar: {patch_resp.text}")

                elif stats_resp.status_code == 401 or tickets_resp.status_code == 401:
                    logger.warning(f"Streamlit: Token expirado en panel Admin para '{st.session_state.user_email}'")
                    st.error("🔒 Token inválido o expirado.")
                    st.session_state.access_token = None
                else:
                    logger.error(f"Streamlit: Error cargando stats Admin ({stats_resp.status_code})")
                    st.error(f"❌ Error al obtener datos ({stats_resp.status_code}): {stats_resp.text}")

            except requests.exceptions.ConnectionError:
                logger.error("Streamlit: No se pudo conectar con la API al cargar estadísticas.")
                st.error("🔌 No se pudo conectar con la API de FastAPI.")
            except Exception as e:
                logger.error(f"Streamlit: Error inesperado cargando stats Admin: {e}")
                st.error(f"❌ Error al cargar las estadísticas: {str(e)}")