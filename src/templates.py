# monitoring case #1
CASE_1_NORMAL_TITLE = "【正常】CO2（二酸化炭素） 濃度"
CASE_1_NORMAL_CONTENT = "お部屋のCO2濃度は正常です。"

CASE_1_WARNING_TITLE = "【注意】CO2（二酸化炭素） 濃度"
CASE_1_WARNING_CONTENT = """お部屋のCO2濃度が高い状態（1,500ppm以上）です。換気をしてください。室内のCO2濃度を1,000 ppm以下に保つことが推奨されています。

CO2（二酸化炭素）濃度：{value:,} ppm"""

CASE_1_ABNORMAL_TITLE = "【警告】CO2（二酸化炭素） 濃度"
CASE_1_ABNORMAL_CONTENT = """お部屋のCO2濃度が非常に高い状態（3,000ppm以上）です。すぐに換気をしてください。室内のCO2濃度を1,000ppm以下に保つことが推奨されています。

CO2（二酸化炭素）濃度：{value:,} ppm"""

# monitoring case #2
CASE_2_NORMAL_TITLE = "【正常】温度"
CASE_2_NORMAL_CONTENT = "お部屋の温度は正常です。"

CASE_2_WARNING_TITLE = "【注意】温度"
CASE_2_WARNING_CONTENT = """お部屋の温度が高い状態（35℃以上）です。注意してください。

温度：{value}℃"""

CASE_2_ABNORMAL_TITLE = "【警告】温度"
CASE_2_ABNORMAL_CONTENT = """お部屋の温度が非常に高い（50℃以上）危険な状態です。お部屋を確認してください。

温度：{value}℃"""

# monitoring case #3
CASE_3_NORMAL_TITLE = "【正常】熱中症アラート"
CASE_3_NORMAL_CONTENT = """お部屋は正常です。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

CASE_3_WARNING_TITLE = "【注意】熱中症アラート"
CASE_3_WARNING_CONTENT = """お部屋は熱中症になりやすい状態です。夏場は、室温28℃以下、湿度50～60%を目安に、お部屋を快適な状態に保ってください。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

CASE_3_ABNORMAL_TITLE = "【警告】熱中症アラート"
CASE_3_ABNORMAL_CONTENT = """お部屋は熱中症になりやすい危険な状態です。扇風機やエアコンを使用して、お部屋の温度を下げてください。夏場は、室内を温度28℃以下、湿度50～60%に保つことが推奨されています。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

# monitoring case #4
CASE_4_NORMAL_TITLE = "【正常】インフルエンザ対策"
CASE_4_NORMAL_CONTENT = """お部屋の状態は正常です。

温度：{temp}℃
湿度：{humid}%"""

CASE_4_WARNING_TITLE = "【警告】インフルエンザ対策"
CASE_4_WARNING_CONTENT = """お部屋が乾燥し、インフルエンザになりやすい状態です。冬場は、室内を温度18～25℃、湿度40～60％に保つことが推奨されています。

温度：{temp}℃
湿度：{humid}%"""

# monitoring case #5
CASE_5_NORMAL_TITLE = "【正常】長期不在"
CASE_5_NORMAL_CONTENT = """お部屋の状態は正常です。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

CASE_5_ABNORMAL_TITLE = "【異常】長期不在"
CASE_5_ABNORMAL_CONTENT = """{setting_time}時間以上、お部屋のCO2濃度に変化がありません。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

# monitoring case #6
CASE_6_NORMAL_TITLE = "【正常】長期不通"
CASE_6_NORMAL_CONTENT = """デナリ・ボッツは正常に稼働しています。

CO2：{co2:,} ppm
温度：{temp}℃
湿度：{humid}%"""

CASE_6_WARNING_TITLE = "【警告】長期不通"
CASE_6_WARNING_CONTENT = "デナリ・ボッツが正しく動いていない可能性があります。電源が入っているか確認してください。"

CASE_6_ABNORMAL_TITLE = "【異常】長期不通"
CASE_6_ABNORMAL_CONTENT = "デナリ・ボッツが24時間以上動いていません。電源が入っているか確認してください。"
# monitoring case #7
CASE_7_ABNORMAL_TITLE = "【異常】侵入者の疑い"
CASE_7_ABNORMAL_CONTENT = "不在設定されているお部屋のCO2濃度が大きく上昇しました。お部屋の状態を確認してください。"

# EMAIL
RECOVER_EMAIL_TEMPLATE = """{email}　様

デナリ・ボッツの正常を検知しましたのでお知らせします。

通知ID：{device_monitor_id}
デバイス名：{device_name}
デバイス IMEI：{imei}
正常検知日時：{occurred_at} JST
(正常と判断した日時です)

{content}

正常検知の判断基準については、以下をご確認ください。
https://www.denaribots.com/faq

※このメールは送信専用アドレスからお送りしています。ご返信いただいても回答はできませんので、あらかじめご了承ください。

デナリ・ボッツ管理ページ
https://www.denaribots.com/contact"""

ABNORMAL_EMAIL_TEMPLATE = """{email}　様

デナリ・ボッツの異常を検知しましたのでお知らせします。

通知ID：{device_monitor_id}
デバイス名：{device_name}
デバイス IMEI：{imei}
異常検知日時：{occurred_at} JST
(異常と判断した日時です)

{content}

異常検知の判断基準については、以下をご確認ください。
https://www.denaribots.com/faq

※このメールは送信専用アドレスからお送りしています。ご返信いただいても回答はできませんので、あらかじめご了承ください。

デナリ・ボッツ管理ページ
https://www.denaribots.com/contact"""

EMAIL_TITLE_MAPPING = {
    # "{monitor_case}:{monitor_status}": "title"
    "1:1": "【デナリ・ボッツ】CO2（二酸化炭素） 濃度 正常",
    "1:3": "【デナリ・ボッツ】CO2（二酸化炭素） 濃度 警告検知のお知らせ",
    "2:1": "【デナリ・ボッツ】温度 正常",
    "2:3": "【デナリ・ボッツ】温度 警告検知のお知らせ",
    "3:1": "【デナリ・ボッツ】熱中症 正常",
    "3:3": "【デナリ・ボッツ】熱中症 警告検知のお知らせ",
    "5:1": "【デナリ・ボッツ】長期不在 正常",
    "5:3": "【デナリ・ボッツ】長期不在 異常",
    "6:1": "【デナリ・ボッツ】長期不通 正常",
    "6:3": "【デナリ・ボッツ】長期不通 異常",
    "7:3": "【デナリ・ボッツ】侵入者の疑い 異常",
}
