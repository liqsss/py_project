import tushare as ts  # https://www.tushare.pro/
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

pro = ts.pro_api('3ef62fda3b6929541a9fbffd853d5f5a164d3b35fd20b7e413774099')

df = pro.daily(**{
	"ts_code": "600518.SH",
	"trade_date": "",
	"start_date": "",
	"end_date": "",
	"offset": "",
	"limit": 500
}, fields=[
	"ts_code",
	"trade_date",
	"close",
	"change",
	"pct_chg",
	"vol",
	"amount"
])

sz = pro.daily(**{
	"ts_code": "000001.SZ",
	"trade_date": "",
	"start_date": "",
	"end_date": "",
	"offset": "",
	"limit": 10
}, fields=[
	"ts_code",
	"trade_date",
	"close",
	"change",
	"pct_chg",
	"vol",
	"amount"
])

plt.plot(df.index, df['close'], label="Line 1")
plt.yscale('linear')
#plt.plot(df['trade_date'], df['close'], label="Line 1")
plt.legend()
plt.show()



