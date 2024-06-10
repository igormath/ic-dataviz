# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import html, dcc
from dash.dependencies import Input, Output
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import flask

server = flask.Flask(__name__)
app = dash.Dash(server=server, name="Dashboard", url_base_pathname="/rad/", use_pages=True, pages_folder="")

df = pd.read_csv('df_sem_pendentes_number.csv')
time_series = pd.read_csv('serie_nota_RAD_row_(2017-2022)-sem-NaN.csv')

averageGradePerUnit = df.groupby('UNIDADE')['Nota_RAD'].mean().reset_index()
averageGradePerUnit.rename(columns={'Nota_RAD': 'Media'}, inplace=True)

fig_cumulative = px.bar(df, x="UNIDADE", y="Nota_RAD", title="Notas por Unidade cumulativo")
fig_average = px.bar(averageGradePerUnit, x="UNIDADE", y="Media", title="Notas por unidade média")

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
opcoes_checklist = ['Média Geral'] + unique_unities

dash.register_page(
        "Visão Histórica", 
        path='/',
        order=0, 
        layout=html.Main([

            dcc.Checklist(
                options=[{'label': 'Selecionar Todos', 'value': 'Select All'}],
                value=['Select All'], 
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
            value='Média Geral', 
            inline=True,
            id='unity_timeseries_boxplot',
            ),

            # dcc.Graph(id='boxplot_rad_timeseries_unity'),

            # dcc.Graph(id='timeseries_errorbands'),

            dcc.Graph(id='boxplot_line'),
]))

# Visão por ano: gráficos que só mostram um ano. Aqui, teria um seletor único de
# que afetaria todos os gráficos



radio_items_year_options = sorted(time_series['Ano'].unique())

dash.register_page(
        "Visão por ano", 
        path='/visao-ano',
        order=1, 
        layout=html.Main([
            
           
            # dcc.RadioItems(
            #     options=radio_items_year_options,
            #     value=radio_items_year_options[len(radio_items_year_options) - 1],
            #     inline=True,
            #     id='year_timeseries',
            # ),

            html.Div([
                html.Div([
                        dcc.Dropdown(
                            options=radio_items_year_options,
                            value=radio_items_year_options[len(radio_items_year_options) - 1],
                            clearable=False,
                            searchable=False,
                            className="year-dropdown",
                            id='year_timeseries',
                        ),
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
                ], className="dropdown__checklist__div"),

                dcc.Graph(id='grouped-boxplot'),
            ],
            className='row',
            id='grouped-boxplot-container',
            ),
            
            html.Div(
                dcc.Graph(id='number_of_teachers_bars'), 
                className="fixed-div"
            ),
                
            html.Div([
                    dcc.Graph(
                        id='strip_chart_timeseries',
                        figure=fig
                    ),

                    dcc.Graph(id='violin_unity'),

                    # dcc.Graph(id='boxplot_rad_timeseries'),
                ],
                className = 'row'
            ),

            ],
            ),
)

# Layout da página principal

dash.register_page(
        "Sobre", 
        path='/sobre',
        order=2,
        layout=html.Div([
            html.P("O Relatório de Atividades Docentes (RAD) resume as atividades desenvolvidas pelos docentes nas dimensões de ensino, pesquisa, extensão e gestão no período de avaliação, e as quantifica com base em indicadores mensuráveis. Estes dados são posteriormente validados pelas comissões locais de cada unidade de ensino seguindo as regras dispostas na resolução CONSUN 028/2018 (UPE, 2018)."),
            html.P("Este processo avaliativo bem estruturado gera dados confiáveis do desempenho dos docentes e, se analisados de forma agregada, também de cada unidade de ensino que compõe a UPE. Esses dados podem revelar insights valiosos capazes de auxiliar no processo de tomada de decisões, contribuindo assim para alcançar um dos principais objetivos de um processo avaliativo em uma organização: o aprimoramento contínuo das atividades desenvolvidas."),
            html.P("Desse modo, a construção deste dashboard para disponibilizar os dados do RAD aos gestores da UPE de forma simples e intuitiva pode levar à geração de inúmeros insights, como identificação da necessidade de programas de capacitação, incentivo a projetos de pesquisa/ensino/extensão em áreas/unidades específicas da instituição e, de forma geral, uma visão mais detalhada e granularizada das atividades realizadas na instituição."),
        ],
        className="home-page-container", ),
)

pages = iter(dash.page_registry.values())
page0 = next(pages)
page1 = next(pages)
page2 = next(pages)


# Layout com um componente dcc.Location para capturar o pathname da URL
app.layout = html.Header([
        html.Div([
            html.Div([
                html.Img(src=r'assets/dotLab-white.png', alt='DotLab logo', className='icon-header'),
                html.Img(src=r'assets/upe-campus_caruaru_white-transparente.png', alt='Upe Caruaru logo', className='icon-header upe-logo'),
            ], className='icons-container'),
        html.H1('Painel RAD', className="page-title"),
        ], className="header-container"),
        html.Nav(
            html.Ul([
                html.Li(
                    dcc.Link(f"{page0['name']}", href=page0["relative_path"]),
                    className="nav-link active", 
                    id="li-0",
                ), #adicionar classname
                html.Li(
                    dcc.Link(f"{page1['name']}", href=page1["relative_path"]),
                    className="nav-link", 
                    id="li-1",
                ),
                html.Li(
                    dcc.Link(f"{page2['name']}", href=page2["relative_path"]),
                    className="nav-link", 
                    id="li-2",
                ),
        ], className="main-links-list", id="nav-list"),
        ),
        dcc.Location(id='url', refresh=False),
    dash.page_container,
])

@app.callback(
    [Output(f"li-{i}", "className") for i in range(3)],
    Input("url", "pathname"),
)
def update_active_links(pathname):
    active_index = None
    if pathname == page0["relative_path"]:
        active_index = 0
    elif pathname == page1["relative_path"]:
        active_index = 1
    elif pathname == page2["relative_path"]:
        active_index = 2

    return [
        "nav-link active" if i == active_index else "nav-link"
        for i in range(3)
    ]

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
        title='Notas por unidade (separadas por dimensão) - 2022',
        xaxis=dict(title='Unidade'),
        yaxis=dict(title='Nota'),
        boxmode='group',
        plot_bgcolor='#FFFFFF',
        title_y = 0.8,
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="right",
            y=-0.05,
            x=0.22
        ),
    )
    
    figure = go.Figure(data=data, layout=layout)

    figure.update_yaxes(
        showgrid=True,
        gridwidth=1, 
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    figure.update_xaxes(
        fixedrange=True,
    )

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
        title='Evolução da nota média por unidade',
        xaxis_title='Ano',
        yaxis_title='Nota RAD Média',
        xaxis_tickformat=',d',
        xaxis=dict(
            tickmode='array',
            tickvals=media_unidade_ano['Ano'].unique(),
            ticktext=[str(int(ano)) for ano in media_unidade_ano['Ano'].unique()] ,
            title={
                'standoff': 50,
            }
        ),
        plot_bgcolor='#FFFFFF',
        title_y = 0.9,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="right",
            x=1
        ),
        # xaxis_range=[2016, 2022]
    )

    fig.update_yaxes(
        gridwidth=1, 
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    fig.update_xaxes(
        fixedrange=True,
        gridwidth=1, 
        gridcolor='#e6e9f8',
    )

    return fig

@app.callback(
    Output("violin_unity", "figure"),
    Input("year_timeseries", "value"),
    Input("unity", "value")
)

def update_output_boxplot(year_timeseries, unity):

    filtered_df = time_series[time_series['Unidade'].isin(unity)]
    filtered_timeseries = filtered_df.loc[filtered_df['Ano'] == year_timeseries]
    df_average = filtered_timeseries.groupby('Unidade')['Nota_RAD'].mean().reset_index()
    df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()

    units = sorted(filtered_timeseries['Unidade'].unique())

    fig = go.Figure()

    for unity_name in units:
        fig.add_trace(go.Violin(x=filtered_timeseries['Unidade'][filtered_timeseries['Unidade'] == unity_name],
                                y=filtered_timeseries['Nota_RAD'][filtered_timeseries['Unidade'] == unity_name],
                                name=unity_name,
                                meanline_visible=True,
                                fillcolor='rgba(166, 58, 80, 0.7)',
                                line_color='rgba(166, 58, 80, 1)',
                                showlegend=False,
                                hoverinfo='y+name'
                            ))
        
    fig.add_trace(go.Scatter(
        x=df_average['Unidade'],
        y=df_average['Nota_RAD'],
        mode='lines',
        name='Nota RAD média',
        line=dict(
            color='black',
            dash='dash',
        )
    ))
        
    fig.update_layout(
        plot_bgcolor='#FFFFFF',
        title_text=f'Distribuição das notas por unidade - {year_timeseries}',
    )

    fig.update_yaxes(
        gridwidth=1, 
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    fig.update_xaxes(
        fixedrange=True,
    )
                                
    return fig


# @app.callback(
#     Output("boxplot_rad_timeseries", "figure"),
#     Input("year_timeseries", "value")
# )

# def update_output_boxplot(year_timeseries):

#     filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]
#     df_average = filtered_timeseries.groupby('Unidade')['Nota_RAD'].mean().reset_index()
#     df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()


#     data = []
    
#     data.append(go.Box(
#         x=sorted(filtered_timeseries['Unidade']),
#         y=filtered_timeseries['Nota_RAD'],
#         name='Nota RAD',
#         marker_color='#A63A50',
#         boxmean=True,
#     )
#     )

#     data.append(go.Scatter(
#         x=df_average['Unidade'],
#         y=df_average['Nota_RAD'],
#         mode='lines',
#         name='Nota RAD média',
#         line=dict(
#             color='black',
#             dash='dash',
#         )
#     ))
    
#     layout = go.Layout(
#         title=f'Relatório de Atividades Docentes {year_timeseries} - Notas por unidade (Nota geral)',
#         xaxis=dict(title='Unidade'),
#         yaxis=dict(title='Nota RAD Geral'),
#         boxmode='group',
#         plot_bgcolor='#FFFFFF',
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1,
#         ),
#     )
    
#     figure = go.Figure(data=data, layout=layout)
#     return figure

@app.callback(
    Output("strip_chart_timeseries", "figure"),
    Input("year_timeseries", "value"),
    Input("unity", "value")
)

def update_output_strip(year_timeseries, unity):
    filtered_df_unity = time_series[time_series['Unidade'].isin(unity)]
    filtered_timeseries = filtered_df_unity.loc[filtered_df_unity['Ano'] == year_timeseries]
    filtered_df_result = filtered_timeseries.sort_values(by='Unidade')

    color_map = {
            'Professor Adjunto': 'rgba(253, 174, 97, 0.7)',
            'Professor Assistente': 'rgba(171, 217, 233, 0.7)',
            'Professor Associado': 'rgba(233, 25, 28, 0.7)',
            'Professor Auxiliar': 'rgba(44, 123, 182, 0.7)',
            'Professor Titular': 'rgba(0, 0, 0, 0.7)',
        }

    figure = px.strip(
               filtered_df_result, 
               x='Unidade', 
               y='Nota_RAD',
               color='Cargo',
               color_discrete_map=color_map,
               orientation='v', 
               stripmode='overlay', 
               title='Notas por cargo',
            )

    figure.update_layout(
        xaxis_title='Unidade',
        yaxis_title='Nota RAD',
        plot_bgcolor='#fff',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),  
    )

    # Adiciona as linhas das grades

    figure.update_yaxes(
        showgrid=True,
        gridwidth=1, 
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    figure.update_xaxes(
        fixedrange=True,
    )

    return figure

@app.callback(
    Output("number_of_teachers_bars", "figure"),
    Input("year_timeseries", "value")
)

def horizontal_bar_chart(year_timeseries):
    filtered_timeseries = time_series.loc[time_series['Ano'] == year_timeseries]
    n_teachers = filtered_timeseries['Unidade'].value_counts().reset_index()
    n_teachers.columns = ['Unidade', 'N_Professores']
    
    figure = go.Figure(go.Bar(
        x = n_teachers['N_Professores'],
        y = n_teachers['Unidade'],
        orientation = 'h',
    ))

    figure.update_layout(
        title = f'Número de professores por Unidade, Ano {year_timeseries}',
        paper_bgcolor = '#e5ebf7',
        height = 420,  # Defina a altura desejada em pixels
        margin=dict(
            t=40,
            pad=0
        ),
    )

    figure.update_xaxes(
        fixedrange=True,
    )

    figure.update_yaxes(
        fixedrange=True,
    )

    return figure

# @app.callback(
#     Output("boxplot_rad_timeseries_unity", "figure"),
#     Input("unity_timeseries_boxplot", "value")
# )

# def update_output_boxplot(unity_timeseries_boxplot):
    
#     filtered_timeseries = time_series.loc[time_series['Unidade'] == unity_timeseries_boxplot]
#     df_average = filtered_timeseries.groupby('Ano')['Nota_RAD'].mean().reset_index()
#     df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()

#     data = []

#     if (unity_timeseries_boxplot == 'Média Geral'):    
#         data.append(go.Box(
#             x=time_series['Ano'],
#             y=time_series['Nota_RAD'],
#             name='Nota RAD',
#             marker_color='#A63A50',
#             boxmean=True
#         )
#         )
#     else:
#         data.append(go.Box(
#             x=filtered_timeseries['Ano'],
#             y=filtered_timeseries['Nota_RAD'],
#             name='Nota RAD',
#             marker_color='#A63A50',
#             boxmean=True
#         )
#         )

#     data.append(go.Scatter(
#         x=df_average['Ano'],
#         y=df_average['Nota_RAD'],
#         mode='lines',
#         name='Nota RAD média',
#         line=dict(color='black')
#     ))
    
#     layout = go.Layout(
#         title='Relatório de Atividades Docentes - Série por unidade (Nota geral)',
#         xaxis=dict(title='Unidade'),
#         yaxis=dict(title='Nota RAD Geral'),
#         boxmode='group',
#         plot_bgcolor='#FFFFFF',
#     )
    
#     figure = go.Figure(data=data, layout=layout)
#     return figure

@app.callback(
    Output("boxplot_line", "figure"),
    Input("unity_timeseries_boxplot", "value")
)

def update_output_boxplot(unity_timeseries_boxplot):
    
    filtered_timeseries = time_series.loc[time_series['Unidade'] == unity_timeseries_boxplot]
    df_average = filtered_timeseries.groupby('Ano')['Nota_RAD'].mean().reset_index()
    df_average['Nota_RAD'] = filtered_timeseries['Nota_RAD'].mean()


    # Monta a série para cálculo da média e quartis.
    quartiles_dataframe = time_series.groupby(['Unidade', 'Ano'])['Nota_RAD'].describe(percentiles=[.25, .75])
    quartiles_dataframe = quartiles_dataframe.reset_index()[['mean', '25%', '75%', 'Unidade', 'Ano']]
    if (unity_timeseries_boxplot == 'Média Geral'):
        filtered_quartiles_dataframe = quartiles_dataframe.groupby('Ano')[['mean', '25%', '75%']].mean().reset_index()
    else:
        filtered_quartiles_dataframe = quartiles_dataframe.loc[quartiles_dataframe['Unidade'] == unity_timeseries_boxplot]

    fig = go.Figure()

    if (unity_timeseries_boxplot == 'Média Geral'):    
        fig.add_trace(go.Violin(
            x=time_series['Ano'],
            y=time_series['Nota_RAD'],
            name='Nota RAD',
            meanline_visible=True,
            fillcolor='rgba(166, 58, 80, 0.7)',
            line_color='rgba(166, 58, 80, 1)',
            showlegend=False,
        ))

        fig.add_trace(go.Scatter(
        x=filtered_quartiles_dataframe['Ano'],
        y=filtered_quartiles_dataframe['mean'],
        mode='lines',
        name='Nota RAD média',
        line=dict(color='rgb(31, 119, 180)'),
        ))
    else:
        fig.add_trace(go.Violin(
            x=filtered_timeseries['Ano'],
            y=filtered_timeseries['Nota_RAD'],
            name='Nota RAD',
            meanline_visible=True,
            fillcolor='rgba(166, 58, 80, 0.7)',
            line_color='rgba(166, 58, 80, 1)',
            showlegend=False,
        ))

        fig.add_trace(go.Scatter(
            x=filtered_quartiles_dataframe['Ano'],
            y=filtered_quartiles_dataframe['mean'],
            mode='lines',
            name='Nota RAD média',
            line=dict(color='rgb(31, 119, 180)'),
        ))
    
    fig.update_layout(
        title='Distribuição da nota média por ano',
        xaxis=dict(title='Ano'),
        yaxis=dict(title='Nota RAD'),
        boxmode='group',
        plot_bgcolor='#FFFFFF',
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1, 
        gridcolor='#e6e9f8',
        fixedrange=True,
    )

    fig.update_xaxes(
        fixedrange=True,
    )
    
    return fig

# @app.callback(
#     Output("timeseries_errorbands", "figure"),
#     Input("unity_timeseries_boxplot", "value")
# )

# def update_output_errorbands(unity_timeseries_boxplot):

#     # Constrói a série a partir da unidade informada no parâmetro da função, criando um novo dataframe com as colunas dos percentis 25% e 75%.
#     quartiles_dataframe = time_series.groupby(['Unidade', 'Ano'])['Nota_RAD'].describe(percentiles=[.25, .75])
#     quartiles_dataframe = quartiles_dataframe.reset_index()[['mean', '25%', '75%', 'Unidade', 'Ano']]
#     if (unity_timeseries_boxplot == 'Média Geral'):
#         filtered_quartiles_dataframe = quartiles_dataframe.groupby('Ano')[['mean', '25%', '75%']].mean().reset_index()
#     else:
#         filtered_quartiles_dataframe = quartiles_dataframe.loc[quartiles_dataframe['Unidade'] == unity_timeseries_boxplot]
    
#     figure = go.Figure([
#         go.Scatter(
#             name='Média',
#             x=filtered_quartiles_dataframe['Ano'],
#             y=filtered_quartiles_dataframe['mean'],
#             mode='lines',
#             line=dict(color='rgb(31, 119, 180)'),
#         ),
#         go.Scatter(
#             name='Limite Superior',
#             x=filtered_quartiles_dataframe['Ano'],
#             y=filtered_quartiles_dataframe['75%'],
#             mode='lines',
#             marker=dict(color="#444"),
#             line=dict(width=0),
#             showlegend=False
#         ),
#         go.Scatter(
#             name='Limite Inferior',
#             x=filtered_quartiles_dataframe['Ano'],
#             y=filtered_quartiles_dataframe['25%'],
#             marker=dict(color="#444"),
#             line=dict(width=0),
#             mode='lines',
#             fillcolor='rgba(68, 68, 68, 0.3)',
#             fill='tonexty',
#             showlegend=False
#         )
#     ])

#     figure.update_layout( xaxis={
#         'range': [filtered_quartiles_dataframe['Ano'].min(), filtered_quartiles_dataframe['Ano'].max()], 
#         'tickvals': [*range(int(filtered_quartiles_dataframe['Ano'].min()), int(filtered_quartiles_dataframe['Ano'].max()))]
#     })
    
#     return figure

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    