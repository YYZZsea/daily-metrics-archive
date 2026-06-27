# Exit Risk Inputs

这里放持仓卖点提醒的统一输入，只记录“买了哪些股票”，不记录数量、成本、金额或账户信息。

## 目录

```text
inputs/exit-risk/
  tickers.txt
```

## tickers.txt 格式

一行一只股票，第二列可选买入/观察日期：

```text
MRVL 2026-06-20
MU 2026-06-24
HOOD
```

字段说明：

- `ticker`: 必填，美股代码。
- `buy_date`: 可选，格式建议 `YYYY-MM-DD`。如果写了，会用当日或之后第一个交易日收盘价估算买入/观察收益。
- `notes`: 可选，可以用空格接在日期后面，只写非敏感备注。

也可以继续用 `tickers.csv`，格式为：

```csv
ticker,name,category,buy_date,notes
MRVL,Marvell Technology,stock,2026-06-20,
MU,Micron Technology,stock,2026-06-24,
```

不要放：

- 持仓数量
- 买入成本
- 市值
- 账户名
- Robinhood/Yahoo 账号信息

输出统一写到：

```text
latest/exit-risk/
```

研究与教育用途，不构成投资建议。
