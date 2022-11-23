import re
from datetime import datetime
from colorsys import rgb_to_hls, hls_to_rgb
from typing import List, Tuple
import pandas as pd
import plotly.graph_objs as go

from grackle.model import TableTransactionSplit


class ChartPrep:
    """Tools to transform data for charting purposes"""
    BLUE = (31, 119, 180)
    CYAN = (23, 190, 207)
    ORANGE = (255, 127, 14)
    YELLOW = (189, 163, 34)
    GREEN = (44, 160, 44)
    RED = (214, 39, 40)
    BROWN = (140, 86, 75)
    PURPLE = (148, 103, 189)
    PINK = (227, 119, 194)
    GREY = (127, 127, 127)

    DEFAULT_COLORS = [
        BLUE, ORANGE, GREEN, RED, PURPLE, BROWN, PINK, GREY, YELLOW, CYAN
    ]

    TEMPLATE = '%{y:,.0f}'

    @classmethod
    def rgb_to_str(cls, rgb: Tuple[float, float, float]) -> str:
        return f'rgb({", ".join([str(x) for x in rgb])})'

    @classmethod
    def str_to_rgb(cls, rgb_str: str) -> Tuple[float, float, float]:
        r, g, b = [float(x) for x in re.findall(r'\d+', rgb_str)]
        return r, g, b

    @classmethod
    def adjust_color(cls, orig_rgb: Tuple[float, float, float], is_lighten: bool = True, factor: float = 0.1) -> \
            Tuple[float, float, float]:
        """Adjusts an RGB color to be lighter/darker than the original value"""
        if is_lighten:
            factor = 1 + factor
        else:
            factor = 1 - factor

        r, g, b = (x / 255.0 for x in orig_rgb)
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = (x * 255 for x in hls_to_rgb(h, l, s))
        return r, g, b

    @staticmethod
    def filter_dates(df: pd.DataFrame, start: datetime, end: datetime = None) -> pd.DataFrame:
        if end is not None:
            # Start and end date
            date_mask = (df['date'] >= start) & (df['date'] <= end)
        else:
            date_mask = (df['date'] >= start)
        return df.loc[date_mask]

    @staticmethod
    def get_balances(transactions: List[TableTransactionSplit], split_future: bool = False) -> pd.DataFrame:
        """Retrieves an account's daily balance
        """

        df = pd.DataFrame()
        t: TableTransactionSplit
        for t in transactions:
            df = pd.concat([df, pd.DataFrame({
                'name': t.account.name,
                'fullname': t.account.full_name,
                'date': t.transaction.transaction_date,
                'value': t.amount
            }, index=[0])], ignore_index=True)
        # Group by date, summing the values
        result_df = df.groupby(['fullname', 'name', 'date'], as_index=False).agg({'value': 'sum'}) \
            .sort_values(['fullname', 'name', 'date'], ascending=True)
        result_df = result_df.pivot(values='value', index='date', columns='name').fillna(0).cumsum().reset_index()
        if split_future:
            # Isolate the entries from today onward
            # Find row that's the last one before today's date. This helps the graph look more seamless
            last_before_today_idx = result_df['date'].loc[
                result_df['date'].dt.date < datetime.now().date()].idxmax()
            future = result_df.iloc[last_before_today_idx:]
            result_df = pd.merge(result_df, result_df.iloc[last_before_today_idx:],
                                 how='left', on='date', suffixes=('', '_future'))
            result_df.loc[future.index[1:], future.columns[1:]] = None
            return result_df
        return result_df

    @classmethod
    def plot_timeseries(cls, df: pd.DataFrame, n_days_ma: int = None, as_area: bool = False) -> go.Figure:
        """Plots a timeseries from a dataframe where the first column is assumed to be dates and
            the other columns are accounts or other ways of grouping data.
        If an column name ends in '_future', an attempt will be made to associate it with
            a related column lacking that suffix."""

        all_acct_cols = df.columns.tolist()[1:]
        historical_cols = [x for x in all_acct_cols if '_future' not in x]
        # current and future column mapping

        fig = go.Figure()
        for i, col in enumerate(df.columns.tolist()[1:]):
            if col in historical_cols:
                # This is past data
                color = cls.DEFAULT_COLORS[historical_cols.index(col)]
                line = dict(color=cls.rgb_to_str(color), width=2)
            else:
                # Likely future data. Look up the color for the account minus '_future'
                color = cls.DEFAULT_COLORS[historical_cols.index(col.replace('_future', ''))]
                line = dict(color=cls.rgb_to_str(color), width=2, dash='dot')
            if as_area:
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df[col], name=col, mode='lines+markers', line=line,
                               marker=dict(size=5), hoverinfo='name+x+y', stackgroup='one', hoveron='points',
                               hovertemplate=cls.TEMPLATE)
                )
            else:
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df[col], name=col, mode='lines+markers', line=line,
                               marker=dict(size=5), hovertemplate=cls.TEMPLATE)
                )
            if '_future' not in col and not as_area:
                if n_days_ma is not None:
                    # Add n-day moving average to the plot
                    color = cls.adjust_color(cls.DEFAULT_COLORS[historical_cols.index(col)], factor=0.1)
                    line = dict(color=cls.rgb_to_str(color), width=2, dash='dash')
                    fig.add_trace(
                        go.Scatter(x=df['date'], y=df[col].rolling(n_days_ma).mean(), name=f'{col}-ma',
                                   mode='lines', line=line, hovertemplate=cls.TEMPLATE)
                    )

        return fig

    @classmethod
    def get_monthly_activity(cls, transactions: List, acct_filter: str = None) -> pd.DataFrame:
        """Gets all transactions for budget analysis"""
        if acct_filter is None:
            acct_filter = r'.*'
        df = pd.DataFrame()
        for row in transactions:
            if re.match(acct_filter, row.account.full_name) is None:
                continue
            # Load data into dataframe
            df = pd.concat([df, pd.DataFrame({
                'date': row.transaction.transaction_date,
                'type': row.account.account_type.name,
                'account': row.account.name,
                'amt': row.amount,
                'cur': row.account.account_currency.name,
            }, index=[0])], ignore_index=True)
        # Group by month, year
        df = df.set_index('date')
        grouped = df.groupby([pd.Grouper(freq='M'), 'cur', 'account']).sum().reset_index()
        return grouped
