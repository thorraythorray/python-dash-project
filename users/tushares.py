import tushare as ts    
from functools import partial
import pandas

class TushareApi:
    
    def __init__(self):
        self.pro = ts.pro_api('7ac9297d197575159fca742713005757987ec369fca94e5464638365')

    def execute(self, api_name, *args, **kwargs):
        func = getattr(self.pro, api_name)
        dataframe = func(*args, **kwargs)
        return dataframe

    def __getattr__(self, name):
        return partial(self.execute, name)


class TushareData:

    @staticmethod
    def get_shares_basic():
        dataframe = TushareApi().stock_basic(date="2020-12-01", fields='ts_code,symbol,name,area,industry,market,list_status,list_date')
        dataframe["list_status"] = dataframe["list_status"].map(lambda list_status: "上市" if list_status == "L" else "退市")
        header = ["TS代码", "股票代码", "股票名称", "地域", "所属行业", "市场类型", "上市状态", "上市日期"]
        new_column = {}
        for index, item in enumerate(dataframe.columns.tolist()):
            new_column.update({item: header[index]})
        dataframe.rename(columns=new_column, inplace=True)
        return dataframe
    
    @staticmethod
    def get_K_data(type, ts_code):
        assert type in ["daily", "weekly", "monthly"]
        k_func = getattr(TushareApi(), type)
        k_map = {
            "daily": "20200101",
            "weekly": "20150101",
            "monthly": "20100101"
            }
        dataframe = k_func(ts_code=ts_code, start_date=k_map[type])
        dataframe["trade_date"] = dataframe["trade_date"].map(lambda trade_date: trade_date[:4] + "-" + trade_date[4:6] + "-" + trade_date[6:8])

        return dataframe


    @staticmethod
    def test_get_share_info():
        return TushareApi().stock_basic(date="2020-12-01", fields='symbol,name,area,industry,market,list_status,list_date,ts_code')
    



    
if __name__ == "__main__":
    dataframe = TushareData.get_K_data("daily", "600000.SH")
    
    # dataframe = dataframe.loc[dataframe["TS代码"].eq("600000.SH")]
    # print("dataframe", dataframe)
    # dataframe = dataframe.iloc[0, :].tolist()
    # dataframe=dataframe[1:6] + dataframe[7:9]
    # print(dataframe)

    dataframe = TushareData.get_shares_basic()
    query_dff = dataframe.loc[dataframe["TS代码"].eq("600000.SH")].iloc[0, 2]
    print(query_dff)

    # dataframe = list(map(str, dataframe))
    # print(dataframe)
    # a=(",".join(dataframe[1:6] + dataframe[7:9]))
    # print(a)
    # print("{}今日成交  开盘：{}  收盘：{}  最高：{}  最低：{} 跌涨额：{}  跌涨幅：{}".format(*dataframe))
    
    # dataframe = TushareData.get_shares_basic()
    # print(dataframe)
    
        