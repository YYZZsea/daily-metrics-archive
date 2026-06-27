# Exit Risk Inputs

这里放持仓卖点提醒的统一输入，只记录“买了哪些股票”，不记录数量、成本、金额或账户信息。

## 目录

```text
inputs/exit-risk/
  tickers.csv
```

## tickers.csv 格式

```csv
ticker,name,category,notes
MRVL,Marvell Technology,stock,
MU,Micron Technology,stock,
```

字段说明：

- `ticker`: 必填，美股代码。
- `name`: 可选，公司名。
- `category`: 可选，常用 `stock`、`etf`、`option_proxy`。
- `notes`: 可选，只写非敏感备注。

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
