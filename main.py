import json
import smtplib
from email.mime.text import MIMEText

with open("result.json", "r", encoding="utf-8") as f:
    r = json.load(f)

html = f"""
<h3>📊 创业板ETF（{r['symbol']}）T-1 决策</h3>
<table border="1" cellpadding="6" cellspacing="0">
<tr><td>日期</td><td>{r['date']}</td></tr>
<tr><td>收盘价</td><td>{r['close']}</td></tr>
<tr><td>ATR%</td><td>{r['ATR_pct']}%</td></tr>
<tr><td>BOLL宽度</td><td>{r['BOLL_width']}</td></tr>
<tr><td>BOLL位置</td><td>{r['BOLL_pos']}</td></tr>
<tr><td>MA20斜率</td><td>{r['MA20_slope']}</td></tr>
<tr><td>量能比</td><td>{r['VolRatio']}</td></tr>
<tr><td><b>明日评分</b></td><td><b>{r['score']}</b></td></tr>
<tr><td><b>明日结论</b></td><td><b>{r['decision']}</b></td></tr>
<tr><td><b>未来一周</b></td><td><b>{r['week_trend']}</b></td></tr>
</table>
"""

msg = MIMEText(html, "html", "utf-8")
msg["Subject"] = "📊 创业板ETF T-1 决策日报"
msg["From"] = "YOUR_EMAIL"
msg["To"] = "TO_EMAIL"
msg["Cc"] = "CC_EMAIL"

smtp = smtplib.SMTP_SSL("smtp.qq.com", 465)
smtp.login("YOUR_EMAIL", "SMTP_AUTH_CODE")
smtp.send_message(msg)
smtp.quit()
