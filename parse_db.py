import pandas as pd
from datetime import datetime, timedelta
import asyncio

from database.req import add_target


async def main() -> None:
    file_path = "user2.xlsx"
    df = pd.read_excel(file_path)
    df = df[df["Последняя активность (UTC)"] != "Более недели назад"]
    df["Последняя активность (UTC)"] = pd.to_datetime(df["Последняя активность (UTC)"], errors="coerce")
    two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
    filtered_df = df[(df["Последняя активность (UTC)"].isna()) | (df["Последняя активность (UTC)"] > two_weeks_ago)]
    data = filtered_df.to_dict(orient="records")
    for row in data:
        await add_target(row['Username'], 483458201)

if __name__ == '__main__':
    asyncio.run(main())
