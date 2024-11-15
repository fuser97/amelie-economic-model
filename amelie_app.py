import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import io

class AmelieEconomicModel:
    def __init__(self):
        self.capex = {
            'Leaching Reactor': 20000,
            'Press Filter': 15000,
            'Precipitation Reactor': 18000,
            'Solvent Extraction Unit': 30000,
            'Microwave Thermal Treatment Unit': 25000,
            'Pre-treatment Dryer': 15000,
            'Secondary Dryer': 12000,
            'Wastewater Treatment Unit': 18000
        }
        self.opex = {
            'Reagents': 90,
            'Energy': 44,
            'Labor': 80,
            'Maintenance': 20,
            'Disposal': 12.5,
            'Microwave Energy': 6.0,
            'Drying Energy (Pre-treatment)': 3.5,
            'Drying Energy (Secondary)': 2.5,
            'Malic Acid': 8.0,
            'Hydrogen Peroxide': 4.0,
            'Lithium Precipitation Reagents': 5.0,
            'Co/Ni/Mn Precipitation Reagents': 7.0,
            'Wastewater Treatment Chemicals': 6.0
        }
        self.scenarios = {}

    def calculate_totals(self):
        capex_total = sum(self.capex.values())
        opex_total = sum(self.opex.values())
        return capex_total, opex_total

    def generate_pie_chart(self, data, title):
        fig, ax = plt.subplots(figsize=(10, 8))  # Increased size
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title(title, fontsize=16)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return buf

    def generate_table(self, data, title):
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Cost (EUR)'])
        total = df['Cost (EUR)'].sum()
        df.loc[len(df)] = ['Total', total]
        return df

    def add_scenario(self, name, capex_changes, opex_percentage_changes, energy_cost_variation=None):
        self.scenarios[name] = {
            'CapEx': capex_changes,
            'OpExPercentage': opex_percentage_changes,
            'EnergyCostVariation': energy_cost_variation
        }

    def apply_scenario(self, name):
        if name in self.scenarios:
            scenario = self.scenarios[name]
            for key, change in scenario['CapEx'].items():
                self.capex[key] = self.capex.get(key, 0) + change
            for key, percentage_change in scenario['OpExPercentage'].items():
                self.opex[key] *= (1 + percentage_change / 100)
            if scenario.get('EnergyCostVariation') is not None:
                self.opex['Energy'] *= (1 + scenario['EnergyCostVariation'] / 100)

    def get_assumptions(self, scenario_name):
        assumptions = f"""
        ### General Assumptions:
        1. Pilot project sized for 10 kg BM per batch.
        2. No infrastructure costs.
        3. Process includes BM pre-treatment, microwave-assisted thermal treatment, leaching in water and acid, precipitation, and wastewater treatment.
        4. Energy cost calculated dynamically based on kWh per machine.
        5. Labor includes one operator per batch.
        6. Maintenance and disposal are estimated.
        
        ### Specific Assumptions for {scenario_name}:
        """
        if scenario_name == "Lower Utility Costs":
            assumptions += "- Reduced energy consumption.\n- 15% reduction in energy costs.\n- 5% reduction in labor costs."
        elif scenario_name == "Base Utility Costs":
            assumptions += "- Standard energy consumption and costs."
        elif scenario_name == "Upper Utility Costs":
            assumptions += "- Increased energy consumption.\n- 25% increase in energy costs.\n- 10% increase in labor costs."
        else:
            assumptions += "No specific assumptions provided."
        return assumptions

# Streamlit App
model = AmelieEconomicModel()

# Add scenarios
model.add_scenario(
    "Lower Utility Costs",
    capex_changes={},
    opex_percentage_changes={"Energy": -15, "Labor": -5},
    energy_cost_variation=-15
)
model.add_scenario(
    "Base Utility Costs",
    capex_changes={},
    opex_percentage_changes={},
    energy_cost_variation=0
)
model.add_scenario(
    "Upper Utility Costs",
    capex_changes={},
    opex_percentage_changes={"Energy": 25, "Labor": 10},
    energy_cost_variation=25
)

st.title("Amelie Economic Model")

# Dropdown menu for scenario selection
scenario_name = st.selectbox("Select a scenario:", list(model.scenarios.keys()))

if st.button("Apply Scenario"):
    model.apply_scenario(scenario_name)

capex_total, opex_total = model.calculate_totals()

st.subheader(f"Assumptions for {scenario_name}")
st.markdown(model.get_assumptions(scenario_name))

st.subheader("Results")
st.write(f"**Total CapEx:** {capex_total} EUR")
st.write(f"**Total OpEx:** {opex_total} EUR/batch")

# CapEx Chart
st.subheader("CapEx Breakdown")
capex_chart_buf = model.generate_pie_chart(model.capex, "CapEx Breakdown")
st.image(capex_chart_buf, caption="CapEx Pie Chart", use_column_width=True)

# OpEx Chart
st.subheader("OpEx Breakdown")
opex_chart_buf = model.generate_pie_chart(model.opex, "OpEx Breakdown")
st.image(opex_chart_buf, caption="OpEx Pie Chart", use_column_width=True)

# Display tables
st.subheader("CapEx Table")
capex_table = model.generate_table(model.capex, "CapEx Breakdown")
st.table(capex_table)

st.subheader("OpEx Table")
opex_table = model.generate_table(model.opex, "OpEx Breakdown")
st.table(opex_table)
