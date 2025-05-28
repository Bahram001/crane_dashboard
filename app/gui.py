import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ---- Setup ----
st.set_page_config(page_title="Crane Listings Dashboard", layout="wide")
st.title("📊 Crane Listings Dashboard")

# ---- Load CSVs from Output Folder ----
@st.cache_data
def load_data(file_path):
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            st.error("Unsupported file format")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

def get_all_csvs(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# ---- File selection ----
output_folder = os.path.join(os.path.dirname(__file__), "..", "output")
csv_files = get_all_csvs(output_folder)

selected_file = st.selectbox("📂 Choose a dataset:", csv_files)

if selected_file:
    df = load_data(os.path.join(output_folder, selected_file))
    if df.empty:
        st.warning("Selected file is empty or could not be loaded.")
        st.stop()

    st.markdown(f"### 📄 Loaded `{selected_file}` - {len(df)} entries")
    
    # Convert all columns to lowercase
    df.columns = [col.lower() for col in df.columns]
    available_columns = df.columns.tolist()


    # ---- Standardize 'price' column ----
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce")

    # ---- Sidebar Filters ----
    st.sidebar.header("🔎 Filter Listings")
    filtered_df = df.copy()

    # Filter by Title
    if "title" in available_columns:
        search_term = st.sidebar.text_input("Search in Title", "")
        if search_term:
            filtered_df = filtered_df[filtered_df["title"].str.contains(search_term, case=False, na=False)]

    # Filter by Location
    if "location" in available_columns:
        location_filter = st.sidebar.text_input("Location Contains", "")
        if location_filter:
            filtered_df = filtered_df[filtered_df["location"].str.contains(location_filter, case=False, na=False)]

    # Filter by Condition
    if "condition" in available_columns:
        condition_options = ["All"] + sorted(df["condition"].dropna().unique())
        condition_filter = st.sidebar.selectbox("Condition", condition_options)
        if condition_filter != "All":
            filtered_df = filtered_df[filtered_df["condition"] == condition_filter]

    # Filter by Crane Type
    crane_types = ["All"] + sorted(df["crane type"].dropna().unique())
    crane_type_filter = st.sidebar.selectbox("Crane Type", crane_types)
    if crane_type_filter != "All":
        filtered_df = filtered_df[filtered_df["crane type"] == crane_type_filter]

    # Filter by Price Range
    if "price" in filtered_df.columns and not filtered_df["price"].dropna().empty:
        min_price = int(filtered_df["price"].min())
        max_price = int(filtered_df["price"].max())
        price_range = st.sidebar.slider("Price Range", min_value=min_price, max_value=max_price,
                                        value=(min_price, max_price), step=1000)
        filtered_df = filtered_df[(filtered_df["price"] >= price_range[0]) & (filtered_df["price"] <= price_range[1])]

    # ---- Filtered Data Display ----
    st.markdown("---")
    st.markdown("### 📊 Filtered Results")
    st.markdown(f"Showing **{len(filtered_df)}** crane listings that match your filters.")
    st.dataframe(filtered_df, use_container_width=True)

    # ---- Export Buttons ----
    st.markdown("### 📤 Export Options")

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Listings')
        processed_data = output.getvalue()
        return processed_data

    st.download_button(
        label="📁 Export to CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_cranes.csv",
        mime="text/csv"
    )

    st.download_button(
        label="📤 Export to Excel (.xlsx)",
        data=to_excel(filtered_df),
        file_name="filtered_cranes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    with st.expander("📂 Show Full Raw Dataset"):
        st.dataframe(df, use_container_width=True)
