# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('df_sem_pendentes_number.csv')
time_series = pd.read_csv('serie_nota_RAD_row_2017-2022.csv')

averageGradePerUnit = df.groupby('UNIDADE')['Nota_RAD'].mean().reset_index()
averageGradePerUnit.rename(columns={'Nota_RAD': 'Media'}, inplace=True)

fig_cumulative = px.bar(df, x="UNIDADE", y="Nota_RAD", title="Notas por Unidade cumulativo")
fig_average = px.bar(averageGradePerUnit, x="UNIDADE", y="Media", title="Notas por unidade média")

app = Dash(__name__, use_pages=True, pages_folder="")
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

# Visão histórica: gráficos que plotam todos os anos.

unique_unities = sorted(time_series['Unidade'].unique())
opcoes_checklist = unique_unities + ['Média Geral']

dash.register_page(
        "Visão Histórica", 
        path='/visao-historica', 
        layout=html.Main([
            html.H2('Visão Histórica', className="page-title"),

            dcc.Checklist(
                options=[{'label': 'Selecionar Todos', 'value': 'Select All'}],
                value=[], 
                inline=True,
                id='select_all',
            ),

            dcc.Checklist(
                options=opcoes_checklist,
                value=[], 
                inline=True,
                id='unity_timeseries',
            ),

            dcc.Graph(
                id='unit-rad-timeseries',
            ),

            dcc.RadioItems(
            options=opcoes_checklist,
            value='', 
            inline=True,
            id='unity_timeseries_boxplot',
            ),

            dcc.Graph(id='boxplot_rad_timeseries_unity'),

            dcc.Graph(id='timeseries_errorbands'),
]))

# Visão por ano: gráficos que só mostram um ano. Aqui, teria um seletor único de
# que afetaria todos os gráficos

dash.register_page(
        "Visão por Ano", 
        path='/visao-ano', 
        layout=html.Main([
            html.H2('Visão por Ano', className="page-title"),
            html.P('Box plot das quatro dimensões do Relatório de Atividades Docentes da Universidade de Pernambuco, agrupados por unidade de ensino.', className="page-paragraph"),

            dcc.RadioItems(
                options=sorted(time_series['Ano'].unique()),
                value='', 
                inline=True,
                id='year_timeseries',
            ),

            dcc.Graph(
                id='strip_chart_timeseries',
                figure=fig
            ),

            html.P(
                id='number_of_teachers',
                className="page-paragraph",
            ),

            dcc.Graph(id='violin_unity'),

            dcc.Graph(id='boxplot_rad_timeseries'),

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
]))

# Layout da página principal

dash.register_page(
        "Página Inicial", 
        path='/',
        layout=html.Div([
            html.P("O Relatório de Atividades Docentes (RAD) resume as atividades desenvolvidas pelos docentes nas dimensões de ensino, pesquisa, extensão e gestão no período de avaliação, e as quantifica com base em indicadores mensuráveis. Estes dados são posteriormente validados pelas comissões locais de cada unidade de ensino seguindo as regras dispostas na resolução CONSUN 028/2018 (UPE, 2018)."),
            html.P("Este processo avaliativo bem estruturado gera dados confiáveis do desempenho dos docentes e, se analisados de forma agregada, também de cada unidade de ensino que compõe a UPE. Esses dados podem revelar insights valiosos capazes de auxiliar no processo de tomada de decisões, contribuindo assim para alcançar um dos principais objetivos de um processo avaliativo em uma organização: o aprimoramento contínuo das atividades desenvolvidas."),
            html.P("Desse modo, a construção deste dashboard para disponibilizar os dados do RAD aos gestores da UPE de forma simples e intuitiva pode levar à geração de inúmeros insights, como identificação da necessidade de programas de capacitação, incentivo a projetos de pesquisa/ensino/extensão em áreas/unidades específicas da instituição e, de forma geral, uma visão mais detalhada e granularizada das atividades realizadas na instituição."),
        ],
        className="home-page-container", ),
)

app.layout = html.Main([
    html.H1('Protótipo RAD', className="page-title"),

    html.Ul([
        html.Li(
            dcc.Link(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ], className="main-links-list"),
    dash.page_container,
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
        title='Relatório de Atividades Docentes 2022 - Notas por unidade (separadas por dimensão)',
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
    

# Callback para selecionar todas as opções no gráfico de série temporal

@app.callback(
    Output('unity_timeseries', 'value'),
    Input('select_all', 'value')
)
def select_all_options(select_all):
    if 'Select All' in select_all:
        return opcoes_checklist
    return []

@app.callback(
    Output("unit-rad-timeseries", "figure"),
    Input("unity_timeseries", "value")
)

def update_output_strip(unity_timeseries):
    # Cria um novo dataframe apenas com a nota média do RAD em toda UPE
    average_per_year = time_series.groupby('Ano')['Nota_RAD'].mean().reset_index()
    general_average_df = pd.DataFrame({'Docente': [''] * len(average_per_year),
                                  'Cargo': [''] * len(average_per_year),
                                  'Nota_RAD': average_per_year['Nota_RAD'],
                                  'Unidade': 'Média Geral',
                                  'Ano': average_per_year['Ano']})
    
    # Adiciona este dataframe criado ao dataframe lido do CSV externo
    df_with_average = pd.concat([time_series, general_average_df], ignore_index=True)

    # Filtra este dataframe de acordo com as opções escolhidas pelo usuário na CheckList.
    filtered_time_series = df_with_average.loc[df_with_average['Unidade'].isin(unity_timeseries)]
    media_unidade_ano = filtered_time_series.groupby(['Unidade', 'Ano'])['Nota_RAD'].mean().reset_index()
    media_unidade_ano.columns = ['Unidade', 'Ano', 'Nota_Media']

    fig = px.line(media_unidade_ano, x = 'Ano', y = 'Nota_Media', color='Unidade')
    
    fig.update_layout(
        xaxis_title='Ano',
        yaxis_title='Nota RAD Média',
        xaxis_tickformat=',d',
        xaxis=dict(
            tickmode='array',
            tickvals=media_unidade_ano['Ano'].unique(),
            ticktext=[str(int(ano)) for ano in media_unidade_ano['Ano'].unique()] 
        ),
        # xaxis_range=[2016, 2022]
    )
    return fig

@app.callback(
    Output("violin_unity", "figure"),
    Input("year_timeseries", "value")
)

def update_output_boxplot(year_timeseries):

    filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]

    units = sorted(filtered_timeseries['Unidade'].unique())

    fig = go.Figure()

    for unity in units:
        fig.add_trace(go.Violin(x=filtered_timeseries['Unidade'][filtered_timeseries['Unidade'] == unity],
                                y=filtered_timeseries['Nota_RAD'][filtered_timeseries['Unidade'] == unity],
                                name=unity,
                                meanline_visible=True,
                                fillcolor='rgba(166, 58, 80, 0.7)',
                                line_color='rgba(166, 58, 80, 1)',
                                showlegend=False,
                            ))
                                
    return fig


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
    Output("number_of_teachers", "children"),
    Input("year_timeseries", "value")
)

def calcular_numero(year_timeseries):
    filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]
    n_teachers = filtered_timeseries['Unidade'].value_counts().reset_index()
    n_teachers.columns = ['Unidade', 'N_Professores']
    result_string = 'Quantidade de docentes por unidade:\n'
    for index, row in n_teachers.iterrows():
        result_string += '{}: {}, '.format(row['Unidade'], row['N_Professores'])

    # Removendo a última vírgula e adicionando quebra de linha no final
    result_string = result_string[:-2] + '\n'
    # Supondo que o cálculo do número seja simplesmente o número de cliques no botão
    return result_string

@app.callback(
    Output("boxplot_rad_timeseries_unity", "figure"),
    Input("unity_timeseries_boxplot", "value")
)

def update_output_boxplot(unity_timeseries_boxplot):
    
    filtered_timeseries = time_series.loc[time_series['Unidade'] == unity_timeseries_boxplot]
    df_average = filtered_timeseries.groupby('Ano')['Nota_RAD'].mean().reset_index()
    df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()

    data = []

    if (unity_timeseries_boxplot == 'Média Geral'):    
        data.append(go.Box(
            x=time_series['Ano'],
            y=time_series['Nota_RAD'],
            name='Nota RAD',
            marker_color='#A63A50',
            boxmean=True
        )
        )
    else:
        data.append(go.Box(
            x=filtered_timeseries['Ano'],
            y=filtered_timeseries['Nota_RAD'],
            name='Nota RAD',
            marker_color='#A63A50',
            boxmean=True
        )
        )

    # data.append(go.Scatter(
    #     x=df_average['Ano'],
    #     y=df_average['Nota_RAD'],
    #     mode='lines',
    #     name='Nota RAD média',
    #     line=dict(color='black')
    # ))
    
    layout = go.Layout(
        title='Relatório de Atividades Docentes - Série por unidade (Nota geral)',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota RAD Geral'),
        boxmode='group',
        plot_bgcolor='#FFFFFF',
    )
    
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(
    Output("timeseries_errorbands", "figure"),
    Input("unity_timeseries_boxplot", "value")
)

def update_output_errorbands(unity_timeseries_boxplot):

    # Constrói a série a partir da unidade informada no parâmetro da função, criando um novo dataframe com as colunas dos percentis 25% e 75%.
    quartiles_dataframe = time_series.groupby(['Unidade', 'Ano'])['Nota_RAD'].describe(percentiles=[.25, .75])
    quartiles_dataframe = quartiles_dataframe.reset_index()[['mean', '25%', '75%', 'Unidade', 'Ano']]
    if (unity_timeseries_boxplot == 'Média Geral'):
        filtered_quartiles_dataframe = quartiles_dataframe.groupby('Ano')[['mean', '25%', '75%']].mean().reset_index()
    else:
        filtered_quartiles_dataframe = quartiles_dataframe.loc[quartiles_dataframe['Unidade'] == unity_timeseries_boxplot]
    
    figure = go.Figure([
        go.Scatter(
            name='Média',
            x=filtered_quartiles_dataframe['Ano'],
            y=filtered_quartiles_dataframe['mean'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Limite Superior',
            x=filtered_quartiles_dataframe['Ano'],
            y=filtered_quartiles_dataframe['75%'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Limite Inferior',
            x=filtered_quartiles_dataframe['Ano'],
            y=filtered_quartiles_dataframe['25%'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    
    return figure

if __name__ == '__main__':
    app.run(debug=True)
    