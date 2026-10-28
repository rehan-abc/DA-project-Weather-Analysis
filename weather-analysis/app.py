"""Weather Data Analysis Dashboard.

A beginner-friendly Streamlit web application that analyzes weather data
from a CSV file and displays key summary metrics and visualizations.
"""

from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Required columns for the weather dataset
REQUIRED_COLUMNS = ["Date", "Temperature", "Humidity", "Rainfall"]

# Path to the bundled default sample dataset
DEFAULT_DATA_PATH = Path(__file__).parent / "weather.csv"


def load_data(file_source):
    """Load and validate weather data from a CSV file path or file uploader.

    Parameters:
        file_source: A file path (str/Path) or a Streamlit UploadedFile object.

    Returns:
        tuple: (pandas.DataFrame or None, str or None)
               Returns (df, None) if successful, or (None, error_message) if validation fails.
    """
    try:
        df = pd.read_csv(file_source)
    except Exception as exc:
        return None, f"Could not read the CSV file. Details: {exc}"

    if df.empty:
        return None, "The uploaded CSV file is empty. Please provide a dataset with data rows."

    # Validate required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        missing_str = ", ".join(f"'{col}'" for col in missing_columns)
        expected_str = ", ".join(f"'{col}'" for col in REQUIRED_COLUMNS)
        return None, (
            f"Missing required column(s): {missing_str}. "
            f"The CSV file must contain exactly these columns: {expected_str}."
        )

    # Parse and validate dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isna().all():
        return None, "All values in the 'Date' column are invalid or could not be parsed as dates."

    # Parse and validate numeric columns
    numeric_columns = ["Temperature", "Humidity", "Rainfall"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().all():
            return None, f"All values in the '{col}' column are non-numeric or invalid."

    # Remove rows where essential values are missing
    initial_rows = len(df)
    df = df.dropna(subset=["Date"] + numeric_columns)
    if df.empty:
        return None, "No valid rows remaining after removing missing/invalid data entries."

    if len(df) < initial_rows:
        dropped = initial_rows - len(df)
        st.warning(f"Note: {dropped} row(s) with invalid or missing values were excluded from the analysis.")

    # Sort sequentially by date
    df = df.sort_values(by="Date").reset_index(drop=True)

    return df, None


def calculate_statistics(df: pd.DataFrame) -> dict:
    """Calculate key summary weather statistics.

    Parameters:
        df: Validated weather pandas DataFrame.

    Returns:
        dict: Summary statistics including temperatures, humidity, and rainfall.
    """
    return {
        "avg_temp": df["Temperature"].mean(),
        "max_temp": df["Temperature"].max(),
        "min_temp": df["Temperature"].min(),
        "avg_humidity": df["Humidity"].mean(),
        "total_rainfall": df["Rainfall"].sum(),
    }


def plot_temperature_trend(df: pd.DataFrame) -> plt.Figure:
    """Create a line chart showing temperature changes over time."""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    ax.plot(
        df["Date"],
        df["Temperature"],
        marker="o",
        markersize=4,
        color="#e74c3c",
        linewidth=2,
        label="Temperature (°C)",
    )

    # Highlight mean line
    mean_temp = df["Temperature"].mean()
    ax.axhline(
        mean_temp,
        color="#c0392b",
        linestyle="--",
        linewidth=1.2,
        alpha=0.7,
        label=f"Average ({mean_temp:.1f} °C)",
    )

    ax.set_title("Temperature Trend Over Time", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, labelpad=8)
    ax.set_ylabel("Temperature (°C)", fontsize=11, labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()
    return fig


def plot_rainfall_trend(df: pd.DataFrame) -> plt.Figure:
    """Create a bar chart showing daily rainfall over time."""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    ax.bar(
        df["Date"],
        df["Rainfall"],
        color="#3498db",
        width=0.7,
        edgecolor="#2980b9",
        linewidth=0.8,
        label="Daily Rainfall (mm)",
    )

    ax.set_title("Daily Rainfall", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, labelpad=8)
    ax.set_ylabel("Rainfall (mm)", fontsize=11, labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()
    return fig


def plot_humidity_trend(df: pd.DataFrame) -> plt.Figure:
    """Create a line chart showing humidity changes over time."""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    ax.plot(
        df["Date"],
        df["Humidity"],
        marker="s",
        markersize=4,
        color="#2ecc71",
        linewidth=2,
        label="Humidity (%)",
    )

    # Highlight mean line
    mean_hum = df["Humidity"].mean()
    ax.axhline(
        mean_hum,
        color="#27ae60",
        linestyle="--",
        linewidth=1.2,
        alpha=0.7,
        label=f"Average ({mean_hum:.1f} %)",
    )

    ax.set_title("Humidity Level Over Time", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, labelpad=8)
    ax.set_ylabel("Relative Humidity (%)", fontsize=11, labelpad=8)
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper right", framealpha=0.9)
    plt.tight_layout()
    return fig


def main():
    """Main function to render the Streamlit Weather Analysis application."""
    st.set_page_config(
        page_title="Weather Data Analysis",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header section
    st.title("🌤️ Weather Data Analysis")
    st.markdown(
        "Analyze daily weather data from CSV files with interactive statistics, "
        "summary metric cards, and charts."
    )

    # Sidebar: Data input configuration
    st.sidebar.header("📁 Data Source")
    st.sidebar.markdown(
        "Upload your own weather CSV file or use the built-in sample dataset."
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=["csv"],
        help="Upload a CSV file containing columns: Date, Temperature, Humidity, Rainfall",
    )

    # Determine whether using uploaded file or sample dataset
    if uploaded_file is not None:
        source_label = f"Uploaded file: `{uploaded_file.name}`"
        df, error = load_data(uploaded_file)
        is_sample = False
    else:
        source_label = "Built-in Sample Dataset (`weather.csv`)"
        if not DEFAULT_DATA_PATH.exists():
            st.error(
                f"Sample data file not found at expected location: `{DEFAULT_DATA_PATH}`. "
                "Please upload a CSV file or check your project directory."
            )
            return
        df, error = load_data(DEFAULT_DATA_PATH)
        is_sample = True

    # Handle errors if data failed validation
    if error is not None:
        st.error(f"⚠️ **Data Error:** {error}")
        st.info(
            "**Expected CSV Format:**\n\n"
            "- Column 1: `Date` (e.g. YYYY-MM-DD)\n"
            "- Column 2: `Temperature` (numeric in °C)\n"
            "- Column 3: `Humidity` (numeric in %)\n"
            "- Column 4: `Rainfall` (numeric in mm)"
        )
        return

    # Data Source notification banner
    if is_sample:
        st.info(
            f"ℹ️ Currently viewing: **{source_label}**. "
            "*(This contains synthetic sample data for demonstration, not actual recorded weather observations.)*"
        )
    else:
        st.success(f"✅ Successfully loaded: **{source_label}** ({len(df)} records)")

    # -------------------------------------------------------------
    # 1. Statistics Cards (At the Top)
    # -------------------------------------------------------------
    stats = calculate_statistics(df)

    st.subheader("📊 Key Weather Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Avg Temperature",
            value=f"{stats['avg_temp']:.1f} °C",
        )
    with col2:
        st.metric(
            label="Max Temperature",
            value=f"{stats['max_temp']:.1f} °C",
        )
    with col3:
        st.metric(
            label="Min Temperature",
            value=f"{stats['min_temp']:.1f} °C",
        )
    with col4:
        st.metric(
            label="Avg Humidity",
            value=f"{stats['avg_humidity']:.1f} %",
        )
    with col5:
        st.metric(
            label="Total Rainfall",
            value=f"{stats['total_rainfall']:.1f} mm",
        )

    st.markdown("---")

    # -------------------------------------------------------------
    # 2. Visualizations
    # -------------------------------------------------------------
    st.subheader("📈 Visualizations")

    # Chart 1: Temperature changes over time
    st.markdown("#### 🌡️ Temperature Over Time")
    fig_temp = plot_temperature_trend(df)
    st.pyplot(fig_temp)
    plt.close(fig_temp)

    # Charts 2 & 3: Rainfall and Humidity side by side on desktop
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 🌧️ Daily Rainfall")
        fig_rain = plot_rainfall_trend(df)
        st.pyplot(fig_rain)
        plt.close(fig_rain)

    with chart_col2:
        st.markdown("#### 💧 Humidity Over Time")
        fig_hum = plot_humidity_trend(df)
        st.pyplot(fig_hum)
        plt.close(fig_hum)

    st.markdown("---")

    # -------------------------------------------------------------
    # 3. Data Table Exploration
    # -------------------------------------------------------------
    st.subheader("📋 Dataset Explorer")

    display_df = df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_df.style.format({
            "Temperature": "{:.1f} °C",
            "Humidity": "{:.1f} %",
            "Rainfall": "{:.1f} mm",
        }),
        use_container_width=True,
    )

    # Optional download button for the current dataset
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Current Data as CSV",
        data=csv_bytes,
        file_name="weather_export.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
