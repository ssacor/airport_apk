"""
Airport Details Finder - Streamlit Web App
============================================
A web app that lets users search for airport details by name, IATA code,
ICAO code, city, or country, shows them on an interactive map,
and displays full details.

NOTE: This app uses ONLY Streamlit + pandas (both pre-installed on
Streamlit Cloud) - no folium, no pycountry, no extra libraries.
Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

# CSV file from OurAirports: https://davidmegginson.github.io/ourairports-data/
DATA_FILE = "data/airports.csv"

# Fields that are searchable (country_name is derived from iso_country;
# keywords holds alternate/old names, e.g. 'Katunayake' for Colombo airport)
SEARCH_COLUMNS = ["name", "iata_code", "icao_code", "municipality",
                  "iso_country", "country_name", "keywords"]

# Max airports plotted on the map (keeps the map fast & readable)
MAX_MAP_MARKERS = 500

# Built-in ISO 3166-1 alpha-2 -> country name mapping.
# This replaces the pycountry library so the app has NO external dependencies.
COUNTRY_NAMES = {
    "AD": "Andorra", "AE": "United Arab Emirates", "AF": "Afghanistan",
    "AG": "Antigua and Barbuda", "AI": "Anguilla", "AL": "Albania",
    "AM": "Armenia", "AO": "Angola", "AQ": "Antarctica", "AR": "Argentina",
    "AS": "American Samoa", "AT": "Austria", "AU": "Australia",
    "AW": "Aruba", "AX": "Åland Islands", "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina", "BB": "Barbados", "BD": "Bangladesh",
    "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria",
    "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin",
    "BL": "Saint Barthélemy", "BM": "Bermuda", "BN": "Brunei Darussalam",
    "BO": "Bolivia", "BQ": "Bonaire, Sint Eustatius and Saba",
    "BR": "Brazil", "BS": "Bahamas", "BT": "Bhutan",
    "BV": "Bouvet Island", "BW": "Botswana", "BY": "Belarus",
    "BZ": "Belize", "CA": "Canada", "CC": "Cocos (Keeling) Islands",
    "CD": "Congo (Democratic Republic)", "CF": "Central African Republic",
    "CG": "Congo", "CH": "Switzerland", "CI": "Côte d'Ivoire",
    "CK": "Cook Islands", "CL": "Chile", "CM": "Cameroon",
    "CN": "China", "CO": "Colombia", "CR": "Costa Rica",
    "CU": "Cuba", "CV": "Cape Verde", "CW": "Curaçao",
    "CX": "Christmas Island", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DJ": "Djibouti", "DK": "Denmark",
    "DM": "Dominica", "DO": "Dominican Republic", "DZ": "Algeria",
    "EC": "Ecuador", "EE": "Estonia", "EG": "Egypt",
    "EH": "Western Sahara", "ER": "Eritrea", "ES": "Spain",
    "ET": "Ethiopia", "FI": "Finland", "FJ": "Fiji",
    "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands",
    "FR": "France", "GA": "Gabon", "GB": "United Kingdom",
    "GD": "Grenada", "GE": "Georgia", "GF": "French Guiana",
    "GG": "Guernsey", "GH": "Ghana", "GI": "Gibraltar",
    "GL": "Greenland", "GM": "Gambia", "GN": "Guinea",
    "GP": "Guadeloupe", "GQ": "Equatorial Guinea", "GR": "Greece",
    "GS": "South Georgia and South Sandwich Islands", "GT": "Guatemala",
    "GU": "Guam", "GW": "Guinea-Bissau", "GY": "Guyana",
    "HK": "Hong Kong", "HM": "Heard Island and McDonald Islands",
    "HN": "Honduras", "HR": "Croatia", "HT": "Haiti",
    "HU": "Hungary", "ID": "Indonesia", "IE": "Ireland",
    "IL": "Israel", "IM": "Isle of Man", "IN": "India",
    "IO": "British Indian Ocean Territory", "IQ": "Iraq", "IR": "Iran",
    "IS": "Iceland", "IT": "Italy", "JE": "Jersey",
    "JM": "Jamaica", "JO": "Jordan", "JP": "Japan",
    "KE": "Kenya", "KG": "Kyrgyzstan", "KH": "Cambodia",
    "KI": "Kiribati", "KM": "Comoros", "KN": "Saint Kitts and Nevis",
    "KP": "North Korea", "KR": "South Korea", "KW": "Kuwait",
    "KY": "Cayman Islands", "KZ": "Kazakhstan", "LA": "Laos",
    "LB": "Lebanon", "LC": "Saint Lucia", "LI": "Liechtenstein",
    "LK": "Sri Lanka", "LR": "Liberia", "LS": "Lesotho",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "LY": "Libya", "MA": "Morocco", "MC": "Monaco",
    "MD": "Moldova", "ME": "Montenegro", "MF": "Saint Martin",
    "MG": "Madagascar", "MH": "Marshall Islands", "MK": "North Macedonia",
    "ML": "Mali", "MM": "Myanmar", "MN": "Mongolia",
    "MO": "Macao", "MP": "Northern Mariana Islands", "MQ": "Martinique",
    "MR": "Mauritania", "MS": "Montserrat", "MT": "Malta",
    "MU": "Mauritius", "MV": "Maldives", "MW": "Malawi",
    "MX": "Mexico", "MY": "Malaysia", "MZ": "Mozambique",
    "NA": "Namibia", "NC": "New Caledonia", "NE": "Niger",
    "NF": "Norfolk Island", "NG": "Nigeria", "NI": "Nicaragua",
    "NL": "Netherlands", "NO": "Norway", "NP": "Nepal",
    "NR": "Nauru", "NU": "Niue", "NZ": "New Zealand",
    "OM": "Oman", "PA": "Panama", "PE": "Peru",
    "PF": "French Polynesia", "PG": "Papua New Guinea", "PH": "Philippines",
    "PK": "Pakistan", "PL": "Poland", "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn Islands", "PR": "Puerto Rico", "PS": "Palestine",
    "PT": "Portugal", "PW": "Palau", "PY": "Paraguay",
    "QA": "Qatar", "RE": "Réunion", "RO": "Romania",
    "RS": "Serbia", "RU": "Russia", "RW": "Rwanda",
    "SA": "Saudi Arabia", "SB": "Solomon Islands", "SC": "Seychelles",
    "SD": "Sudan", "SE": "Sweden", "SG": "Singapore",
    "SH": "Saint Helena", "SI": "Slovenia", "SJ": "Svalbard and Jan Mayen",
    "SK": "Slovakia", "SL": "Sierra Leone", "SM": "San Marino",
    "SN": "Senegal", "SO": "Somalia", "SR": "Suriname",
    "SS": "South Sudan", "ST": "Sao Tome and Principe", "SV": "El Salvador",
    "SX": "Sint Maarten", "SY": "Syria", "SZ": "Eswatini",
    "TC": "Turks and Caicos Islands", "TD": "Chad",
    "TF": "French Southern Territories", "TG": "Togo", "TH": "Thailand",
    "TJ": "Tajikistan", "TK": "Tokelau", "TL": "Timor-Leste",
    "TM": "Turkmenistan", "TN": "Tunisia", "TO": "Tonga",
    "TR": "Turkey", "TT": "Trinidad and Tobago", "TV": "Tuvalu",
    "TW": "Taiwan", "TZ": "Tanzania", "UA": "Ukraine",
    "UG": "Uganda", "UM": "United States Minor Outlying Islands",
    "US": "United States", "UY": "Uruguay", "UZ": "Uzbekistan",
    "VA": "Vatican City", "VC": "Saint Vincent and the Grenadines",
    "VE": "Venezuela", "VG": "British Virgin Islands",
    "VI": "U.S. Virgin Islands", "VN": "Vietnam", "VU": "Vanuatu",
    "WF": "Wallis and Futuna", "WS": "Samoa", "YE": "Yemen",
    "YT": "Mayotte", "ZA": "South Africa", "ZM": "Zambia",
    "ZW": "Zimbabwe",
}

# Map airport type -> marker color/size on the built-in st.map
TYPE_STYLE = {
    "large_airport":   {"color": "#d9534f", "size": 20},
    "medium_airport":  {"color": "#f0ad4e", "size": 14},
    "small_airport":   {"color": "#5bc0de", "size": 8},
    "seaplane_base":   {"color": "#999999", "size": 8},
    "heliport":        {"color": "#666666", "size": 6},
}


@st.cache_data
def load_airports(file_path):
    """
    Load the airports CSV once and prepare it for fast searching:
      - everything read as string, empty cells as ""
      - coordinates converted to numbers
      - country names derived from ISO codes using the built-in COUNTRY_NAMES
        dict (so 'srilanka' finds 'LK')
      - pre-lowercased search columns + one combined search text (fast search)
    Cached: the 13 MB file is read only once, no matter how many searches.
    """
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
    df = df.fillna("")

    # Convert coordinates to numbers (invalid values become NaN -> excluded from map)
    for col in ["latitude_deg", "longitude_deg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Country code -> country name (built-in mapping, no external library)
    df["country_name"] = df["iso_country"].map(COUNTRY_NAMES).fillna(df["iso_country"])

    # Pre-lowercase all search fields once -> searches are a single fast pass
    for col in SEARCH_COLUMNS:
        df[f"_lc_{col}"] = df[col].astype(str).str.lower()

    # Also a space-stripped country name, so 'srilanka' matches 'Sri Lanka'
    df["_lc_country_nospace"] = df["_lc_country_name"].str.replace(" ", "")

    # One combined search text per airport (used for the "All fields" search)
    df["_search_all"] = (
        df["_lc_name"] + " | " +
        df["_lc_iata_code"] + " | " +
        df["_lc_icao_code"] + " | " +
        df["_lc_municipality"] + " | " +
        df["_lc_iso_country"] + " | " +
        df["_lc_country_name"] + " | " +
        df["_lc_country_nospace"] + " | " +
        df["_lc_keywords"]
    )

    return df


def search_airports(airports_df, query, field):
    """
    Find airports matching the query.

    - field: which column to search ('all', 'name', 'iata_code', 'icao_code',
             'municipality', 'iso_country', 'country_name')
    - query: search term, case-insensitive, partial match
    - Matches are OR'd across fields (a result only needs to match ONE field),
      which is what makes searching 'CMB' (IATA-only) work correctly.
    """
    query = query.strip().lower()
    if not query:
        return airports_df.iloc[0:0]  # empty result

    if field == "all":
        mask = airports_df["_search_all"].str.contains(query, regex=False)
    else:
        mask = airports_df[f"_lc_{field}"].str.contains(query, regex=False)

    result = airports_df[mask]

    # Remove duplicate entries (same airport listed under several codes)
    if "ident" in result.columns:
        result = result.drop_duplicates(subset=["ident"])

    # Sort for relevance: exact IATA match first, then exact ICAO,
    # then name starting with the query, then the rest
    if not result.empty:
        exact_iata = result["_lc_iata_code"] == query
        exact_icao = result["_lc_icao_code"] == query
        name_starts = result["_lc_name"].str.startswith(query)
        result = result.assign(
            _score=(3 * exact_iata + 2 * exact_icao + 1 * name_starts).astype(int)
        ).sort_values("_score", ascending=False).drop(columns=["_score"])

    return result.reset_index(drop=True)


def build_map_data(matches):
    """
    Prepare a DataFrame for Streamlit's built-in st.map().
    Returns (map_df, truncated) or (None, 0) if nothing can be plotted.
    st.map() is a Streamlit native feature - no external library needed.
    """
    # Only airports with valid coordinates can be plotted
    valid = matches.dropna(subset=["latitude_deg", "longitude_deg"])
    valid = valid[
        valid["latitude_deg"].between(-90, 90) &
        valid["longitude_deg"].between(-180, 180)
    ]
    if valid.empty:
        return None, 0

    plotted = valid.head(MAX_MAP_MARKERS)
    truncated = len(valid) - len(plotted)

    # st.map expects columns named exactly: latitude, longitude
    map_df = pd.DataFrame({
        "latitude": plotted["latitude_deg"],
        "longitude": plotted["longitude_deg"],
        # Style markers by airport type (color + size)
        "color": plotted["type"].map(TYPE_STYLE).map(
            lambda s: s["color"] if isinstance(s, dict) else None
        ).fillna("#888888"),
        "size": plotted["type"].map(TYPE_STYLE).map(
            lambda s: s["size"] if isinstance(s, dict) else 8
        ).fillna(8),
    })

    return map_df, truncated


def main():
    st.set_page_config(page_title="Airport Details Finder", page_icon="✈️", layout="centered")

    st.title("✈️ Airport Details Finder")
    st.markdown(
        "Search **over 86,000 airports** worldwide by name, IATA code, ICAO code, "
        "city, or country — see them on an **interactive map** and view full details."
    )
    st.divider()

    # --- Sidebar: search controls ---
    st.sidebar.header("Search Settings")
    query = st.sidebar.text_input(
        "Search term",
        placeholder="e.g. CMB, Colombo, Sri Lanka, Katunayake...",
        help="Case-insensitive. Partial matches work too.",
    )
    field = st.sidebar.selectbox(
        "Search by",
        options=["all", "name", "iata_code", "icao_code", "municipality",
                 "iso_country", "country_name"],
        format_func=lambda x: {
            "all": "All fields",
            "name": "Airport name",
            "iata_code": "IATA code",
            "icao_code": "ICAO code",
            "municipality": "City",
            "iso_country": "Country code (e.g. LK)",
            "country_name": "Country name (e.g. Sri Lanka)",
        }[x],
        index=0,
    )

    # --- Load data (with friendly error if the CSV is missing) ---
    try:
        airports_df = load_airports(DATA_FILE)
    except FileNotFoundError:
        st.error(
            f"❌ `{DATA_FILE}` not found!\n\n"
            "Download it from **OurAirports** and place it next to this file:\n"
            "https://davidmegginson.github.io/ourairports-data/"
        )
        st.stop()

    st.caption(f"📊 Dataset loaded: **{len(airports_df):,} airports**")

    # --- Search & results ---
    if st.sidebar.button("🔍 Search", type="primary") or query:
        matches = search_airports(airports_df, query, field)

        if matches.empty:
            st.warning(f"No airports found matching **'{query}'**. Try a different search term.")
        else:
            st.success(f"Found **{len(matches)}** airport(s) matching **'{query}'**")

            # 1. Interactive map (Streamlit built-in st.map - no extra libraries)
            st.subheader("🗺️ Airports on Map")
            map_df, truncated = build_map_data(matches)
            if map_df is None:
                st.info("No plotable locations (missing coordinates) for these results.")
            else:
                st.map(map_df)
                if truncated > 0:
                    st.caption(
                        f"ℹ️ Showing the first {MAX_MAP_MARKERS} airports on the map "
                        f"({truncated} more in the table below)."
                    )

            # 2. Detailed view: one expandable card per airport
            st.subheader("📋 Airport Details")
            for _, ap in matches.iterrows():
                with st.expander(f"{ap.get('name', 'Unknown airport')} "
                                 f"({ap.get('iata_code', 'N/A')})"):
                    col1, col2 = st.columns(2)
                    col1.markdown(f"**IATA Code:** `{ap.get('iata_code', 'N/A')}`")
                    col1.markdown(f"**ICAO Code:** `{ap.get('icao_code', 'N/A')}`")
                    col2.markdown(f"**City:** {ap.get('municipality', 'N/A')}")
                    col2.markdown(f"**Country:** {ap.get('country_name', ap.get('iso_country', 'N/A'))}")
                    col1.markdown(f"**Latitude:** {ap.get('latitude_deg', 'N/A')}")
                    col1.markdown(f"**Longitude:** {ap.get('longitude_deg', 'N/A')}")
                    col2.markdown(f"**Altitude:** {ap.get('elevation_ft', 'N/A')} ft")
                    col2.markdown(f"**Timezone:** {ap.get('tz', 'N/A')}")
                    st.markdown(f"**Type:** {ap.get('type', 'N/A')}")

            # 3. Full results table
            st.subheader("📊 All Results")
            show_cols = ["name", "iata_code", "icao_code", "municipality",
                         "country_name", "latitude_deg", "longitude_deg", "tz"]
            show_cols = [c for c in show_cols if c in matches.columns]
            st.dataframe(matches[show_cols].rename(columns={
                "name": "Airport", "iata_code": "IATA", "icao_code": "ICAO",
                "municipality": "City", "country_name": "Country",
                "latitude_deg": "Latitude", "longitude_deg": "Longitude", "tz": "Timezone"
            }), width="stretch")

    else:
        st.info("👆 Enter a search term in the sidebar and click **Search** to find airports.")
        # Show a small sample so the app isn't empty on first load
        st.markdown("### 👋 Preview of the dataset")
        sample = airports_df.head(5)[
            ["name", "iata_code", "icao_code", "municipality", "country_name"]
        ].rename(columns={
            "name": "Airport", "iata_code": "IATA", "icao_code": "ICAO",
            "municipality": "City", "country_name": "Country"
        })
        st.dataframe(sample, width="stretch")


if __name__ == "__main__":
    main()
