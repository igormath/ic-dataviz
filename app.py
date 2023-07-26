# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

df = pd.read_csv('/mnt/extra-drive/Coding/IC/df_sem_pendentes.csv')

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
    )
])

if __name__ == '__main__':
    app.run(debug=True)
