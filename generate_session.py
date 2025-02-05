from pyrogram import Client

with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
    session_string = app.export_session_string()
    print(f"Ваша строка сессии: {session_string}")
    print(f"Ваша строка сессии: {app.session.dc_id}")
    print(f"Ваша строка сессии: {app.session.auth_key}")


# AgGvxY8ACjn082QqxdLzxdLBBPHKc6ZfqHgzWfar3_jaBJF6eDtz-gksHMYLfifSASUquCPjR5vNaeRRa2G4aUun0al7HY2sO7cRRyD2uJhPAO-FGBjcOpghlMmOs3_geA91vXIJy67MTFYfqf_KgBnCwzKLavzJ_wv3TEHrHA-GXzcH6WVcr9fZWSizfVhMZUQF1i7GmymqI_A8U9wfXwQkCzR_d8lRYuv4FRle6PLXQLO9XXxz5JmAR_9_IQwrziFJk5681-wKKKPazJQTiSWCuTUiHTs0GVj-kCWshYHi_L-34j4WyxawAiPx0zZtrMXQw4IO45fmCoW6rFWgjVWYmbR3OQAAAAFlqreqAA