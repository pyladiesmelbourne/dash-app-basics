import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from textwrap import dedent

# Gapminder dataset GAPMINDER.ORG, CC-BY LICENSE
url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv"
df = pd.read_csv(url)
df = df.rename(index=str, columns={"pop": "population",
                                   "lifeExp": "life_expectancy",
                                   "gdpPercap": "GDP_per_capita"})

# Utility functions
def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

# Dash app
app = dash.Dash()
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

app.layout = html.Div([
    html.H1('Dash App Basics',
    ),

    dcc.Markdown(dedent('''
    ## What is dash?
    [Dash](https://dash.plot.ly/)
    is a python framework for building simple web apps.

    It combines:

    * [Plotly](https://plot.ly/) for interactive graphs
    * [Flask](http://flask.pocoo.org/) for the web framework
    * [React](https://reactjs.org/) for the javascript user interface

    Here's a bare bones look at an example Python Dash app.
    ''')
    ),

    html.H2("The Gapminder dataset"),
    dcc.Markdown(dedent('''
    The dataset used here is based on free material from
    [GAPMINDER.ORG](https://www.gapminder.org/data/), CC-BY LICENSE.

    Let's take a look at the dataset...
    ''')
    ),
    dcc.Markdown(dedent('''
    ```
    import pandas as pd
    url = "https://raw.githubusercontent.com/plotly/datasets/master/" +
          "gapminderDataFiveYear.csv"
    df = pd.read_csv(url)
    df = df.rename(index=str, columns={"pop": "population",
                                       "lifeExp": "life_expectancy",
                                       "gdpPercap": "GDP_per_capita"})
    df.sample(5)
    ```
    ''')
    ),
    generate_table(df.sample(5)),

    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': i, 'value': i} for i in df.country.unique()],
        multi=True,
        value=['Australia']
    ),
    dcc.Graph(id='timeseries-graph'),

    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=df['year'].min(),
        step=None,
        marks={str(year): str(year) for year in df['year'].unique()}
    )

])

@app.callback(
    dash.dependencies.Output('timeseries-graph', 'figure'),
    [dash.dependencies.Input('country-dropdown', 'value')])
def update_graph(country_values):
    dff = df.loc[df['country'].isin(country_values)]

    return {
        'data': [go.Scatter(
            x=dff[dff['country'] == country]['year'],
            y=dff[dff['country'] == country]['GDP_per_capita'],
            text="Continent: " +
                  f"{dff[dff['country'] == country]['continent'].unique()[0]}",
            mode='lines+markers',
            name=country,
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ) for country in dff.country.unique()],
        'layout': go.Layout(
            title="GDP over time, by country",
            xaxis={'title': 'Year'},
            yaxis={'title': 'GDP Per Capita'},
            margin={'l': 60, 'b': 50, 't': 80, 'r': 0},
            hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_df = df[df.year == selected_year]
    traces = []
    for i in filtered_df.continent.unique():
        df_by_continent = filtered_df[filtered_df['continent'] == i]
        traces.append(go.Scatter(
            x=df_by_continent['GDP_per_capita'],
            y=df_by_continent['life_expectancy'],
            text=df_by_continent['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title="Correlation between GDP and life expectancy",
            xaxis={'type': 'log', 'title': 'GDP Per Capita'},
            yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
            margin={'l': 40, 'b': 40, 't': 150, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
