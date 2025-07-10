#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Dash Mantine Components的DatePicker功能
"""

import dash
from dash import Dash, Input, Output, callback, html
import dash_mantine_components as dmc
from datetime import date

# 创建Dash应用
app = Dash(__name__)

# 应用布局
app.layout = html.Div([
    html.H1("Mantine DatePicker 测试", style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        html.H3("DatePickerInput 组件测试"),
        html.P("测试点击月份和年份是否可以快速选择"),
        
        dmc.DatePickerInput(
            id="date-picker-input",
            label="选择日期",
            placeholder="选择一个日期",
            value=None,
            style={'width': '300px', 'marginBottom': '20px'}
        ),
        
        html.Div(id="selected-date-output"),
        
        html.Hr(style={'margin': '30px 0'}),
        
        html.H3("使用说明"),
        html.Ul([
            html.Li("点击输入框打开日期选择器"),
            html.Li("尝试点击顶部的月份标题切换月份视图"),
            html.Li("尝试点击顶部的年份标题切换年份视图"),
            html.Li("这是我们期望实现的交互效果")
        ])
    ], style={
        'maxWidth': '600px',
        'margin': '0 auto',
        'padding': '20px'
    })
])

# 回调函数
@callback(
    Output("selected-date-output", "children"),
    Input("date-picker-input", "value")
)
def update_output(selected_date):
    if selected_date:
        return html.P(f"选择的日期: {selected_date}", style={'color': 'green', 'fontWeight': 'bold'})
    else:
        return html.P("未选择日期", style={'color': 'gray'})

if __name__ == "__main__":
    app.run(debug=True, port=8053)