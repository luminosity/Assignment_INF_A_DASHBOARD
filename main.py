import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def load_and_clean_data():
    df = pd.read_csv("VIW_FNT.csv")

    # Sum weeks 1-52 for each year and drop unused columns
    df_cleaned = df.groupby(["WHOREGION", "COUNTRY_AREA_TERRITORY", "ISO_YEAR"], as_index=False)["INF_A"].sum()

    # Drop rows with year 2025 as data is incomplete yet
    df_cleaned = df_cleaned[df_cleaned.ISO_YEAR != 2025]

    # rename column headers
    df_cleaned = df_cleaned.rename(columns={"WHOREGION": "WHO Region",
                                            "COUNTRY_AREA_TERRITORY": "Country/Area/Territory",
                                            "ISO_YEAR": "Year",
                                            "INF_A": "Influenza A Cases"})

    # change WHO Region codes to names
    region_code_to_name = {
        "AFR" : "Africa",
        "AMR" : "Americas",
        "SEAR" : "South-East Asia",
        "EUR" : "Europe",
        "EMR" : "Eastern Mediterranean",
        "WPR" : "Western Pacific Region"
    }

    df_cleaned["WHO Region"] = df_cleaned["WHO Region"].map(region_code_to_name)

    return df_cleaned

st.title("Influenza A Data Dashboard")
# try to load data and show error message if failed
try:
    df = load_and_clean_data()
except:
    st.error("Failed to load data. Please check the data file and try again.")

# Create view option selection
view_option = st.selectbox("View data by:", ["WHO Region", "Country/Area/Territory", "Total"])

if view_option == "Total":
    # Group data by year and sum Influenza A Cases
    grouped_df = df.groupby("Year", as_index=False)["Influenza A Cases"].sum()
    pivot_df = grouped_df.set_index("Year").T.fillna(0).astype(int)
else:
    # Filter data based on selected options
    option_text = "WHO Region(s)" if view_option == "WHO Region" else "Country/Area/Territory"
    selected_options = st.multiselect(f"Select specific {option_text} to view:", df[view_option].unique(), default=[])

    if selected_options:
        df = df[df[view_option].isin(selected_options)]

    grouped_df = df.groupby([view_option, "Year"], as_index=False)["Influenza A Cases"].sum()
    pivot_df = grouped_df.pivot(index=view_option, columns="Year", values="Influenza A Cases").fillna(0).astype(int)

# Show data table
st.subheader("Influenza A Cases by Year")
st.dataframe(pivot_df)

# Chart with year as x-axis and Influenza A Cases as y-axis and each line represents a region
chart = alt.Chart(grouped_df).mark_area(opacity=0.3).encode(
    x='Year:O',
    y='Influenza A Cases:Q',
    color=f'{view_option}:N'
)

st.altair_chart(chart)

# Show data source
st.markdown("Data source: [WHO FluNet](https://www.who.int/tools/flunet)")

# Note
st.markdown("Note: Data might not be complete for some years in some regions/countries.")