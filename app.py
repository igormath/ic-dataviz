# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('df_sem_pendentes_number.csv')
df_avg_rad = pd.read_csv('average_RAD_per_unit.csv')


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
server = app.server
app._favicon = "favicon.ico"
app.title = "RAD - Universidade de Pernambuco"

fig = px.strip(df, x='UNIDADE', y='Nota_RAD', color='CARGO', orientation='v', 
               stripmode='overlay', title='Gráfico Strip por unidade')

fig.update_layout(
    xaxis_title='Unidade',
    yaxis_title='Nota RAD'
)

app.layout = html.Main([
    html.H1('Protótipo RAD', className="page-title"),
    
    html.P('Box plot das quatro dimensões do Relatório de Atividades Docentes da Universidade de Pernambuco, agrupados por unidade de ensino.', className="page-paragraph"),

    dcc.Checklist(
        id='only-one', 
        options=[{
                'label': 'Selecionar todos', 
                'value': 'Option'
                }],
        value=['Option'],
        inline=True,
        className='page-checklist'
    ),

    dcc.Checklist(
        id='unity-grouped',
        options= ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns', 'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada'],
        value=[],
        inline=True,
        className="page-checklist"
    ),

    dcc.Graph(id='grouped-boxplot'),

    dcc.Checklist(
        id='unity-nongrouped',
        options= ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns', 'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada'],
        value=[],
        inline=True,
        className="page-checklist"
    ),

    dcc.Graph(id='boxplot-rad'),

    html.Div([
    dcc.Graph(
        id='strip-chart',
        figure=fig
    )
])
])

@app.callback(
    Output("grouped-boxplot", "figure"),
    Input("unity-grouped", "value")
)

def update_output_boxplot(unity):
    filtered_df = df[df['UNIDADE'].isin(unity)]

    
    data = [
        go.Box(
            y=filtered_df['Ensino'],
            x=filtered_df['UNIDADE'],
            name='Ensino',
            marker_color='#F79646'
        ),
        go.Box(
            y=filtered_df['Pesquisa'],
            x=filtered_df['UNIDADE'],
            name='Pesquisa',
            marker_color='#92D050'
        ),
        go.Box(
            y=filtered_df['Extensão'],
            x=filtered_df['UNIDADE'],
            name='Extensão',
            marker_color='#4BACC6'
        ),
        go.Box(
            y=filtered_df['Gestão'],
            x=filtered_df['UNIDADE'],
            name='Gestão',
            marker_color='#B65708'
        )
    ]
    
    layout = go.Layout(
        title='Relatório de Atividades Docentes 2023 - Notas por unidade (separadas por dimensão)',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota'),
        boxmode='group'
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(
    [Output('unity-grouped', 'value'),
     Output('unity-nongrouped', 'value')],
    [Input('only-one', 'value')]
)

def update_checklists(value):
    if value:
        return ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns',
                'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada'], \
               ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns',
                'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada']
    else:
        return [], []

@app.callback(
    Output("boxplot-rad", "figure"),
    Input("unity-nongrouped", "value")
)

def update_output_boxplot(unity):
    filtered_df = df[df['UNIDADE'].isin(unity)]
    filtered_df = filtered_df.sort_values(by='UNIDADE')
    filtered_df_avg_rad = df_avg_rad[df_avg_rad['UNIDADE'].isin(unity)]
    filtered_df_avg_rad = filtered_df_avg_rad.sort_values(by='UNIDADE')
    
    data = []
    
    data.append(go.Box(
        y=filtered_df['Nota_RAD'],
        x=filtered_df['UNIDADE'],
        name='Nota RAD',
        marker_color='#A63A50',
        boxmean=True
    )
    )

    data.append(go.Scatter(
        x=filtered_df_avg_rad['UNIDADE'],
        y=filtered_df_avg_rad['Media_Nota_RAD'],
        mode='lines',
        name='Nota RAD média',
        line=dict(color='black')
    ))
    
    layout = go.Layout(
        title='Relatório de Atividades Docentes 2023 - Notas por unidade (geral)',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota RAD Geral'),
        boxmode='group'
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

if __name__ == '__main__':
    app.run(debug=True)
