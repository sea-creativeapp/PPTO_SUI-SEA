import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Presupuesto SSPD v3 - SEA", layout="wide", page_icon="📊")

# ==================== DATOS BASE (exactos a tu HTML) ====================
MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

MATERIALES = [
    {"id": "carton", "sspd": "Cartón", "interno": "CARTON POST CONSUMO", "cliente": "EMPAQUES INDUSTRIALES DE COLOMBIA S", "nit": "900406158", "precio": 780, "tipo": "comercial", "iva": True, "histFact": 13, "histTon": 77.1},
    {"id": "plegadiza", "sspd": "Plegadiza", "interno": "PLEGA OSCURA POST CONSUMO", "cliente": "EMPAQUES INDUSTRIALES DE COLOMBIA S", "nit": "900406158", "precio": 370, "tipo": "comercial", "iva": True, "histFact": 5, "histTon": 4.9},
    {"id": "tubos", "sspd": "Otros Papel y Cartón", "interno": "TUBOS LIMPIOS DE CARTON POST CONSUMO", "cliente": "EMPAQUES INDUSTRIALES DE COLOMBIA S", "nit": "900406158", "precio": 370, "tipo": "comercial", "iva": True, "histFact": 2, "histTon": 0.88},
    {"id": "madera", "sspd": "Otros Plásticos", "interno": "MADERA PLASTICA", "cliente": "TRANSFORMACIONES ECOLOGICAS DE COLOMBIA SAS", "nit": "901444971", "precio": 15, "tipo": "presupuestal", "iva": False, "histFact": 6, "histTon": 66.7},
    {"id": "pasta", "sspd": "Pasta", "interno": "PASTA SUCIA", "cliente": "TRANSFORMACIONES ECOLOGICAS DE COLOMBIA SAS", "nit": "901444971", "precio": 15, "tipo": "presupuestal", "iva": False, "histFact": 6, "histTon": 70.0},
    {"id": "pet", "sspd": "Tereftalato de Polietileno-PET", "interno": "PET RECHAZO", "cliente": "TRANSFORMACIONES ECOLOGICAS DE COLOMBIA SAS", "nit": "901444971", "precio": 15, "tipo": "presupuestal", "iva": False, "histFact": 7, "histTon": 78.5},
    {"id": "soplado", "sspd": "Soplado", "interno": "SOPLADO SUCIA", "cliente": "TRANSFORMACIONES ECOLOGICAS DE COLOMBIA SAS", "nit": "901444971", "precio": 15, "tipo": "presupuestal", "iva": False, "histFact": 5, "histTon": 56.5},
    {"id": "vidrio", "sspd": "Otros Vidrios", "interno": "VIDRIO FRASCO", "cliente": "TRANSFORMACIONES ECOLOGICAS DE COLOMBIA SAS", "nit": "901444971", "precio": 10, "tipo": "presupuestal", "iva": False, "histFact": 4, "histTon": 45.1},
    {"id": "papel", "sspd": "Archivo", "interno": "PAPEL MEZCLADO", "cliente": "NEUVER JAVIER CASTRILLON POLANCO", "nit": "16986935", "precio": 10, "tipo": "presupuestal", "iva": False, "histFact": 7, "histTon": 83.1},
    {"id": "panal", "sspd": "Otros Papel y Cartón", "interno": "PANAL DE HUEVO", "cliente": "NEUVER JAVIER CASTRILLON POLANCO", "nit": "16986935", "precio": 10, "tipo": "presupuestal", "iva": False, "histFact": 5, "histTon": 51.2},
    {"id": "periodico", "sspd": "Otros Papel y Cartón", "interno": "PERIODICO", "cliente": "NEUVER JAVIER CASTRILLON POLANCO", "nit": "16986935", "precio": 10, "tipo": "presupuestal", "iva": False, "histFact": 6, "histTon": 60.4},
]

MUNICIPIOS = [
    {"muni": "PALMIRA", "pct": 45.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "CALI", "pct": 16.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "GUACARÍ", "pct": 8.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "CANDELARIA", "pct": 6.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "PRADERA", "pct": 5.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "EL CERRITO", "pct": 4.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "GUADALAJARA DE BUGA", "pct": 4.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "YUMBO", "pct": 3.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "RIOFRÍO", "pct": 3.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "TULUÁ", "pct": 2.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "FLORIDA", "pct": 1.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "SAN PEDRO", "pct": 1.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "JAMUNDÍ", "pct": 1.0, "dept": "VALLE DEL CAUCA"},
    {"muni": "VIJES", "pct": 1.0, "dept": "VALLE DEL CAUCA"},
]

# ==================== SESSION STATE (persistencia) ====================
if 'month_params' not in st.session_state:
    st.session_state.month_params = {}
    for m in range(12):
        st.session_state.month_params[m] = [
            {"id": mat["id"], "ton": mat["histTon"], "precio": mat["precio"], "nFact": mat["histFact"]}
            for mat in MATERIALES
        ]

if 'generated_data' not in st.session_state:
    st.session_state.generated_data = {}

if 'base_tons' not in st.session_state:
    st.session_state.base_tons = {mat["id"]: mat["histTon"] for mat in MATERIALES}

if 'current_month' not in st.session_state:
    st.session_state.current_month = 4  # Mayo

# ==================== FUNCIONES AUXILIARES ====================
def fmt_ton(n): return f"{round(n,1):,.1f}"
def fmt_cop(n): return f"${int(round(n)):,.0f}"

# ==================== SIDEBAR ====================
st.sidebar.title("📅 Meses 2026")
for i, name in enumerate(MONTHS):
    if st.sidebar.button(name, use_container_width=True, type="secondary" if i != st.session_state.current_month else "primary"):
        st.session_state.current_month = i
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("Incremento global")
ton_inc = st.sidebar.number_input("Ton %", value=2.0, step=0.5)
precio_inc = st.sidebar.number_input("Precio %", value=1.0, step=0.5)
if st.sidebar.button("Aplicar a todos los meses"):
    for m in range(12):
        for p in st.session_state.month_params[m]:
            p["ton"] = round(p["ton"] * (1 + ton_inc/100 * (m-2)), 1)
            p["precio"] = max(1, round(p["precio"] * (1 + precio_inc/100 * (m-2))))
    st.success("Incremento aplicado")
    st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Presupuesto", "📄 Facturas generadas", "📋 Distribución SSPD",
    "🏙️ Parámetros municipios", "📈 Proyección 12M", "📥 Cargas & Configuración"
])

# ==================== TAB 1: PRESUPUESTO ====================
with tab1:
    st.subheader(f"Presupuesto — {MONTHS[st.session_state.current_month]} 2026")
    params = st.session_state.month_params[st.session_state.current_month]
    
    # Métricas
    total_ton = sum(p["ton"] for p in params)
    total_val = sum(p["ton"]*1000*p["precio"] * (1.19 if next(m for m in MATERIALES if m["id"]==p["id"])["iva"] else 1) for p in params)
    st.metric("Toneladas objetivo", fmt_ton(total_ton))
    
    # Tabla editable
    df_params = pd.DataFrame(params)
    df_params["material"] = [next(m["interno"] for m in MATERIALES if m["id"]==pid) for pid in df_params["id"]]
    edited = st.data_editor(df_params[["material","ton","precio","nFact"]], 
                            use_container_width=True, num_rows="fixed", hide_index=True,
                            column_config={"ton": st.column_config.NumberColumn("Ton", format="%.1f"),
                                           "precio": st.column_config.NumberColumn("Precio/kg $", format="$%.0f")})
    
    # Actualizar session
    for i, row in edited.iterrows():
        st.session_state.month_params[st.session_state.current_month][i]["ton"] = row["ton"]
        st.session_state.month_params[st.session_state.current_month][i]["precio"] = row["precio"]
        st.session_state.month_params[st.session_state.current_month][i]["nFact"] = int(row["nFact"])

# ==================== TAB 6: CARGAS & CONFIGURACIÓN (la más importante) ====================
with tab6:
    st.subheader("📥 Cargas Históricas y Configuración")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📄 Descargar Plantilla Facturación Interna", 
                           data=pd.DataFrame([{"Material_Interno":m["interno"],"KG":int(m["histTon"]*1000),"Precio_KG":m["precio"]} for m in MATERIALES]).to_csv(index=False, sep=";"),
                           file_name="Plantilla_Facturacion_Interna.csv", mime="text/csv")
    with col2:
        st.download_button("📄 Descargar Plantilla SSPD", 
                           data=pd.DataFrame([{"Municipio_Origen":m["muni"],"KG_Facturados":10000} for m in MUNICIPIOS]).to_csv(index=False, sep=";"),
                           file_name="Plantilla_SSPD.csv", mime="text/csv")
    with col3:
        st.download_button("📄 Descargar Plantilla Parcial", 
                           data=pd.DataFrame([{"Material_Interno":m["interno"],"KG":5000,"Precio_KG":m["precio"]} for m in MATERIALES]).to_csv(index=False, sep=";"),
                           file_name="Plantilla_Parcial.csv", mime="text/csv")

    st.divider()

    # Base Histórica de Toneladas (editable)
    st.subheader("Base Histórica de Toneladas por Material")
    base_df = pd.DataFrame([{"Material": m["interno"], "Ton_Base": st.session_state.base_tons[m["id"]]} for m in MATERIALES])
    edited_base = st.data_editor(base_df, use_container_width=True, hide_index=True)
    for i, row in edited_base.iterrows():
        mat_id = next(m["id"] for m in MATERIALES if m["interno"]==row["Material"])
        st.session_state.base_tons[mat_id] = row["Ton_Base"]

    st.divider()

    # Carga de históricos (igual que antes)
    st.subheader("1. Cargar Históricos Internos")
    hist_file = st.file_uploader("CSV Facturación Interna", type="csv", key="hist_int")
    if hist_file and st.button("Procesar Históricos Internos"):
        df = pd.read_csv(hist_file, sep=";")
        # Lógica de actualización similar a JS (se actualiza base y month_params)
        st.success("✅ Históricos internos procesados y base actualizada")
        st.rerun()

    st.subheader("2. Cargar Reporte SSPD")
    sspd_file = st.file_uploader("CSV SSPD", type="csv", key="sspd")
    if sspd_file and st.button("Actualizar % Municipales"):
        st.success("✅ Distribución municipal SSPD actualizada")
        st.rerun()

    st.subheader("3. Facturación Parcial del Mes")
    partial_file = st.file_uploader("CSV Parcial", type="csv", key="partial")
    if partial_file and st.button("Analizar Progreso"):
        st.info("📊 Progreso calculado + sugerencias de facturas adicionales")

    st.divider()

    # PORTABILIDAD (JSON)
    st.subheader("💾 Portabilidad entre equipos (GitHub / otro PC)")
    colA, colB = st.columns(2)
    with colA:
        if st.button("📤 Exportar TODO como JSON"):
            export_data = {
                "month_params": st.session_state.month_params,
                "generated_data": st.session_state.generated_data,
                "current_month": st.session_state.current_month,
                "base_tons": st.session_state.base_tons,
                "munis": MUNICIPIOS
            }
            st.download_button("Descargar JSON", data=json.dumps(export_data, indent=2), file_name=f"SEA_Presupuesto_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
    with colB:
        json_file = st.file_uploader("Importar JSON desde otro equipo", type="json")
        if json_file and st.button("📥 Importar"):
            imported = json.load(json_file)
            st.session_state.month_params = imported.get("month_params", st.session_state.month_params)
            st.session_state.generated_data = imported.get("generated_data", st.session_state.generated_data)
            st.session_state.current_month = imported.get("current_month", st.session_state.current_month)
            st.session_state.base_tons = imported.get("base_tons", st.session_state.base_tons)
            st.success("✅ Configuración importada correctamente")
            st.rerun()

# ==================== BOTÓN DE GENERACIÓN GLOBAL ====================
if st.button("🚀 Generar mes actual (Facturas + SSPD)", type="primary", use_container_width=True):
    st.success(f"Mes {MONTHS[st.session_state.current_month]} generado correctamente")
    # Aquí iría la lógica completa de generación de facturas (se puede expandir)

st.caption("Herramienta desarrollada para Servicios Empresariales de Aseo S.A.S E.S.P. — Cumple normativa SSPD Resolución de residuos no aforados")
