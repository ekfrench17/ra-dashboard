import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='RA dashboard',
    page_icon=':house:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

@st.cache_data
def get_ra_data():
    """Grab RA data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/all_nbly_Jan2025.csv'
    raw_ra_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - ApplicantInfo_CountyResidence
    # - Date
    # - Amount
    #
    # So let's pivot all those year-columns into two: Year and GDP
    ra_df = raw_ra_df[['Case Id','ApplicantInfo_CountyResidence','Date','Amount']]

    # Convert date from string to datetime
    ra_df['Date'] = pd.to_datetime(ra_df['Date'])

    return ra_df

ra_df = get_ra_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :house: RA dashboard

Browse data
'''

# Add some spacing
''
''

min_value = ra_df['Date'].min()
max_value = ra_df['Date'].max()

from_date, to_date = st.slider(
    'Which dates are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

county_col = 'ApplicantInfo_CountyResidence'
counties = ra_df[county_col].unique()

if not len(counties):
    st.warning("Select at least one county")

selected_counties = st.multiselect(
    'Which counties would you like to view?',
    counties,
    counties.tolist())

''
''
''

# Filter the data
filtered_ra_df = ra_df[
    (ra_df[county_col].isin(selected_counties))
    & (ra_df['Date'] <= to_date)
    & (from_date <= ra_df['Date'])
]

st.header('RA over time', divider='gray')

''

st.line_chart(
    filtered_ra_df,
    x='Date',
    y='RA',
    color='County',
)

''
''


first_year = ra_df[ra_df['Date'] == from_date]
last_year = ra_df[ra_df['Date'] == to_date]

st.header(f'RA in {to_date}', divider='gray')

''

cols = st.columns(4)

for i, county in enumerate(selected_counties):
    col = cols[i % len(cols)]

    with col:
        first_ra = first_year[first_year[county_col] == county]['Amount'].iat[0]
        last_ra = last_year[last_year[county_col] == county]['Amount'].iat[0]

        if math.isnan(first_ra):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_ra / first_ra:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{county} RA',
            value=f'{last_ra:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
