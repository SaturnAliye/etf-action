import akshare as ak
import pandas as pd
import numpy as np
import json

# ===== 参数 =====
SYMBOL = "159915"
ATR_MAX = 0.035
BOLLW_MIN = 0.05
BOLLW_MAX = 0.20
BUY_SCORE = 70

def run_strategy():
    # ===== 1. ETF 日线 =====
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

    # ===== 显式锁定 T-1（核心）=====
    row = df.iloc[-2]

    # ===== 2. 指数（日线）=====
    sh = ak.stock_zh_index_daily(symbol="sh000001")[["date", "close"]]
    sz = ak.stock_zh_index_daily(symbol="sz399001")[["date", "close"]]
    sh["date"] = pd.to_datetime(sh["date"])
    sz["date"] = pd.to_datetime(sz["date"])
    sh["SH_R1"] = sh["close"].pct_change()
    sz["SZ_R1"] = sz["close"].pct_change()

    df = df.merge(sh[["date", "SH_R1"]], on="date", how="left")
    df = df.merge(sz[["date", "SZ_R1"]], on="date", how="left")

    row = df[df["date"] == row["date"]].iloc[0]

    # ===== 3. 技术指标 =====
    df["prev_close"] = df["close"].shift(1)
    df["TR"] = np.maximum(
        df["high"] - df["low"],
        np.maximum(
            abs(df["high"] - df["prev_close"]),
            abs(df["low"] - df["prev_close"])
        )
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

    r = df[df["date"] == row["date"]].iloc[0]

    # ===== 4. 过滤 + 打分 =====
    decision = "NO"
    total_score = 0

    if not (
        r["ATR_pct"] > ATR_MAX or
        r["BOLL_width"] < BOLLW_MIN or
        r["BOLL_width"] > BOLLW_MAX or
        r["MA20_slope"] <= 0
    ):
        score_boll = max(0, 100 - abs(r["BOLL_pos"] - 0.5) * 200)
        score_atr = 100 * (1 - r["ATR_pct"] / ATR_MAX)
        score_vol = min(100, r["VolRatio"] * 100)
        score_mkt = 50 + 25 * np.sign(r["SH_R1"] + r["SZ_R1"])

        total_score = (
            0.5 * score_boll +
            0.3 * score_atr +
            0.1 * score_vol +
            0.1 * score_mkt
        )

        if total_score >= BUY_SCORE:
            decision = "BUY"
        elif total_score >= 50:
            decision = "WATCH"

    # ===== 5. 周趋势 =====
    week_score = (
        (r["MA20_slope"] > 0) * 40 +
        (0.35 < r["BOLL_pos"] < 0.65) * 30 +
        (r["VolRatio"] >= 1.0) * 20 +
        ((r["SH_R1"] + r["SZ_R1"]) > 0) * 10
    )
    week_trend = "UP" if week_score >= 60 else "SIDE" if week_score >= 40 else "DOWN"

    return {
        "symbol": SYMBOL,
        "data_date": r["date"].strftime("%Y-%m-%d"),
        "predict_date": (r["date"] + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "close": round(r["close"], 3),
        "ATR_pct": round(r["ATR_pct"] * 100, 2),
        "BOLL_width": round(r["BOLL_width"], 2),
        "BOLL_pos": round(r["BOLL_pos"], 2),
        "MA20_slope": round(r["MA20_slope"], 4),
        "VolRatio": round(r["VolRatio"], 2),
        "score": round(total_score, 1),
        "decision": decision,
        "week_trend": week_trend
    }

if __name__ == "__main__":
    result = run_strategy()
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)



