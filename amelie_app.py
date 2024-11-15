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
        self.cost_fluctuations = {
            'Reagents': {'Lower': -20, 'Base': 0, 'Upper': 20},
            'Energy': {'Lower': -15, 'Base': 0, 'Upper': 25},
            'Labor': {'Lower': -5, 'Base': 0, 'Upper': 10},
            'Maintenance': {'Lower': -10, 'Base': 0, 'Upper': 15},
            'Disposal': {'Lower': -10, 'Base': 0, 'Upper': 10},
            'Microwave Energy': {'Lower': -10, 'Base': 0, 'Upper': 15},
            'Ascorbic Acid': {'Lower': -15, 'Base': 0, 'Upper': 20},
            'Wastewater Treatment': {'Lower': -5, 'Base': 0, 'Upper': 10}
        }
        self.scenarios = {}

    def calculate_totals(self):
        capex_total = sum(self.capex.values())
        opex_total = sum(self.opex.values())
        return capex_total, opex_total

    def generate_pie_chart(self, data, title):
          fig, ax = plt.subplots(figsize=(12, 10))  # Grafico più grande
          # Esplosione di alcune sezioni per evidenziare
          explode = [0.1 if key in ["Reagents", "Energy", "Labor"] else 0 for key in data.keys()]
          wedges, texts, autotexts = ax.pie(
              data.values(),
              labels=None,
              autopct='%1.1f%%',
              startangle=90,
              explode=explode
          )
          ax.set_title(title, fontsize=16)

          # Aggiunta di una legenda per etichette leggibili
          ax.legend(
              loc="upper left",
              labels=[f"{key} ({value} EUR)" for key, value in data.items()],
              fontsize=12,
              bbox_to_anchor=(1, 0.5),
              frameon=False
          )

          # Personalizzazione delle percentuali
          for text in autotexts:
              text.set_fontsize(14)
              text.set_color('black')

          buf = io.BytesIO()
          plt.savefig(buf, format='png', bbox_inches="tight")
          buf.seek(0)
          return buf

    def generate_table(self, data):
        df = pd.DataFrame(list(data.items()), columns=['Category', 'Cost (EUR)'])
        total = df['Cost (EUR)'].sum()
        df.loc[len(df)] = ['Total', total]
        return df

    def add_scenario(self, name, capex_changes, opex_percentage_changes, fluctuation_type):
        self.scenarios[name] = {
            'CapEx': capex_changes,
            'OpExPercentage': opex_percentage_changes,
            'FluctuationType': fluctuation_type
        }

    def apply_scenario(self, name):
        if name in self.scenarios:
            scenario = self.scenarios[name]
            for key, change in scenario['CapEx'].items():
                self.capex[key] = self.capex.get(key, 0) + change
            for key, percentage_change in scenario['OpExPercentage'].items():
                self.opex[key] *= (1 + percentage_change / 100)
            for cost, fluctuation in self.cost_fluctuations.items():
                fluctuation_percentage = fluctuation[scenario['FluctuationType']]
                if cost in self.opex:
                    self.opex[cost] *= (1 + fluctuation_percentage / 100)

    def get_assumptions(self, scenario_name):
      assumptions = """
      ### General Assumptions:
      1. Pilot project sized for 10 kg BM per batch.
      2. No infrastructure costs.
      3. Process: BM pre-treatment (drying), microwave-assisted thermal treatment, leaching in water, precipitation for lithium recovery, secondary drying, leaching in acid (malic acid and hydrogen peroxide), additional precipitation for Co, Ni, and Mn recovery, and wastewater treatment.
      4. Energy cost calculated dynamically based on kWh per machine.
      5. Labor includes one operator per batch.
      6. Maintenance and disposal are estimated.
      7. Microwave-assisted thermal treatment considered (source: Aznar, p. 57).
      8. Use of ascorbic/malic acid for leaching based on AMELIE project results (source: Gaeta, p. 30).
      9. Cost fluctuations are calculated based on the following ranges:
         - **Lower Range**:
           - Reagents: -20%
           - Energy: -15%
           - Labor: -5%
           - Maintenance: -10%
           - Disposal: -10%
           - Microwave Energy: -10%
           - Ascorbic Acid: -15%
           - Wastewater Treatment: -5%
         - **Base Range**:
           - No fluctuations applied.
         - **Upper Range**:
           - Reagents: +20%
           - Energy: +25%
           - Labor: +10%
           - Maintenance: +15%
           - Disposal: +10%
           - Microwave Energy: +15%
           - Ascorbic Acid: +20%
           - Wastewater Treatment: +10%
      """

      # Specific assumptions based on the scenario
      if scenario_name == "Lower Utility Costs":
          assumptions += """
          ### Specific Assumptions for Lower Utility Costs:
          - Reduced energy consumption due to optimized operations.
          - 15% reduction in energy costs.
          - 5% reduction in labor costs.
          - Lower range of cost fluctuations applied.
          """
      elif scenario_name == "Base Utility Costs":
          assumptions += """
          ### Specific Assumptions for Base Utility Costs:
          - Standard energy consumption and costs.
          - No cost fluctuations applied.
          """
      elif scenario_name == "Upper Utility Costs":
          assumptions += """
          ### Specific Assumptions for Upper Utility Costs:
          - Increased energy consumption due to inefficiencies.
          - 25% increase in energy costs.
          - 10% increase in labor costs.
          - Upper range of cost fluctuations applied.
          """
      else:
          assumptions += """
          ### Specific Assumptions:
          - No specific assumptions provided for this scenario.
          """
      return assumptions



# Streamlit App
model = AmelieEconomicModel()

# Add scenarios
model.add_scenario(
    "Lower Utility Costs",
    capex_changes={},
    opex_percentage_changes={"Labor": -5},
    fluctuation_type="Lower"
)
model.add_scenario(
    "Base Utility Costs",
    capex_changes={},
    opex_percentage_changes={},
    fluctuation_type="Base"
)
model.add_scenario(
    "Upper Utility Costs",
    capex_changes={},
    opex_percentage_changes={"Labor": 10},
    fluctuation_type="Upper"
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
capex_table = model.generate_table(model.capex)
st.table(capex_table)

st.subheader("OpEx Table")
opex_table = model.generate_table(model.opex)
st.table(opex_table)
