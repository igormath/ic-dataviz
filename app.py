# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('df_sem_pendentes_number.csv')
time_series = pd.read_csv('serie_nota_RAD_row_2017-2022.csv')

averageGradePerUnit = df.groupby('UNIDADE')['Nota_RAD'].mean().reset_index()
averageGradePerUnit.rename(columns={'Nota_RAD': 'Media'}, inplace=True)

fig_cumulative = px.bar(df, x="UNIDADE", y="Nota_RAD", title="Notas por Unidade cumulativo")
fig_average = px.bar(averageGradePerUnit, x="UNIDADE", y="Media", title="Notas por unidade média")

app = Dash(__name__)
server = app.server
app._favicon = "favicon.ico"
app.title = "RAD - Universidade de Pernambuco"

fig = px.strip(
               df, 
               x='UNIDADE', 
               y='Nota_RAD', 
               color='CARGO', 
               orientation='v', 
               stripmode='overlay', 
               title='Gráfico beeswarm por unidade'
            )

fig.update_layout(
    xaxis_title='Unidade',
    yaxis_title='Nota RAD'
)

average_rad_general = time_series.groupby('Ano')['Nota_RAD'].mean().reset_index()

figTimeSeries = go.Figure()
figTimeSeries.add_trace(go.Scatter(x=['2017', '2018', '2019', '2020', '2021', '2022'],
                        y=average_rad_general['Nota_RAD'],
                        mode='lines+markers',
                        name='Média de Nota',
                        ))

figTimeSeries.update_layout(
    title='Nota RAD média por ano - Universidade de Pernambuco',
    xaxis_title='Ano',
    yaxis_title='Nota RAD',
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
        id='unity',
        options= ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns', 'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada'],
        value=[],
        inline=True,
        className="page-checklist"
    ),

    dcc.Graph(id='grouped-boxplot'),

    dcc.Graph(
        id='time-series-chart',
        figure=figTimeSeries
    ),

    dcc.RadioItems(
        options=sorted(time_series['Unidade'].unique()),
        value='', 
        inline=True,
        id='unity_timeseries',
    ),

    dcc.Graph(
        id='unit-rad-timeseries',
    ),

    dcc.RadioItems(
        options=sorted(time_series['Ano'].unique()),
        value='', 
        inline=True,
        id='year_timeseries',
    ),

    dcc.Graph(id='boxplot_rad_timeseries'),

    dcc.Graph(
        id='strip_chart_timeseries',
        figure=fig
    ),

    dcc.RadioItems(
        options=sorted(time_series['Unidade'].unique()),
        value='', 
        inline=True,
        id='unity_timeseries_boxplot',
    ),

    dcc.Graph(id='boxplot_rad_timeseries_unity'),
])

@app.callback(
    Output("grouped-boxplot", "figure"),
    Input("unity", "value")
)

def update_output_grouped_boxplot(unity):
    filtered_df = df[df['UNIDADE'].isin(unity)]
    filtered_df = filtered_df.sort_values(by='UNIDADE')
    
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
        boxmode='group',
        plot_bgcolor='#FFFFFF'
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(
    Output('unity', 'value'),
    Input('only-one', 'value')
)

def update_checklists(value):
    if value:
        return ['Arcoverde', 'Caruaru', 'ESEF', 'FCAP', 'FCM', 'FENSG', 'FOP', 'Garanhuns',
                'ICB', 'Mata Norte', 'Mata Sul', 'POLI', 'Petrolina', 'Reitoria', 'Salgueiro', 'Serra Talhada']
    else:
        return []

@app.callback(
    Output("unit-rad-timeseries", "figure"),
    Input("unity_timeseries", "value")
)

def update_output_strip(unity_timeseries):
    filtered_timeseries = time_series.loc[time_series['Unidade'] == unity_timeseries]
    average_rad_unity = filtered_timeseries.groupby('Ano')['Nota_RAD'].mean().reset_index()

    fig_unity_timeseries = go.Figure()
    
    fig_unity_timeseries.add_trace(go.Scatter(x=filtered_timeseries['Ano'].unique(),
                        y=average_rad_unity['Nota_RAD'],
                        mode='lines+markers',
                        name='Média de Nota',
                        ))

    fig_unity_timeseries.update_layout(
        title='Nota RAD média por ano - Unidade %s' % (unity_timeseries),
        xaxis_title='Ano',
        yaxis_title='Nota RAD',
        xaxis_tickformat=',d',
        xaxis=dict(
            tickmode='array',
            tickvals=average_rad_unity['Ano'].unique(),  # Define os valores dos ticks do eixo X
            ticktext=[str(int(ano)) for ano in average_rad_unity['Ano'].unique()]  # Converte os valores dos ticks para string

        )
    )
    return fig_unity_timeseries

@app.callback(
    Output("boxplot_rad_timeseries", "figure"),
    Input("year_timeseries", "value")
)

def update_output_boxplot(year_timeseries):

    filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]
    df_average = filtered_timeseries.groupby('Unidade')['Nota_RAD'].mean().reset_index()
    df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()


    data = []
    
    data.append(go.Box(
        x=filtered_timeseries['Unidade'],
        y=filtered_timeseries['Nota_RAD'],
        name='Nota RAD',
        marker_color='#A63A50',
        boxmean=True
    )
    )

    data.append(go.Scatter(
        x=df_average['Unidade'],
        y=df_average['Nota_RAD'],
        mode='lines',
        name='Nota RAD média',
        line=dict(color='black')
    ))
    
    layout = go.Layout(
        title='Relatório de Atividades Docentes 2023 - Notas por unidade (Nota geral)',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota RAD Geral'),
        boxmode='group',
        plot_bgcolor='#FFFFFF',
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(
    Output("strip_chart_timeseries", "figure"),
    Input("year_timeseries", "value")
)

def update_output_strip(year_timeseries):

    filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]
    filtered_df = filtered_timeseries.sort_values(by='Unidade')



    color_map = {
            'Professor Adjunto': 'rgba(253, 174, 97, 0.7)',
            'Professor Assistente': 'rgba(171, 217, 233, 0.7)',
            'Professor Associado': 'rgba(233, 25, 28, 0.7)',
            'Professor Auxiliar': 'rgba(44, 123, 182, 0.7)',
            'Professor Titular': 'rgba(0, 0, 0, 0.7)',
        }

    figure = px.strip(
               filtered_df, 
               x='Unidade', 
               y='Nota_RAD',
               color='Cargo',
               color_discrete_map=color_map,
               orientation='v', 
               stripmode='overlay', 
               title='Gráfico beeswarm por unidade',
            )

    figure.update_layout(
        xaxis_title='Unidade',
        yaxis_title='Nota RAD',
        plot_bgcolor='#fff',
    )

    return figure

@app.callback(
    Output("boxplot_rad_timeseries_unity", "figure"),
    Input("unity_timeseries_boxplot", "value")
)

def update_output_boxplot(unity_timeseries_boxplot):

    filtered_timeseries = time_series.loc[time_series['Unidade'] == unity_timeseries_boxplot]
    df_average = filtered_timeseries.groupby('Ano')['Nota_RAD'].mean().reset_index()
    df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()


    data = []
    
    data.append(go.Box(
        x=filtered_timeseries['Ano'],
        y=filtered_timeseries['Nota_RAD'],
        name='Nota RAD',
        marker_color='#A63A50',
        boxmean=True
    )
    )

    data.append(go.Scatter(
        x=df_average['Ano'],
        y=df_average['Nota_RAD'],
        mode='lines',
        name='Nota RAD média',
        line=dict(color='black')
    ))
    
    layout = go.Layout(
        title='Relatório de Atividades Docentes 2023 - Série por unidade (Nota geral)',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota RAD Geral'),
        boxmode='group',
        plot_bgcolor='#FFFFFF',
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

if __name__ == '__main__':
    app.run(debug=True)
    