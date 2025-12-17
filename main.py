import akshare as ak
import pandas as pd
import numpy as np
import json

ATR_MAX = 0.035
BOLLW_MIN = 0.05
BOLLW_MAX = 0.20
BUY_SCORE = 70
SYMBOL = "159915"

def run_strategy():
    df = ak.fund_etf_hist_em(symbol=SYMBOL, period="daily", adjust="")
    df = df.rename(columns={
        "日期": "date",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume"
    })
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["prev_close"] = df["close"].shift(1)
    df["TR"] = np.maximum(
        df["high"] - df["low"],
        np.maximum(abs(df["high"] - df["prev_close"]),
                   abs(df["low"] - df["prev_close"]))
    )
    df["ATR20"] = df["TR"].rolling(20).mean()
    df["ATR_pct"] = df["ATR20"] / df["close"]

    df["MA20"] = df["close"].rolling(20).mean()
    df["MA20_slope"] = df["MA20"] - df["MA20"].shift(5)

    df["STD20"] = df["close"].rolling(20).std()
    df["UB"] = df["MA20"] + 2 * df["STD20"]
    df["LB"] = df["MA20"] - 2 * df["STD20"]
    df["BOLL_width"] = (df["UB"] - df["LB"]) / df["MA20"]
    df["BOLL_pos"] = (df["close"] - df["LB"]) / (df["UB"] - df["LB"])

    df["VolMA20"] = df["volume"].rolling(20).mean()
    df["VolRatio"] = df["volume"] / df["VolMA20"]

    r = df.iloc[-1]

    score = 50
    decision = "WATCH"
    if (
        r["ATR_pct"] <= ATR_MAX and
        BOLLW_MIN <= r["BOLL_width"] <= BOLLW_MAX and
        r["MA20_slope"] > 0
    ):
        score = 75
        decision = "BUY"

    return {
        "symbol": SYMBOL,
        "date": r["date"].strftime("%Y-%m-%d"),
        "close": round(r["close"], 3),
        "ATR_pct": round(r["ATR_pct"] * 100, 2),
        "BOLL_width": round(r["BOLL_width"], 2),
        "BOLL_pos": round(r["BOLL_pos"], 2),
        "MA20_slope": round(r["MA20_slope"], 4),
        "VolRatio": round(r["VolRatio"], 2),
        "score": score,
        "decision": decision,
        "week_trend": "UP" if r["MA20_slope"] > 0 else "SIDE"
    }

if __name__ == "__main__":
    result = run_strategy()
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("result.json written")

