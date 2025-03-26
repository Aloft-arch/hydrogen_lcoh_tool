# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 15:09:32 2025

@author: vasbes
"""

# hydrogen_lcoh_tool.py

import streamlit as st
import pandas as pd

# === PAGE CONFIG ===
st.set_page_config(page_title="🔐 Hydrogen LCOH Calculator", layout="centered")

# === SIMPLE PASSWORD PROTECTION ===
def check_password():
    def password_entered():
        if st.session_state["password"] == "norconsult123":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["authenticated"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.warning("Incorrect password.")
        st.stop()

check_password()

# === APP TITLE ===
st.title("⚡ Hydrogen LCOH & CO₂ Savings Calculator")
st.markdown("Estimate **Levelized Cost of Hydrogen (LCOH)** and **CO₂ savings** based on your electrolyzer setup.")

# === USER INPUTS ===
st.subheader("🔧 Electrolyzer and Cost Parameters")

capacity_mw = st.number_input("Electrolyzer capacity (MW)", min_value=1.0, value=20.0, step=1.0)
efficiency_kwh_per_kg = st.number_input("Specific energy consumption (kWh/kg H₂)", min_value=30.0, value=52.5, step=0.5)
full_load_hours = st.number_input("Full load hours per year", min_value=1000, max_value=8760, value=4000, step=100)
capex_eur_per_kw = st.number_input("CAPEX (€ per kW)", min_value=300, value=1000, step=50)
opex_percent = st.number_input("OPEX (% of CAPEX per year)", min_value=1.0, value=4.0, step=0.5)
electricity_cost_eur_per_mwh = st.number_input("Electricity cost (€ per MWh)", min_value=10, value=50, step=5)
lifetime_years = st.number_input("Plant lifetime (years)", min_value=1, value=20, step=1)

# === CALCULATIONS ===
capacity_kw = capacity_mw * 1000
total_energy_kwh_per_year = capacity_kw * full_load_hours
hydrogen_kg_per_year = total_energy_kwh_per_year / efficiency_kwh_per_kg

capex_total = capex_eur_per_kw * capacity_kw
opex_annual = (opex_percent / 100) * capex_total
electricity_cost_annual = (total_energy_kwh_per_year / 1000) * electricity_cost_eur_per_mwh
annualized_capex = capex_total / lifetime_years

total_annual_cost = opex_annual + electricity_cost_annual + annualized_capex
lcoh = total_annual_cost / hydrogen_kg_per_year

# CO₂ savings (vs grey H₂ ~10.6 kg CO₂ per kg H₂)
co2_savings_per_kg = 10.6
total_co2_savings_tons = hydrogen_kg_per_year * co2_savings_per_kg / 1000

# === RESULTS ===
st.subheader("📈 Results")
st.markdown(f"**Annual H₂ Production:** `{hydrogen_kg_per_year:,.0f}` kg")
st.markdown(f"**Levelized Cost of H₂ (LCOH):** `{lcoh:.2f} € / kg`")
st.markdown(f"**CO₂ Savings vs Grey H₂:** `{total_co2_savings_tons:,.0f}` tons/year")

# === EXPORT ===
st.subheader("📥 Export Summary")
df_export = pd.DataFrame([{
    "H₂ production (kg/year)": round(hydrogen_kg_per_year),
    "LCOH (€/kg)": round(lcoh, 2),
    "CO₂ savings (t/year)": round(total_co2_savings_tons),
    "Electrolyzer capacity (MW)": capacity_mw,
    "Efficiency (kWh/kg)": efficiency_kwh_per_kg,
    "Full load hours": full_load_hours,
    "CAPEX (€/kW)": capex_eur_per_kw,
    "OPEX (%)": opex_percent,
    "Electricity cost (€/MWh)": electricity_cost_eur_per_mwh,
    "Lifetime (years)": lifetime_years
}])
st.download_button("Download CSV", df_export.to_csv(index=False).encode(), file_name="h2_lcoh_summary.csv", mime="text/csv")
