# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('/mnt/extra-drive/Coding/IC/df_sem_pendentes.csv')
df_number = pd.read_csv('df_sem_pendentes_number.csv')

df['Nota_RAD'] = df['Nota_RAD'].str.replace(",", ".")
df['Nota_RAD'] = pd.to_numeric(df['Nota_RAD'])

averageGradePerUnit = df.groupby('UNIDADE')['Nota_RAD'].mean().reset_index()
averageGradePerUnit.rename(columns={'Nota_RAD': 'Media'}, inplace=True)

fig_cumulative = px.bar(df, x="UNIDADE", y="Nota_RAD", title="Notas por Unidade cumulativo")
fig_average = px.bar(averageGradePerUnit, x="UNIDADE", y="Media", title="Notas por unidade média")

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
       html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


app = Dash(__name__)

app.layout = html.Div([
    html.H1('Tabela IC'),

    generate_table(df, 20),
    
    dcc.Graph(
        id='grafico_cumulativo',
        figure=fig_cumulative
    ),

    dcc.Graph(
        id='grafico_media',
        figure=fig_average
    ),
    
    dcc.Dropdown(
        id='select-option',
        options=[
            {'label': 'Arcoverde', 'value': 'Arcoverde'},
            {'label': 'Caruaru', 'value': 'Caruaru'},
            {'label': 'ESEF', 'value': 'ESEF'},
            {'label': 'FCAP', 'value': 'FCAP'},
            {'label': 'FCM', 'value': 'FCM'},
            {'label': 'FENSG', 'value': 'FENSG'},
            {'label': 'FOP', 'value': 'FOP'},
            {'label': 'Garanhuns', 'value': 'Garanhuns'},
            {'label': 'ICB', 'value': 'ICB'},
            {'label': 'Mata Norte', 'value': 'Mata Norte'},
            {'label': 'Mata Sul', 'value': 'Mata Sul'},
            {'label': 'POLI', 'value': 'POLI'},
            {'label': 'Petrolina', 'value': 'Petrolina'},
            {'label': 'Reitoria', 'value': 'Reitoria'},
            {'label': 'Salgueiro', 'value': 'Salgueiro'},
            {'label': 'Serra Talhada', 'value': 'Serra Talhada'},
            ],
        value='',
        placeholder=''
    ),

    html.P("Dimensão: "),

    dcc.Checklist(
        id='dimension',
        options= ['Nota_RAD', 'Ensino', 'Pesquisa', 'Extensão', 'Gestão'],
        value=['Nota_RAD'],
        inline=True
    ),

    dcc.Graph(id='graph'),

    html.H4("Violin plot: "),

    dcc.Graph(id='graph-violin')
])

@app.callback(
    Output("graph", "figure"),    
    Input("select-option", "value"),
    Input("dimension", "value")
)

def update_output(selected_option, dimension):
    temp = df_number[df_number["UNIDADE"] == selected_option]
    fig = px.box(temp, y=dimension)
    return fig

@app.callback(
    Output("graph-violin", "figure"),    
    Input("select-option", "value"),
    Input("dimension", "value")
)

def update_output_violin(selected_option, dimension):
    temp = df_number[df_number["UNIDADE"] == selected_option]
    fig = px.violin(temp, y=dimension)
    return fig

if __name__ == '__main__':
    app.run(debug=True)
