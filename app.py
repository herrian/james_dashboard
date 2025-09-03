import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Title
st.title("James' Dashboard")

# Sidebar tabs
sections = ["Welcome", "Upload & Edit Data", "Visualise Data"]
selected_section = st.sidebar.radio("Select Section", sections)

# --- Persistent file uploader ---
def get_uploaded_file(key="uploaded_file"):
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    # Save uploaded file to session state if it's new
    if uploaded_file is not None:
        st.session_state[key] = uploaded_file
    
    # Return previously uploaded file if exists
    return st.session_state.get(key, None)

# --- Welcome Section ---
if selected_section == "Welcome":
    st.subheader("Welcome!")
    st.write("""
    This dashboard is the property of James.
    - Use the 'Upload & Edit Data' tab to upload your dataset and make changes to it.
    - Use the 'Visualise Data' tab to create your own charts.
    """)

# --- Upload & Edit Data Section ---
elif selected_section == "Upload & Edit Data":
    st.subheader("Upload Your Dataset")
    uploaded_file = get_uploaded_file("upload_edit_file")

    df = None
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.write("Data Preview (CSV):")
            st.dataframe(df.head())
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            selected_sheet = st.selectbox("Select a sheet", sheet_names)
            df = pd.read_excel(xls, sheet_name=selected_sheet)
            st.write(f"Data Preview: {selected_sheet}")
            st.dataframe(df.head())

        # --- Show last X rows ---
        if not df.empty:
            row_options = [5, 10, 20, 50]
            num_rows = st.selectbox("Show last N rows", row_options, index=0)
            recent_df = df.tail(num_rows)
            st.write(f"Last {num_rows} rows of data:")
            st.dataframe(recent_df)

        # --- Dynamic Input Section ---
        st.write("---")
        st.subheader("Add a New Entry")

        # Persistent main inputs
        input_date = st.text_input("Date (MM-DD-YYYY)", value=st.session_state.get("input_date", ""))
        input_aircraft_total = st.number_input(
            "Daily Aircraft Detected", min_value=0, step=1,
            value=st.session_state.get("input_aircraft_total", 0)
        )
        input_aircraft_adiz = st.number_input(
            "Daily Aircraft in ADIZ", min_value=0, step=1,
            value=st.session_state.get("input_aircraft_adiz", 0)
        )
        input_median_crossings = st.number_input(
            "Daily Median Line Crossings", min_value=0, step=1,
            value=st.session_state.get("input_median_crossings", 0)
        )
        input_plan_vessels = st.number_input(
            "Daily PLAN Vessels Detected", min_value=0, step=1,
            value=st.session_state.get("input_plan_vessels", 0)
        )

        # Save to session_state
        st.session_state["input_date"] = input_date
        st.session_state["input_aircraft_total"] = input_aircraft_total
        st.session_state["input_aircraft_adiz"] = input_aircraft_adiz
        st.session_state["input_median_crossings"] = input_median_crossings
        st.session_state["input_plan_vessels"] = input_plan_vessels

        # --- ADIZ Checkboxes ---
        st.write("ADIZ Regions Violated:")
        median_line_checked = st.checkbox("Median Line", value=st.session_state.get("median_line_checked", False))
        eastern_adiz_checked = st.checkbox("Eastern ADIZ", value=st.session_state.get("eastern_adiz_checked", False))
        northeast_adiz_checked = st.checkbox("Northeast ADIZ", value=st.session_state.get("northeast_adiz_checked", False))
        southern_adiz_checked = st.checkbox("Southern ADIZ", value=st.session_state.get("southern_adiz_checked", False))
        southwest_adiz_checked = st.checkbox("Southwest ADIZ", value=st.session_state.get("southwest_adiz_checked", False))

        # Save checkboxes
        st.session_state["median_line_checked"] = median_line_checked
        st.session_state["eastern_adiz_checked"] = eastern_adiz_checked
        st.session_state["northeast_adiz_checked"] = northeast_adiz_checked
        st.session_state["southern_adiz_checked"] = southern_adiz_checked
        st.session_state["southwest_adiz_checked"] = southwest_adiz_checked

        aircraft_categories = [
            "*Unspecified", "Fighter", "Attack", "Bomber", "AEW&C", "ASW",
            "ELINT", "EW", "RECCE", "Tanker", "Transport"
        ]
        airframes = [
            "*Unspecified", "H-6", "H-6K", "J-10", "J-11", "J-16", "J-16D", "J-7", "JH-7",
            "KA-28 ASW", "KJ-500", "MI-17 Cargo", "SU-30", "WZ-10 Attack",
            "Y-20 Aerial Refuel", "Y-8", "Y-8 ASW", "Y-8 C3", "Y-8 ELINT",
            "Y-8 EW", "Y-8 RECCE", "Y-9", "Y-9 EW", "Z-8", "Z-9 ASW",
            "Helicopter", "Support Aircraft", "UAV", "Fighter"
        ]

        # --- ADIZ Multi-entry Form ---
        def adiz_form(zone_name, checked):
            if f"{zone_name}_entries" not in st.session_state:
                st.session_state[f"{zone_name}_entries"] = []

            if not checked:
                return []

            st.write("---")  # Top divider
            st.write(f"### {zone_name} Region Inputs")

            entries = []
            for idx in range(len(st.session_state[f"{zone_name}_entries"])):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    category = st.selectbox(
                        f"{zone_name} - Aircraft Category {idx+1}",
                        aircraft_categories,
                        key=f"{zone_name}_cat_{idx}"
                    )
                with col2:
                    frame = st.selectbox(
                        f"{zone_name} - Airframe {idx+1}",
                        airframes,
                        key=f"{zone_name}_frame_{idx}"
                    )
                with col3:
                    count = st.number_input(
                        f"{zone_name} - # Aircraft {idx+1}",
                        min_value=0,
                        step=1,
                        key=f"{zone_name}_count_{idx}"
                    )
                entries.append({"Category": category, "Airframe": frame, "Count": count})

            col_add, col_delete = st.columns([1, 1])
            with col_add:
                if st.button(f"➕ Add {zone_name} Entry", key=f"add_{zone_name}"):
                    st.session_state[f"{zone_name}_entries"].append({})
                    st.rerun()
            with col_delete:
                if st.button(f"❌ Delete Last {zone_name} Entry", key=f"delete_last_{zone_name}"):
                    if st.session_state[f"{zone_name}_entries"]:
                        st.session_state[f"{zone_name}_entries"].pop()
                        st.rerun()

            return entries

        median_line_inputs = adiz_form("Median Line", median_line_checked)
        eastern_adiz_inputs = adiz_form("Eastern ADIZ", eastern_adiz_checked)
        northeast_adiz_inputs = adiz_form("Northeast ADIZ", northeast_adiz_checked)
        southern_adiz_inputs = adiz_form("Southern ADIZ", southern_adiz_checked)
        southwest_adiz_inputs = adiz_form("Southwest ADIZ", southwest_adiz_checked)

        # --- Submit Button ---
        st.write("---")
        if st.button("Submit Entry"):
            st.write("You entered:")
            st.write({
                "Date": input_date,
                "Daily Aircraft Detected": input_aircraft_total,
                "Daily Aircraft in ADIZ": input_aircraft_adiz,
                "Daily Median Line Crossings": input_median_crossings,
                "Daily PLAN Vessels Detected": input_plan_vessels,
                "Median Line": median_line_inputs,
                "Eastern ADIZ": eastern_adiz_inputs,
                "Northeast ADIZ": northeast_adiz_inputs,
                "Southern ADIZ": southern_adiz_inputs,
                "Southwest ADIZ": southwest_adiz_inputs
            })

# --- Visualise Data Section ---
elif selected_section == "Visualise Data":
    st.subheader("Visualise Your Data")
    uploaded_file = get_uploaded_file("upload_edit_file")  # Use same persistent file

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            selected_sheet = st.selectbox("Select a sheet", sheet_names, key="vis_sheet")
            df = pd.read_excel(xls, sheet_name=selected_sheet)

        cols = df.columns.tolist()
        x_axis = st.selectbox("Select X-axis", cols)
        y_axis = st.selectbox("Select Y-axis", cols)

        fig, ax = plt.subplots()
        ax.plot(df[x_axis], df[y_axis], marker="o")
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        ax.set_title(f"{y_axis} vs {x_axis}")
        st.pyplot(fig)
    else:
        st.write("Please upload a file to visualise data.")
    
    # --- Dashboard Area ---
    st.write("### Dashboard Area")

    # Make sure the DataFrame is loaded from the uploaded file
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            daily_forces_near_taiwan = pd.read_csv(uploaded_file)
        else:
            xls = pd.ExcelFile(uploaded_file)
            if "Daily forces near Taiwan" in xls.sheet_names:
                daily_forces_near_taiwan = pd.read_excel(xls, sheet_name="Daily forces near Taiwan")
            else:
                st.write("Sheet 'Daily forces near Taiwan' not found.")
                daily_forces_near_taiwan = pd.DataFrame()

        if not daily_forces_near_taiwan.empty:
            # --- Preprocess ---
            daily_forces_near_taiwan['date'] = pd.to_datetime(daily_forces_near_taiwan['Date'], errors='coerce')
            daily_forces_near_taiwan = daily_forces_near_taiwan.dropna(subset=['date'])
            daily_forces_near_taiwan['Year'] = daily_forces_near_taiwan['date'].dt.year
            daily_forces_near_taiwan['Month'] = daily_forces_near_taiwan['date'].dt.month
            daily_forces_near_taiwan['Total Aircraft Detected'] = (
                daily_forces_near_taiwan['Regional Aircraft'] + daily_forces_near_taiwan['ADIZ Aircraft']
            )

            # -------------------------------
            # 1️⃣ Cumulative Statistics (Yearly View)
            # -------------------------------
            st.subheader("Cumulative Statistics (Yearly View)")

            monthly_aircraft = daily_forces_near_taiwan.groupby(['Year', 'Month'])['Total Aircraft Detected'].sum().reset_index()
            pivot_aircraft = monthly_aircraft.pivot(index='Month', columns='Year', values='Total Aircraft Detected').fillna(0)
            pivot_aircraft = pivot_aircraft.sort_index(axis=1)
            cumulative_aircraft = pivot_aircraft.cumsum()

            fig, ax = plt.subplots(figsize=(16, 4))
            colors = {
                2020: '#FADBD8',
                2021: '#F9E79F',
                2022: '#A9CCE3',
                2023: '#7DCEA0',
                2024: '#85929E',
                2025: '#1B2631'
            }

            latest_year = cumulative_aircraft.columns.max()
            for year in cumulative_aircraft.columns:
                if year == latest_year:
                    months_to_plot = cumulative_aircraft.index[cumulative_aircraft[year] > 0]
                    values_to_plot = cumulative_aircraft.loc[months_to_plot, year]
                else:
                    months_to_plot = cumulative_aircraft.index
                    values_to_plot = cumulative_aircraft[year]

                ax.plot(months_to_plot, values_to_plot, marker='o', label=str(year), color=colors.get(year, 'gray'))
                last_month = months_to_plot[-1]
                last_value = values_to_plot.iloc[-1]
                ax.text(last_month, last_value + 0.02 * last_value, f"{int(last_value):,}",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

            ax.set_title('Daily Aircraft Detected (Cumulative Yearly View)', fontsize=16)
            ax.set_xlabel('Month')
            ax.set_ylabel('Cumulative Aircraft Detected')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            ax.grid(True)
            ax.legend(title='Year')
            st.pyplot(fig)

            # -------------------------------
            # 2️⃣ Daily Statistics (Monthly View)
            # -------------------------------
            st.subheader("Daily Statistics (Monthly View)")

            # Load 'Daily median line crossings' sheet if it exists
            if uploaded_file:
                if uploaded_file.name.endswith(".csv"):
                    daily_median_line_crossings = pd.DataFrame()  # CSV may not have this sheet
                else:
                    xls = pd.ExcelFile(uploaded_file)
                    if "Daily median line crossings" in xls.sheet_names:
                        daily_median_line_crossings = pd.read_excel(xls, sheet_name="Daily median line crossings")
                        daily_median_line_crossings['date'] = pd.to_datetime(daily_median_line_crossings['Date'], errors='coerce')
                        daily_median_line_crossings['Year'] = daily_median_line_crossings['date'].dt.year
                        daily_median_line_crossings['Month'] = daily_median_line_crossings['date'].dt.month
                    else:
                        daily_median_line_crossings = pd.DataFrame()

            # Let the user select which daily statistic to plot
            stat_options = ["Daily Aircraft Detected", "Daily Aircraft in ADIZ", "Daily Median Line Crossings"]
            selected_stat = st.selectbox("Select Daily Statistic", stat_options)

            # Prepare data for plotting
            if selected_stat == "Daily Aircraft Detected":
                df_to_plot = daily_forces_near_taiwan.groupby(['Year', 'Month'])['Total Aircraft Detected'].sum().reset_index()
                df_to_plot['YearMonth'] = pd.to_datetime(df_to_plot['Year'].astype(str) + '-' + df_to_plot['Month'].astype(str) + '-01')
                y_values = df_to_plot.groupby('YearMonth')['Total Aircraft Detected'].sum()
                y_label = "Total Aircraft Detected"

            elif selected_stat == "Daily Aircraft in ADIZ":
                df_to_plot = daily_forces_near_taiwan.groupby(['Year', 'Month'])['ADIZ Aircraft'].sum().reset_index()
                df_to_plot['YearMonth'] = pd.to_datetime(df_to_plot['Year'].astype(str) + '-' + df_to_plot['Month'].astype(str) + '-01')
                y_values = df_to_plot.groupby('YearMonth')['ADIZ Aircraft'].sum()
                y_label = "Aircraft in ADIZ"

            else:  # Daily Median Line Crossings
                if not daily_median_line_crossings.empty:
                    df_to_plot = daily_median_line_crossings.groupby(['Year', 'Month'])['Grand Total'].sum().reset_index()
                    df_to_plot['YearMonth'] = pd.to_datetime(df_to_plot['Year'].astype(str) + '-' + df_to_plot['Month'].astype(str) + '-01')
                    y_values = df_to_plot.groupby('YearMonth')['Grand Total'].sum()
                    y_label = "Median Line Crossings"
                else:
                    st.write("No data found for Daily Median Line Crossings.")
                    y_values = pd.Series(dtype=float)

            # Plot if data is available
            if not y_values.empty:
                fig, ax = plt.subplots(figsize=(12, 4))
                ax.plot(y_values.index, y_values.values, marker='o', linestyle='-', color='blue')
                ax.set_title(f"{selected_stat} (Monthly Aggregated)", fontsize=14)
                ax.set_xlabel("Month")
                ax.set_ylabel(y_label)
                ax.grid(True)
                st.pyplot(fig)

            # -------------------------------
            # 3️⃣ Patrol Statistics
            # -------------------------------
            st.subheader("Patrol Statistics")
