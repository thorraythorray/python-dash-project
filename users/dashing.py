import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
import dash_core_components as dcc 
import dash_html_components as html
from datetime import datetime as dt 
import dash_table
import numpy as np
import tushare as ts       
import threading  
from .tushares import TushareData


PAGE_SIZE = 20

# data source 
basic_df = TushareData.get_shares_basic()

app = dash.Dash(__name__)
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.css.config.serve_locally = False

options = [{'label': "{}({})".format( i[2], i[1]), 'value': i[0]} for i in np.array(basic_df).tolist()]

index_page = html.Div(children=[
    html.H1(children='量化投资系统', style={'textAlign': 'center'}),

    html.Div(children=[
        # html.Label('Dropdown'),
        dcc.Dropdown(
            id="select-filering", 
            placeholder="请输入要查的名字或代码..", 
            style={'marginBottom': '18px'},
            clearable=False
            ),
        dcc.Link('查看k线详情', id="detail-linking", href="/detail", style={"flaot": "left", "color": "black"}),
        dcc.Link('跳转东方财富', id="dongfang-linking", href="/dongfang", target="_blank", style={"marginLeft": "4%", "color": "black"}),
        dcc.Link('投资分析', id="lingwai-linking", href="/lingwai", target="_blank", style={"marginLeft": "4%", "color": "black"}),
        dash_table.DataTable(
            id='table-filtering',
            columns=[
                {"name": i, "id": i} for i in basic_df.columns
            ],

            column_selectable="single",

            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom',

            sort_action='custom',
            sort_mode='multi',
            sort_by=[{
                "column_id": "上市日期",
                "direction": "asc"

            }],
            style_table={"marginTop": "18px"},
            style_as_list_view=True,
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white',
                'textAlign': 'center'
            },
        ),   
    ],
    style={
        "width": "60%",
        "marginLeft": "20%"
    }
    )
])

@app.callback(
    dash.dependencies.Output("select-filering", "options"),
    [dash.dependencies.Input("select-filering", "search_value")])
def update_options(search_value):
    print("options query_value", search_value)
    if not search_value:
        raise PreventUpdate
    dff = basic_df
    options = None
    query_dff = None
    query_dff = dff.loc[dff["股票代码"].str.contains(search_value)]
    if query_dff.empty:
        query_dff = dff.loc[dff["股票名称"].str.contains(search_value)]
    options = [{'label': "{}({})".format( i[2], i[1]), 'value': i[0]} for i in np.array(query_dff).tolist()]

    return options

@app.callback(
    dash.dependencies.Output("detail-linking", "href"),
    [dash.dependencies.Input("select-filering", "value")])
def update_link(filter_value):
    return "/detail?code={}".format(filter_value)

@app.callback(
    dash.dependencies.Output("dongfang-linking", "href"),
    [dash.dependencies.Input("select-filering", "value")])
def turn_dongfang(filter_value):
    print("dongfangdongfang", filter_value)
    code = filter_value.split(".")[0]
    url = "http://quote.eastmoney.com/sz{}.html".format(code)
    return url

@app.callback(
    dash.dependencies.Output("lingwai-linking", "href"),
    [dash.dependencies.Input("select-filering", "value")])
def turn_lingwai(filter_value):
    print("lingwai", filter_value)
    url = "http://127.0.0.1:8000/users/ans"
    return url

@app.callback(
    Output('table-filtering', "data"),
    Input('table-filtering', "page_current"),
    Input('table-filtering', "page_size"),
    Input('table-filtering', "sort_by"),
    [dash.dependencies.Input("select-filering", "value")])
def update_table(page_current, page_size, sort_by, query_value):
    dff = basic_df
    if query_value:
        query_dff = dff.loc[dff["TS代码"].eq(query_value)]
        dff = query_dff

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')


# new page 

detail_page = html.Div(children=[
        html.Div(children=[
            html.Button('日K线', id='btn-nclicks-1', n_clicks=0),
            html.Button('周k线', id='btn-nclicks-2', n_clicks=0, style={"marginLeft": "4%"}),
            html.Button('月k线', id='btn-nclicks-3', n_clicks=0, style={"marginLeft": "4%"}),
            html.Div(id='detail-container', style={"marginTop": "20px", "font": "large", "color": "orangered"})
        ],
        style={"marginTop": "20px"}
    ),
    dcc.Graph(
        id='my-graph', 
        animate=True,
        config={"autosizable": True, "displayModeBar": True}
        )

],style={"width": "60%", "marginLeft": "20%"})

@app.callback(Output('detail-container', 'children'),
              [dash.dependencies.Input('url', 'search')])
def update_detail(selected_dropdown_value):
    print("k data", selected_dropdown_value)
    
    share_ts = selected_dropdown_value.replace("?", "").split("&")
    params = {i.split("=")[0]:i.split("=")[1] for i in share_ts}
    ts_code = params["code"]

    query_dff = TushareData.get_K_data("daily", ts_code)
    
    data = query_dff.iloc[1, :].tolist()
    data = data[2:6] + data[7:9]
    msg = "今日成交 ：开盘{}，  收盘{}，  最高{}，  最低{}， 跌涨额{}，  跌涨幅{}".format(*data)
    return html.Div(msg)

@app.callback(Output('my-graph', 'figure'), 
              Input('btn-nclicks-1', 'n_clicks'),
              Input('btn-nclicks-2', 'n_clicks'),
              Input('btn-nclicks-3', 'n_clicks'),
              [dash.dependencies.Input('url', 'search')])
def update_graph(btn1, btn2, btn3, selected_dropdown_value):

    print("gragh", selected_dropdown_value)
    share_ts = selected_dropdown_value.replace("?", "").split("&")
    params = {i.split("=")[0]:i.split("=")[1] for i in share_ts}
    ts_code = params["code"]
    print("search", ts_code)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        query_dff = TushareData.get_K_data("daily", ts_code)
    elif 'btn-nclicks-2' in changed_id:
        query_dff = TushareData.get_K_data("weekly", ts_code)
    elif 'btn-nclicks-3' in changed_id:
        query_dff = TushareData.get_K_data("monthly", ts_code)
    else:
        query_dff = TushareData.get_K_data("daily", ts_code)

    titile = basic_df.loc[basic_df["TS代码"].eq(ts_code)].iloc[0, 2]
    return {
        'data':[
            {
            'x': query_dff.trade_date,
            'y': query_dff.close
            }
        ],
        'layout': {
            'title': titile + " 实时行情图"
        }
    }

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/detail':
        return detail_page
    else:
        return index_page

if __name__ =="__main__":
    app.run_server()