import tushare as ts

pro = ts.pro_api('3ef62fda3b6929541a9fbffd853d5f5a164d3b35fd20b7e413774099')

df = pro.daily(**{
	"ts_code": "600518.SH",
	"trade_date": "",
	"start_date": "",
	"end_date": "",
	"offset": "",
	"limit": 1
}, fields=[
	"ts_code",
	"trade_date",
	"close",
	"change",
	"pct_chg",
	"vol",
	"amount"
])
print(df)


