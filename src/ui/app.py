# Dash应用核心文件
# 创建和配置Dash应用实例

import dash
from dash import dcc, html, Input, Output, State, callback_context
from datetime import datetime, timedelta
import pandas as pd
import dash_mantine_components as dmc

from ..api.alpha_vantage import AlphaVantageClient
from ..data.processor import DataProcessor
from ..data.validator import DataValidator
from ..utils.logger import get_logger
from ..utils.exceptions import APIError, DataValidationError

# 获取日志记录器
logger = get_logger(__name__)


def create_app() -> dash.Dash:
    """
    创建并配置Dash应用实例
    
    Returns:
        dash.Dash: 配置好的Dash应用实例
    """
    logger.info("Creating Dash application...")
    
    # 创建Dash应用
    app = dash.Dash(
        __name__,
        title="iFinance - 智能金融数据查询系统",
        update_title="加载中...",
        suppress_callback_exceptions=True
    )
    
    # 设置应用布局
    app.layout = create_layout()
    
    # 注册回调函数
    register_callbacks(app)
    
    logger.info("Dash application created successfully")
    return app


def create_layout() -> html.Div:
    """
    创建应用的主布局
    
    Returns:
        html.Div: 应用布局组件
    """
    return dmc.MantineProvider([
        html.Div([
        # 页面标题和头部
        html.Div([
            html.H1(
                "iFinance - 智能金融数据查询系统",
                className="app-title",
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'marginBottom': '30px',
                    'fontFamily': 'Arial, sans-serif'
                }
            ),

        ], style={'padding': '20px'}),
        
        # 主要内容区域
        html.Div([
            # 居中的查询面板
            html.Div([
                # 股票搜索区域
                html.Div([
                    html.H3("股票搜索", style={'color': '#34495e', 'marginBottom': '15px'}),
                    
                    # 搜索输入框
                    dcc.Input(
                        id='stock-search-input',
                        type='text',
                        placeholder='输入股票代码或公司名称（如: AAPL, Apple）',
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'fontSize': '14px',
                            'border': '1px solid #bdc3c7',
                            'borderRadius': '4px',
                            'marginBottom': '10px',
                            'boxSizing': 'border-box'  # 确保宽度计算包含padding和border
                        }
                    ),
                    
                    # 搜索按钮
                    html.Button(
                        '搜索',
                        id='search-button',
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'backgroundColor': '#3498db',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'fontSize': '14px',
                            'cursor': 'pointer',
                            'marginBottom': '15px',
                            'boxSizing': 'border-box'  # 确保宽度一致
                        }
                    ),
                    
                    # 搜索结果下拉框
                    html.Div([
                        dcc.Dropdown(
                            id='stock-dropdown',
                            placeholder='选择股票...',
                            style={'width': '100%'}
                        )
                    ], style={'marginBottom': '20px', 'width': '100%'}),
                    
                    # 日期选择器区域
                    html.Label("选择查询日期:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    
                    # Mantine日期选择器
                    html.Div([
                        dmc.DatePickerInput(
                            id='date-picker',
                            label="",
                            placeholder="选择日期",
                            value=datetime.now().date().strftime('%Y-%m-%d'),
                            style={'width': '100%', 'fontSize': '14px'},
                            inputWrapperOrder=['label', 'input', 'description', 'error'],
                            clearable=False
                        )
                    ], style={
                        'marginBottom': '15px', 
                        'width': '100%'
                    }),
                    

                    
                    # 查询按钮
                    html.Button(
                        '查询OHLCV数据',
                        id='fetch-data-button',
                        n_clicks=0,
                        disabled=True,
                        style={
                            'width': '100%',
                            'padding': '12px',
                            'backgroundColor': '#27ae60',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'fontSize': '16px',
                            'cursor': 'pointer',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '30px',
                    'borderRadius': '8px',
                    'maxWidth': '500px',
                    'margin': '0 auto'
                }),
                
                # 数据展示区域
                dcc.Loading(
                    id="loading",
                    children=[
                        html.Div(id='data-display', style={'marginTop': '30px', 'maxWidth': '800px', 'margin': '30px auto 0 auto'})
                    ],
                    type="default"
                )
            ])
    ], style={'padding': '0 20px'}),
        
        # 页脚
        html.Div([
            html.Hr(),
            html.P(
                "Powered by Alpha Vantage API | iFinance v1.0.0",
                style={
                    'textAlign': 'center',
                    'color': '#95a5a6',
                    'fontSize': '12px',
                    'margin': '20px 0'
                }
            )
        ])
    ], style={
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    })
    ])


def register_callbacks(app: dash.Dash) -> None:
    """
    注册应用的回调函数
    
    Args:
        app: Dash应用实例
    """
    logger.info("Registering application callbacks...")
    
    # 初始化组件
    api_client = AlphaVantageClient()
    data_processor = DataProcessor()
    data_validator = DataValidator()
    
    @app.callback(
        [Output('stock-dropdown', 'options'),
         Output('stock-dropdown', 'value')],
        [Input('search-button', 'n_clicks')],
        [State('stock-search-input', 'value')]
    )
    def update_stock_dropdown(n_clicks, search_value):
        """
        更新股票下拉选择框
        """
        if n_clicks == 0 or not search_value:
            return [], None
        
        try:
            # 验证搜索关键词
            validated_keywords = data_validator.validate_search_keywords(search_value)
            
            # 搜索股票
            search_results = api_client.search_symbols(validated_keywords)
            
            # 处理搜索结果
            processed_results = data_processor.process_symbol_search_results(search_results)
            
            # 生成下拉选项
            options = [
                {
                    'label': result['display_label'],
                    'value': result['symbol']
                }
                for result in processed_results[:10]  # 限制显示前10个结果
            ]
            
            # 自动选择第一个结果
            default_value = options[0]['value'] if options else None
            
            return options, default_value
            
        except Exception as e:
            logger.error(f"Stock search failed: {str(e)}")
            return [], None
    
    @app.callback(
        Output('fetch-data-button', 'disabled'),
        [Input('stock-dropdown', 'value')]
    )
    def toggle_fetch_button(selected_stock):
        """
        控制获取数据按钮的启用状态
        """
        return selected_stock is None
    

    
    @app.callback(
        Output('data-display', 'children'),
        [Input('fetch-data-button', 'n_clicks')],
        [State('stock-dropdown', 'value'),
         State('date-picker', 'value')]
    )
    def update_stock_data(n_clicks, selected_stock, selected_date):
        """
        更新股票OHLCV数据显示
        """
        if n_clicks == 0 or not selected_stock:
            return None
        
        
        try:
            # 获取日线数据
            daily_data = api_client.get_daily_data(selected_stock, 'compact')
            
            # 处理数据
            df = data_processor.process_daily_data(daily_data, days_limit=100)
            
            # 检查是否选择了日期
            if selected_date is not None:
                # 查找指定日期的数据
                target_date = pd.to_datetime(selected_date).strftime('%Y-%m-%d')
                
                if target_date in df.index.strftime('%Y-%m-%d'):
                    # 找到指定日期的数据
                    day_data = df[df.index.strftime('%Y-%m-%d') == target_date].iloc[0]
                    
                    return create_ohlcv_display(selected_stock, target_date, day_data)
                else:
                    # 没有找到指定日期的数据，显示最近的数据
                    latest_data = df.iloc[0]
                    latest_date = df.index[0].strftime('%Y-%m-%d')
                    
                    return html.Div([
                        html.Div([
                            html.H4("提示", style={'color': '#f39c12', 'marginBottom': '15px'}),
                            html.P(f"未找到 {target_date} 的数据，显示最近交易日 {latest_date} 的数据：")
                        ], style={
                            'backgroundColor': '#fef9e7',
                            'padding': '15px',
                            'borderRadius': '8px',
                            'border': '1px solid #f1c40f',
                            'marginBottom': '20px'
                        }),
                        create_ohlcv_display(selected_stock, latest_date, latest_data)
                    ])
            else:
                # 没有选择日期，显示最近的数据
                latest_data = df.iloc[0]
                latest_date = df.index[0].strftime('%Y-%m-%d')
                
                return html.Div([
                    html.Div([
                        html.H4("提示", style={'color': '#3498db', 'marginBottom': '15px'}),
                        html.P(f"未选择日期，显示最近交易日 {latest_date} 的数据：")
                    ], style={
                        'backgroundColor': '#e8f4fd',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'border': '1px solid #3498db',
                        'marginBottom': '20px'
                    }),
                    create_ohlcv_display(selected_stock, latest_date, latest_data)
                ])
                
        except Exception as e:
            logger.error(f"Failed to fetch stock data: {str(e)}")
            return create_error_card(str(e))
    
    logger.info("Application callbacks registered successfully")


def create_ohlcv_display(symbol: str, date: str, data: pd.Series) -> html.Div:
    """
    创建OHLCV数据显示卡片
    """
    # 计算日内涨跌（相对于开盘价，东方习惯：涨红跌绿）
    try:
        open_price = data.get('open', 0)
        close_price = data.get('close', 0)
        # 日内涨跌额 = 收盘价 - 开盘价
        intraday_change = close_price - open_price
        # 日内涨跌幅 = (收盘价 - 开盘价) / 开盘价 * 100%
        intraday_change_percent = (intraday_change / open_price * 100) if open_price != 0 else 0
        change_color = '#e74c3c' if intraday_change >= 0 else '#27ae60'  # 涨红跌绿
    except:
        intraday_change = 0
        intraday_change_percent = 0
        change_color = '#7f8c8d'
    
    return html.Div([
        html.H3(f"{symbol} - {date} OHLCV数据", 
                style={'color': '#2c3e50', 'marginBottom': '25px', 'textAlign': 'center'}),
        
        # OHLCV数据网格
        html.Div([
            # 第一行：开盘价和收盘价
            html.Div([
                html.Div([
                    html.H4("开盘价 (Open)", style={'color': '#34495e', 'marginBottom': '10px'}),
                    html.H2(f"${data.get('open', 0):.2f}", style={'color': '#3498db', 'margin': '0'})
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'width': '48%',
                    'display': 'inline-block',
                    'marginRight': '2%'
                }),
                html.Div([
                    html.H4("收盘价 (Close)", style={'color': '#34495e', 'marginBottom': '10px'}),
                    html.H2(f"${data.get('close', 0):.2f}", style={'color': change_color, 'margin': '0'})
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'width': '48%',
                    'display': 'inline-block'
                })
            ], style={'marginBottom': '15px'}),
            
            # 第二行：最高价和最低价
            html.Div([
                html.Div([
                    html.H4("最高价 (High)", style={'color': '#34495e', 'marginBottom': '10px'}),
                    html.H2(f"${data.get('high', 0):.2f}", style={'color': '#e74c3c', 'margin': '0'})  # 最高价用红色
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'width': '48%',
                    'display': 'inline-block',
                    'marginRight': '2%'
                }),
                html.Div([
                    html.H4("最低价 (Low)", style={'color': '#34495e', 'marginBottom': '10px'}),
                    html.H2(f"${data.get('low', 0):.2f}", style={'color': '#27ae60', 'margin': '0'})  # 最低价用绿色
                ], style={
                    'backgroundColor': '#ecf0f1',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'width': '48%',
                    'display': 'inline-block'
                })
            ], style={'marginBottom': '15px'}),
            
            # 第三行：成交量
            html.Div([
                html.H4("成交量 (Volume)", style={'color': '#34495e', 'marginBottom': '10px'}),
                html.H2(f"{data.get('volume', 0):,}", style={'color': '#9b59b6', 'margin': '0'})
            ], style={
                'backgroundColor': '#ecf0f1',
                'padding': '20px',
                'borderRadius': '8px',
                'textAlign': 'center',
                'marginBottom': '15px'
            }),
            
            # 日内涨跌信息
            html.Div([
                html.H4("日内涨跌信息", style={'color': '#34495e', 'marginBottom': '15px', 'textAlign': 'center'}),
                # 涨跌额和涨跌幅并排显示
                html.Div([
                    html.Div([
                        html.P("涨跌额", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0 0 5px 0'}),
                        html.P(f"{intraday_change:+.2f}", style={'fontSize': '18px', 'color': change_color, 'margin': '0', 'fontWeight': 'bold'})
                    ], style={
                        'width': '48%',
                        'display': 'inline-block',
                        'textAlign': 'center',
                        'marginRight': '2%'
                    }),
                    html.Div([
                        html.P("涨跌幅", style={'fontSize': '14px', 'color': '#7f8c8d', 'margin': '0 0 5px 0'}),
                        html.P(f"{intraday_change_percent:+.2f}%", style={'fontSize': '18px', 'color': change_color, 'margin': '0', 'fontWeight': 'bold'})
                    ], style={
                        'width': '48%',
                        'display': 'inline-block',
                        'textAlign': 'center'
                    })
                ])
            ], style={
                'backgroundColor': '#ecf0f1',
                'padding': '20px',
                'borderRadius': '8px'
            })
        ])
    ], style={
        'backgroundColor': 'white',
        'padding': '30px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'maxWidth': '800px',
        'margin': '0 auto'
    })


def create_error_card(error_message: str) -> html.Div:
    """
    创建错误信息卡片
    """
    return html.Div([
        html.H4("错误", style={'color': '#e74c3c', 'marginBottom': '15px'}),
        html.P(f"获取数据时发生错误: {error_message}", style={'color': '#e74c3c'}),
        html.P("请检查股票代码是否正确，或稍后重试。")
    ], style={
        'backgroundColor': '#fdf2f2',
        'padding': '20px',
        'borderRadius': '8px',
        'border': '1px solid #fecaca'
    })