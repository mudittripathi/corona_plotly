import pandas as pd
# import matplotlib.pyplot as pl
# import csv
import plotly.graph_objects as g
import plotly.express as pe
import pickle

cases = 'https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
deaths = 'https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
# recovered = 'https://raw.github.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'


RENAMED_COLUMNS = {
    'Province/State': 'province_state',
    'Country/Region': 'country',
    'Lat': 'lat',
    'Long': 'long',
}

""" function to read the values from the urls """


def df_from_csv(file_name):
    """ Perform ETL on a Johns Hopkins COVID-19 CSV file, Returning a dataframe """
    df = pd.read_csv(file_name)
    df = df.rename(columns=RENAMED_COLUMNS)
    date_cols = df.filter(regex='^\d+/\d+/\d+$').columns
    df = pd.melt(df, id_vars=['province_state', 'country', 'lat', 'long'], value_vars=date_cols, var_name='date',
                 value_name='cases')
    # df.to_csv('output.csv', index=False)
    # df.date = pd.to_datetime(df.date, format='%m/%d/%y')
    # df['day'] = (df.date - pd.to_datetime(df.date.iloc[0])).astype('timedelta64[D]')
    # df.day = df.day.apply(lambda day: int(round(day)))
    # print(df[['date', 'cases', 'province_state', 'country', 'lat', 'long']])
    return df[['date', 'cases', 'province_state', 'country', 'lat', 'long']]


""" df_cases is the main dataframe which has all the values """
df_cases = df_from_csv(cases)
df_deaths = df_from_csv(deaths)
df_cases['deaths'] = df_deaths['cases']
# df_final = df_cases.append(df_deaths['cases'])
df_cases.to_csv('output.csv', index=False)
# print(df_final)


''' reading the data from output.csv '''
data = pd.read_csv('output.csv', parse_dates=['date'])
# print(data.head())


''' recent data '''
recent_data = data[data['date'] == data['date'].max()]
# print(recent_data)

''' max death'''
max_death = data[data['deaths'] == data['deaths'].max()].reset_index(drop=True).drop(['lat', 'long'], axis=1)
# print(max_death)


''' total cases and deaths group by counties'''
affected_countries = recent_data.groupby('country').sum().reset_index()
final = affected_countries.drop(['lat', 'long'], axis=1)
# print(final)


''' with the help of plotly we are showing max cases of each country and provinces '''
figure = g.Figure(data=g.Choropleth(
    locations=affected_countries['country'],
    locationmode='country names',
    z=affected_countries['cases'],
    colorscale='reds',
    autocolorscale=True,
    reversescale=False,
    marker_line_color='black',
    marker_line_width=0.5,
    colorbar_title='Confirmed Cases',
))

figure.update_layout(
    title_text='Countries affected by Coronavirus (COVID-19)',
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular'

    ),
    annotations=[dict(
        x=0.50,
        y=0.2,
    )]
)

figure.show()

''' '''
data_spreading = data.groupby(['date', 'country', 'deaths']).max().drop(['lat', 'long'], axis=1).reset_index()
data_spreading['count'] = data_spreading['cases'].pow(0.1)
data_spreading['date'] = pd.to_datetime(data_spreading['date']).dt.strftime('%m/%d/%Y')

figure_world = pe.scatter_geo(data_spreading,
                              locations=data_spreading['country'],
                              locationmode='country names',
                              color='cases',
                              hover_name="country",
                              size='count',
                              animation_frame="date",
                              projection="natural earth",
                              title='Spreading of Coronavirus disease (COVID-19) date wise')

figure_world.show()


