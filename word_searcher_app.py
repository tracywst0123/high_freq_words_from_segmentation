import pandas as pd
import os
import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from word_dictionary import get_words_df_with_seg

app = dash.Dash()

data = pd.read_csv('original_data.csv', dtype=str)
print_result = []


def count_one_word(data, word):

    have_segment = data[data['account_name'].str.contains(word)]
    count_str = len(have_segment.index)
    return word+'   出现了    '+str(count_str)+'    次'


def get_frequency_table(filter_seg=None):
    if filter_seg:
        dd_table = get_words_df_with_seg(filter_seg=filter_seg)
        # dd_table = dd_table[dd_table.word.notnull()]
    else:
        dd_table = pd.read_csv('word_dictionary_char.csv')

    if dd_table.empty:
        dd_table = pd.DataFrame(data={'word': ['筛选是空的！！'], 'count': ['000000']})

    dd_table = dd_table[['word', 'count']]
    d_table = dash_table.DataTable(id='freq_table',
                                   columns=[{'id': 'word', 'name': 'word'},
                                            {'id': 'count', 'name': 'count'}],
                                   data=dd_table.to_dict('records'),
                                   export_format="csv",
                                   style_table={'width': '50%'},
                                   sort_action='native')
    return d_table


def get_layout():
    layout = [html.H2(children='Word Frequency Dash'),
              html.Div(dcc.Input(id='word_segment', type='text')),
              html.Button('筛选字段_原始数据', id='original_submit', n_clicks=0),
              html.Div(id='result', children=[html.Div()]),
              html.Div(dcc.Input(id='table_seg', type='text')),
              html.Button('筛选字段_分词表', id='filter_submit', n_clicks=0),
              html.Div(id='table', children=[get_frequency_table()])]
    return html.Div(layout)


app.layout = get_layout


@app.callback([Output('result', 'children')],
              [Input('original_submit', 'n_clicks')],
              [State('word_segment', 'value')])
def update_print_result(submit_clicks, text):
    global print_result
    if submit_clicks >= 1:
        result = count_one_word(data, text)
        print_result.append(result)
    return [[html.Div(children=cur) for cur in print_result]]


@app.callback([Output('table', 'children')],
              [Input('filter_submit', 'n_clicks')],
              [State('table_seg', 'value')])
def update_select_table(click, value):
    if click >= 1:
        return [get_frequency_table(filter_seg=value)]
    else:
        return [get_frequency_table()]


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run_server(debug=True, host='0.0.0.0', port=port)

