import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Observatorio Patrimonial de Chile",
    page_icon="🏛️",
    layout="wide"
)

# =========================================================
# IDENTIDAD VISUAL
# =========================================================

CAFE = "#5B4636"
ARENA = "#EDE3D4"
VERDE = "#66745B"
AZUL = "#3E5D73"
GRIS = "#6B6B6B"
FONDO = "#FAF7F2"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {FONDO};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}

    h1 {{
        color: {CAFE};
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }}

    h2, h3 {{
        color: {CAFE};
    }}

    [data-testid="stSidebar"] {{
        background-color: #F1E8DC;
    }}

    [data-testid="stMetric"] {{
        background-color: white;
        border-left: 5px solid {CAFE};
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }}

    .hero-box {{
        background-color: {ARENA};
        padding: 22px 26px;
        border-radius: 14px;
        margin-bottom: 20px;
        border: 1px solid #DED0BC;
    }}

    .small-note {{
        color: {GRIS};
        font-size: 0.92rem;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# PORTADA / HERO
# =========================================================

st.markdown(
    """
    <div class="hero-box">
        <h1> Observatorio Patrimonial de Chile</h1>
        <p style="font-size:1.15rem; margin-bottom:0;">
        Exploración territorial de los Monumentos Nacionales declarados por decreto,
        a partir de datos públicos obtenidos mediante API REST.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Base estadística actualizada al 10 de enero de 2013. "
    "El análisis representa el recurso consultado y no un catastro actualizado al presente."
)

# =========================================================
# CONEXIÓN A LA API
# =========================================================

url = "https://datos.gob.cl/api/3/action/datastore_search"

parametros = {
    "resource_id": "ac5bc22e-b317-407d-8400-9728235fb2ad",
    "limit": 100
}

try:
    respuesta = requests.get(
        url,
        params=parametros,
        timeout=10
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    registros = datos["result"]["records"]

except Exception as error:
    st.error("No fue posible obtener los datos desde la API.")
    st.write(error)
    st.stop()

# =========================================================
# DATAFRAME Y LIMPIEZA
# =========================================================

tabla = pd.DataFrame(registros)

tabla_con_datos = tabla[
    tabla["TOTAL"].notna()
].copy()

fila_total = tabla_con_datos[
    tabla_con_datos["REGION"] == "TOTAL"
].copy()

tabla_regiones = tabla_con_datos[
    tabla_con_datos["REGION"] != "TOTAL"
].copy()

columnas_numericas = ["MH M", "MH I", "SN", "ZT", "TOTAL", "%"]

for columna in columnas_numericas:
    tabla_regiones[columna] = pd.to_numeric(
        tabla_regiones[columna],
        errors="coerce"
    )

# =========================================================
# VARIABLES Y NOMBRES
# =========================================================

categorias = ["MH M", "MH I", "SN", "ZT"]

nombres = {
    "MH M": "Monumento Histórico Mueble",
    "MH I": "Monumento Histórico Inmueble",
    "SN": "Santuario de la Naturaleza",
    "ZT": "Zona Típica"
}

if len(fila_total) > 0:
    total_nacional = int(fila_total.iloc[0]["TOTAL"])
    total_mhm = int(fila_total.iloc[0]["MH M"])
    total_mhi = int(fila_total.iloc[0]["MH I"])
    total_sn = int(fila_total.iloc[0]["SN"])
    total_zt = int(fila_total.iloc[0]["ZT"])
else:
    total_mhm = int(tabla_regiones["MH M"].sum())
    total_mhi = int(tabla_regiones["MH I"].sum())
    total_sn = int(tabla_regiones["SN"].sum())
    total_zt = int(tabla_regiones["ZT"].sum())
    total_nacional = int(tabla_regiones["TOTAL"].sum())

totales_categoria = {
    "MH M": total_mhm,
    "MH I": total_mhi,
    "SN": total_sn,
    "ZT": total_zt
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Exploración")

vista = st.sidebar.radio(
    "Selecciona una vista",
    [
        "Panorama nacional",
        "Concentración territorial",
        "Perfil regional",
        "Comparación por categoría",
        "Comparador interactivo",
        "Datos"
    ]
)

st.sidebar.divider()

st.sidebar.write("**Fuente**")
st.sidebar.write("datos.gob.cl")
st.sidebar.write("API REST CKAN")

st.sidebar.write("**Fecha del recurso**")
st.sidebar.write("10 enero 2013")

st.sidebar.write("**Regiones analizadas**")
st.sidebar.write(len(tabla_regiones))

# =========================================================
# PANORAMA NACIONAL
# =========================================================

if vista == "Panorama nacional":

    st.subheader("Panorama nacional")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total", f"{total_nacional:,}".replace(",", "."))
    c2.metric("MH M", total_mhm)
    c3.metric("MH I", total_mhi)
    c4.metric("SN", total_sn)
    c5.metric("ZT", total_zt)

    st.write("")

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        ranking = tabla_regiones.sort_values(
            "TOTAL",
            ascending=True
        )

        fig1, ax1 = plt.subplots(figsize=(9, 7))

        ax1.barh(
            ranking["REGION"],
            ranking["TOTAL"]
        )

        ax1.set_title(
            "Ranking regional por cantidad total",
            fontsize=15
        )

        ax1.set_xlabel("Cantidad de monumentos")
        ax1.set_ylabel("")
        ax1.grid(axis="x", alpha=0.2)

        plt.tight_layout()
        st.pyplot(fig1)

    with col_b:
        etiquetas = [
            "MH M",
            "MH I",
            "SN",
            "ZT"
        ]

        valores = [
            total_mhm,
            total_mhi,
            total_sn,
            total_zt
        ]

        fig2, ax2 = plt.subplots(figsize=(7, 7))

        ax2.pie(
            valores,
            labels=etiquetas,
            autopct="%1.1f%%",
            startangle=90
        )

        ax2.set_title(
            "Composición nacional por categoría",
            fontsize=15
        )

        ax2.axis("equal")

        plt.tight_layout()
        st.pyplot(fig2)

    st.info(
        "Lectura rápida: el panel combina una visión territorial "
        "con la composición nacional por tipo de Monumento Nacional."
    )

# =========================================================
# CONCENTRACIÓN TERRITORIAL
# =========================================================

elif vista == "Concentración territorial":

    st.subheader("Concentración territorial")

    tabla_ordenada = tabla_regiones.sort_values(
        "TOTAL",
        ascending=False
    ).copy()

    tabla_ordenada["Participación %"] = (
        tabla_ordenada["TOTAL"]
        / total_nacional
        * 100
    )

    top3_total = tabla_ordenada.head(3)["TOTAL"].sum()

    top3_pct = (
        top3_total
        / total_nacional
        * 100
    )

    region_lider = tabla_ordenada.iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Región líder",
        region_lider["REGION"]
    )

    c2.metric(
        "Monumentos región líder",
        int(region_lider["TOTAL"])
    )

    c3.metric(
        "Concentración Top 3",
        f"{top3_pct:.1f}%"
    )

    st.write("")

    fig3, ax3 = plt.subplots(figsize=(12, 7))

    ax3.bar(
        tabla_ordenada["REGION"],
        tabla_ordenada["Participación %"]
    )

    ax3.set_title(
        "Participación regional sobre el total nacional",
        fontsize=15
    )

    ax3.set_ylabel("Participación (%)")
    ax3.set_xlabel("Región")
    ax3.grid(axis="y", alpha=0.2)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig3)

    st.write(
        f"Las tres regiones con mayor número de monumentos concentran "
        f"aproximadamente **{top3_pct:.1f}%** del total registrado."
    )

# =========================================================
# PERFIL REGIONAL
# =========================================================

elif vista == "Perfil regional":

    st.subheader("Perfil regional")

    regiones = sorted(
        tabla_regiones["REGION"].tolist()
    )

    region = st.selectbox(
        "Selecciona una región",
        regiones
    )

    fila = tabla_regiones[
        tabla_regiones["REGION"] == region
    ].iloc[0]

    participacion = (
        fila["TOTAL"]
        / total_nacional
        * 100
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total regional",
        int(fila["TOTAL"])
    )

    c2.metric(
        "Participación nacional",
        f"{participacion:.1f}%"
    )

    categoria_lider = max(
        categorias,
        key=lambda x: fila[x]
    )

    c3.metric(
        "Categoría predominante",
        categoria_lider
    )

    st.write("")

    col_a, col_b = st.columns([1, 1.3])

    with col_a:
        valores = [
            fila["MH M"],
            fila["MH I"],
            fila["SN"],
            fila["ZT"]
        ]

        fig4, ax4 = plt.subplots(figsize=(6, 6))

        ax4.pie(
            valores,
            labels=categorias,
            autopct="%1.1f%%",
            startangle=90
        )

        ax4.set_title(
            f"Composición de {region}",
            fontsize=15
        )

        ax4.axis("equal")

        plt.tight_layout()
        st.pyplot(fig4)

    with col_b:
        detalle = pd.DataFrame({
            "Categoría": [
                nombres["MH M"],
                nombres["MH I"],
                nombres["SN"],
                nombres["ZT"]
            ],
            "Cantidad": [
                int(fila["MH M"]),
                int(fila["MH I"]),
                int(fila["SN"]),
                int(fila["ZT"])
            ]
        })

        st.write("### Detalle regional")
        st.dataframe(
            detalle,
            use_container_width=True,
            hide_index=True
        )

        st.write(
            f"**{region}** representa aproximadamente "
            f"**{participacion:.1f}%** del total nacional registrado."
        )

# =========================================================
# COMPARACIÓN POR CATEGORÍA
# =========================================================

elif vista == "Comparación por categoría":

    st.subheader("Comparación por categoría")

    categoria_nombre = st.selectbox(
        "Selecciona la categoría",
        list(nombres.values())
    )

    categoria = [
        clave
        for clave, valor in nombres.items()
        if valor == categoria_nombre
    ][0]

    ranking_cat = tabla_regiones.sort_values(
        categoria,
        ascending=True
    )

    region_max = ranking_cat.loc[
        ranking_cat[categoria].idxmax()
    ]

    total_categoria = totales_categoria[categoria]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total nacional categoría",
        total_categoria
    )

    c2.metric(
        "Región líder",
        region_max["REGION"]
    )

    c3.metric(
        "Cantidad región líder",
        int(region_max[categoria])
    )

    fig5, ax5 = plt.subplots(figsize=(11, 7))

    ax5.barh(
        ranking_cat["REGION"],
        ranking_cat[categoria]
    )

    ax5.set_title(
        f"{categoria_nombre} por región",
        fontsize=15
    )

    ax5.set_xlabel("Cantidad")
    ax5.set_ylabel("")
    ax5.grid(axis="x", alpha=0.2)

    plt.tight_layout()
    st.pyplot(fig5)

# =========================================================
# COMPARADOR INTERACTIVO
# =========================================================

elif vista == "Comparador interactivo":

    st.subheader("Comparador interactivo de regiones")

    st.write(
        "Selecciona las regiones y el indicador que quieres comparar. "
        "El gráfico se actualiza automáticamente con cada cambio."
    )

    regiones_disponibles = tabla_regiones["REGION"].tolist()

    regiones_default = [
        "Metropolitana de Santiago",
        "Valparaíso",
        "La Araucanía",
        "Antofagasta",
        "Tarapacá"
    ]

    regiones_default = [
        region
        for region in regiones_default
        if region in regiones_disponibles
    ]

    regiones_seleccionadas = st.multiselect(
        "Regiones a comparar",
        regiones_disponibles,
        default=regiones_default
    )

    indicadores = {
        "Total de Monumentos Nacionales": "TOTAL",
        "Monumento Histórico Mueble (MH M)": "MH M",
        "Monumento Histórico Inmueble (MH I)": "MH I",
        "Santuario de la Naturaleza (SN)": "SN",
        "Zona Típica (ZT)": "ZT"
    }

    indicador_nombre = st.selectbox(
        "Indicador",
        list(indicadores.keys())
    )

    indicador = indicadores[indicador_nombre]

    if len(regiones_seleccionadas) == 0:

        st.warning(
            "Selecciona al menos una región para construir la comparación."
        )

    else:

        datos_comparacion = tabla_regiones[
            tabla_regiones["REGION"].isin(
                regiones_seleccionadas
            )
        ].copy()

        datos_comparacion = datos_comparacion.sort_values(
            indicador,
            ascending=False
        )

        lider = datos_comparacion.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Regiones seleccionadas",
            len(datos_comparacion)
        )

        col2.metric(
            "Mayor valor",
            int(lider[indicador])
        )

        col3.metric(
            "Región líder",
            lider["REGION"]
        )

        fig_interactivo, ax_interactivo = plt.subplots(
            figsize=(11, 6)
        )

        barras = ax_interactivo.bar(
            datos_comparacion["REGION"],
            datos_comparacion[indicador]
        )

        ax_interactivo.set_title(
            f"{indicador_nombre}: comparación seleccionada",
            fontsize=15
        )

        ax_interactivo.set_ylabel("Cantidad")
        ax_interactivo.set_xlabel("")
        ax_interactivo.grid(
            axis="y",
            alpha=0.2
        )

        ax_interactivo.bar_label(
            barras,
            fmt="%.0f",
            padding=3
        )

        plt.xticks(
            rotation=35,
            ha="right"
        )

        plt.tight_layout()

        st.pyplot(fig_interactivo)

        tabla_comparacion = datos_comparacion[
            ["REGION", indicador]
        ].copy()

        tabla_comparacion = tabla_comparacion.rename(
            columns={
                "REGION": "Región",
                indicador: indicador_nombre
            }
        )

        st.dataframe(
            tabla_comparacion,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "La comparación utiliza directamente los datos obtenidos "
            "desde la API y cambia según las regiones y el indicador seleccionados."
        )

# =========================================================
# DATOS
# =========================================================

elif vista == "Datos":

    st.subheader("Base regional utilizada")

    tabla_mostrar = tabla_regiones[
        [
            "REGION",
            "MH M",
            "MH I",
            "SN",
            "ZT",
            "TOTAL",
            "%"
        ]
    ].copy()

    tabla_mostrar["%"] = (
        tabla_mostrar["%"] * 100
    ).round(1)

    tabla_mostrar = tabla_mostrar.rename(
        columns={
            "%": "% del total nacional"
        }
    )

    st.dataframe(
        tabla_mostrar,
        use_container_width=True,
        hide_index=True
    )

    suma_regional = int(
        tabla_regiones["TOTAL"].sum()
    )

    if suma_regional == total_nacional:
        st.success(
            "Validación de consistencia correcta: "
            "la suma regional coincide con el total nacional."
        )
    else:
        st.warning(
            "La suma regional no coincide con el total nacional."
        )

# =========================================================
# PIE DE PÁGINA
# =========================================================

st.divider()

st.caption(
    "Proyecto de análisis de datos con Python | "
    "Fuente: datos.gob.cl | API REST CKAN"
)

st.markdown(
    """
    **Integrantes:**  
    Felipe Salvo  
    Hans Cifuentes  
    Ivannia Gomez  

    **Profesor:**  
    Williams Montes
    """
)
