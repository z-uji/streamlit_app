import streamlit as st
import altair as alt
import pandas as pd
import yfinance as yf

@st.cache
def get_stock_prices_data(days, tickers):
    """
    株価データ取得処理.

    :param int days: データ取得期間
    :param dict tickers: 取得するティッカーの辞書
    :return DataFrame df テーブルデータ
    """
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')           # 表示期間中の株価を取得
        hist.index = hist.index.strftime('%Y %B %d')    # 年月日の表示形式設定
        hist = hist[['Close']]                          # 終値のみ取得するように設定
        hist.columns = [company]                        # カラム名に会社名を表示するように設定
        hist = hist.T                                   # 行と列の入れ替え
        hist.index.name = 'Name'                        # インデックスに'Name'を設定
        df = pd.concat([df, hist])
    return df

def show_chart(data):
    """
    株価のデータを整形してグラフ化して表示.

    :param data テーブルデータ
    """
    # データ整形
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices (USD)'}
    )
    # グラフ出力
    chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True)
        .encode(
            x="Date:T",
            y=alt.Y("Stock Prices (USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
            color='Name:N'
        )
    )
    st.altair_chart(chart, use_container_width=True)
    return

def add_tickers(lavel, ticker):
    """
    株価を表示する会社を追加.

    :param string lavel: 追加する会社の表示名
    :param string ticker: 追加する会社のticker
    """
    if ticker == "" or lavel == "":
        if ticker == "":
            st.error("ティッカーが未入力です")

        if lavel == "":
            st.error("ティッカーの表示ラベルが未入力です")

        return

    if lavel in tickers:
        st.error("入力されたティッカーは既に設定されています")
        return
    else:
        tickers[lavel]=ticker
        st.write("追加完了！")
        st.write(tickers)

    return


# ここから下がアプリのメイン処理

tickers = {
        'Amazon': 'AMZN',
        'Apple': 'AAPL',
        'COSTCO': 'COST',
        'FaceBook': 'FB',
        'Google': 'GOOGL',
        'Microsoft':'MSFT',
        'Netflix': 'NFLX',
        'Twitter':'TWTR',
        'Walmart':'WMT',
    }

#サイドバー表示

st.sidebar.write("""
## 設定
""")
# 表示期間
st.sidebar.write("""
### 表示する期間の指定
下のバーを操作すると、グラフに表示する期間を変更できます。
最大表示期間は60日です。
""")
days = st.sidebar.slider('表示期間(日)', min_value=0, max_value=60, value=30)

# 株価の範囲
st.sidebar.write("""
### 表示する株価の範囲の指定
下のバーを操作すると、グラフに表示する株価の範囲を変更できます。
""")
ymin, ymax = st.sidebar.slider(
    '株価範囲(USD)',
    0.0, 3500.0,(0.0, 3500.0)
)


#メインページ表示
# タイトル
st.title('米国株価可視化アプリ')

# 見出し
st.write("""
こちらは米国株価可視化アプリです。\n
サイドバーより、表示する期間と株価の範囲を設定できます。\n
プルダウンメニューから選択した米国企業の株価を表とグラフで表示します。
""")

# 項目名
st.write(f"""
### 過去 **{days}日間** の米国株価（終値）
""")

# 株価のテーブルデータ
df = get_stock_prices_data(days, tickers)

# 複数選択ウィジェットの設定
companies = st.multiselect(
    '表示する会社名を選択してください。',
    list(df.index),
    ['Google', 'Apple']
)


if not companies:
    # 表示する会社が指定されていない場合はエラーメッセージを表示
    st.error("表示する会社を少なくとも1社は選択してください")
else:
    # 表示するデータの指定（選択された会社の株価を表示）
    data = df.loc[companies]
    # テーブルを表示
    st.write("### 株価 (USD)", data.sort_index())
    # グラフを表示
    show_chart(data)
