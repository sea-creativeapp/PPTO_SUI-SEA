import streamlit as st
import pandas as pd
import json
from datetime import datetime
import random

st.set_page_config(page_title="Presupuesto SSPD v3 - SEA", layout="wide", page_icon="📊")

# ==================== DATOS BASE ====================
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

# ==================== SESSION STATE ====================
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
    st.session_state.current_month = 4

# ==================== UTILIDADES ====================
def fmt_ton(n): return f"{round(n,1):,.1f}"
def fmt_cop(n): return f"${int(round(n)):,.0f}"

def generate_month(month_idx):
    facturas = []
    sspd_rows = []
    fac_num = 25000 + month_idx * 200 + 1
    params = st.session_state.month_params[month_idx]

    for mat in MATERIALES:
        p = next((x for x in params if x["id"] == mat["id"]), None)
        if not p or p["nFact"] <= 0: continue
        total_kg = int(p["ton"] * 1000)
        n_fact = p["nFact"]

        kg_distrib = []
        remaining = total_kg
        for i in range(n_fact):
            if i == n_fact - 1:
                kg_distrib.append(remaining)
                break
            base = remaining // (n_fact - i)
            v = random.uniform(0.05, 0.15)
            sign = 1 if random.random() > 0.5 else -1
            kg = int(base * (1 + sign * v))
            kg = max(100, min(kg, remaining - 100 * (n_fact - i - 1)))
            kg_distrib.append(kg)
            remaining -= kg

        for kg in kg_distrib:
            precio = p["precio"]
            if mat["tipo"] == "presupuestal":
                precio = max(1, int(precio * (1 + random.uniform(-0.03, 0.03))))
            subtotal = kg * precio
            iva = int(subtotal * 0.19) if mat["iva"] else 0
            f_num = fac_num
            fac_num += 1

            facturas.append({
                "num": f_num, "matIntern": mat["interno"], "matSSPD": mat["sspd"],
                "cliente": mat["cliente"], "nit": mat["nit"], "kg": kg,
                "precio": precio, "subtotal": subtotal, "iva": iva,
                "totalIva": subtotal + iva, "tipo": mat["tipo"]
            })

            kg_left = kg
            for mu in MUNICIPIOS:
                kg_mu = int(kg * (mu["pct"] / 100)) if mu != MUNICIPIOS[-1] else kg_left
                kg_mu = min(max(0, kg_mu), kg_left)
                if kg_mu > 0:
                    sspd_rows.append({
                        "numFact": f_num, "matSSPD": mat["sspd"], "cliente": mat["cliente"],
                        "nit": mat["nit"], "municipio": mu["muni"], "dept": mu["dept"],
                        "kg": kg_mu, "ton": round(kg_mu/1000, 3), "valorKg": precio,
                        "subtotal": int(kg_mu * precio), "totalIva": int(kg_mu * precio * (1.19 if mat["iva"] else 1))
                    })
                    kg_left -= kg_mu

    st.session_state.generated_data[month_idx] = {"facturas": facturas, "sspd": sspd_rows}
    st.success(f"✅ Mes {MONTHS[month_idx]} 2026 generado correctamente")
    st.rerun()

# ==================== TABS ====================
tab_pres, tab_fact, tab_sspd, tab_muni, tab_proj, tab_cargas = st.tabs([
    "📊 Presupuesto", "📄 Facturas generadas", "📋 Distribución SSPD",
    "🏙️ Parámetros municipios", "📈 Proyección 12M", "📥 Cargas & Configuración"
])

# TAB 1 - PRESUPUESTO
with tab_pres:
    st.subheader(f"Presupuesto — {MONTHS[st.session_state.current_month]} 2026")
    params = st.session_state.month_params[st.session_state.current_month]
    total_ton = sum(p["ton"] for p in params)
    total_val = sum(p["ton"]*1000*p["precio"]*(1.19 if next(m for m in MATERIALES if m["id"]==p["id"])["iva"] else 1) for p in params)

    col1, col2, col3 = st.columns(3)
    col1.metric("Toneladas objetivo", fmt_ton(total_ton))
    col2.metric("Valor total est.", fmt_cop(total_val))
    col3.metric("Facturas est.", sum(p["nFact"] for p in params))

    df = pd.DataFrame(params)
    df["Material"] = [next(m["interno"] for m in MATERIALES if m["id"] == pid) for pid in df["id"]]
    edited = st.data_editor(df[["Material","ton","precio","nFact"]], use_container_width=True, hide_index=True,
                            column_config={"ton": st.column_config.NumberColumn("Ton", format="%.1f"),
                                           "precio": st.column_config.NumberColumn("Precio/kg $", format="$%.0f")})
    for i, row in edited.iterrows():
        st.session_state.month_params[st.session_state.current_month][i].update({"ton": float(row["ton"]), "precio": int(row["precio"]), "nFact": int(row["nFact"])})

    if st.button("🚀 Generar este mes", type="primary", use_container_width=True):
        generate_month(st.session_state.current_month)

# TAB 2 - FACTURAS
with tab_fact:
    st.subheader("Facturas generadas")
    data = st.session_state.generated_data.get(st.session_state.current_month)
    if data:
        df_fact = pd.DataFrame(data["facturas"])
        st.dataframe(df_fact, use_container_width=True)
        st.download_button("⬇ Exportar Facturas CSV", df_fact.to_csv(index=False, sep=";"), f"Facturas_{MONTHS[st.session_state.current_month]}.csv", "text/csv")
    else:
        st.info("Genera el mes primero usando el botón en la pestaña Presupuesto")

# TAB 3 - SSPD
with tab_sspd:
    st.subheader("Distribución SSPD")
    data = st.session_state.generated_data.get(st.session_state.current_month)
    if data:
        df_sspd = pd.DataFrame(data["sspd"])
        st.dataframe(df_sspd, use_container_width=True)
        st.download_button("⬇ Exportar Reporte SSPD CSV", df_sspd.to_csv(index=False, sep=";"), f"Reporte_SSPD_{MONTHS[st.session_state.current_month]}.csv", "text/csv")
    else:
        st.info("Genera el mes primero")

# TAB 4 - MUNICIPIOS
with tab_muni:
    st.subheader("Parámetros de distribución municipal")
    muni_df = pd.DataFrame(MUNICIPIOS)
    edited_muni = st.data_editor(muni_df, use_container_width=True, hide_index=True)
    for i, row in edited_muni.iterrows():
        MUNICIPIOS[i]["pct"] = float(row["pct"])

# TAB 5 - PROYECCIÓN
with tab_proj:
    st.subheader("Proyección anual 2026")
    ton_data = [sum(p["ton"] for p in st.session_state.month_params[m]) for m in range(12)]
    fig = go.Figure()
    fig.add_bar(x=MONTHS, y=ton_data, name="Toneladas", marker_color="#4ade80")
    st.plotly_chart(fig, use_container_width=True)

# TAB 6 - CARGAS & CONFIGURACIÓN
with tab_cargas:
    st.subheader("📥 Cargas Históricas y Configuración")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📄 Plantilla Facturación Interna", pd.DataFrame([{"Material_Interno":m["interno"],"KG":int(m["histTon"]*1000),"Precio_KG":m["precio"]} for m in MATERIALES]).to_csv(index=False, sep=";"), "Plantilla_Facturacion_Interna.csv", "text/csv")
    with col2:
        st.download_button("📄 Plantilla SSPD", pd.DataFrame([{"Municipio_Origen":m["muni"],"KG_Facturados":10000} for m in MUNICIPIOS]).to_csv(index=False, sep=";"), "Plantilla_SSPD.csv", "text/csv")
    with col3:
        st.download_button("📄 Plantilla Parcial", pd.DataFrame([{"Material_Interno":m["interno"],"KG":5000,"Precio_KG":m["precio"]} for m in MATERIALES]).to_csv(index=False, sep=";"), "Plantilla_Parcial.csv", "text/csv")

    st.divider()
    st.subheader("Base Histórica de Toneladas")
    base_df = pd.DataFrame([{"Material": m["interno"], "Ton_Base": st.session_state.base_tons[m["id"]]} for m in MATERIALES])
    edited_base = st.data_editor(base_df, use_container_width=True, hide_index=True)
    for _, row in edited_base.iterrows():
        mat_id = next(m["id"] for m in MATERIALES if m["interno"] == row["Material"])
        st.session_state.base_tons[mat_id] = float(row["Ton_Base"])

    st.divider()
    st.subheader("💾 Portabilidad entre equipos")
    colA, colB = st.columns(2)
    with colA:
        export_data = {"month_params": st.session_state.month_params, "generated_data": st.session_state.generated_data,
                       "current_month": st.session_state.current_month, "base_tons": st.session_state.base_tons, "munis": MUNICIPIOS}
        st.download_button("📤 Exportar TODO como JSON", json.dumps(export_data, indent=2), f"SEA_Presupuesto_{datetime.now().strftime('%Y%m%d')}.json", "application/json")
    with colB:
        json_file = st.file_uploader("📥 Importar JSON", type="json")
        if json_file and st.button("Importar configuración"):
            imported = json.load(json_file)
            st.session_state.month_params = imported.get("month_params", st.session_state.month_params)
            st.session_state.generated_data = imported.get("generated_data", st.session_state.generated_data)
            st.session_state.current_month = imported.get("current_month", st.session_state.current_month)
            st.session_state.base_tons = imported.get("base_tons", st.session_state.base_tons)
            st.success("✅ Configuración importada")

st.caption("✅ Presupuesto de Facturación SSPD v3 completa — Servicios Empresariales de Aseo S.A.S E.S.P. | Normativa Superintendencia de Servicios Públicos")
