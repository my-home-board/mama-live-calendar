
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

TZ = ZoneInfo("Asia/Tokyo")
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; PersonalCalendarBot/1.0)"
})


def get_soup(url):
    response = SESSION.get(url, timeout=25)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def fetch_nightmare(artist):
    today = datetime.now(TZ).date()
    events = []
    seen = set()

    # 現在月から12か月先まで確認する
    for offset in range(13):
        year = today.year + (today.month - 1 + offset) // 12
        month = (today.month - 1 + offset) % 12 + 1

        
        month_url = (
            f"https://nightmare-web.com/schedule/list/"
            f"{year}/{month}/"
            "?cat=L_ALL,live02,live03,live04,live05,live06,live07,live08"
        )

        response = SESSION.get(
            month_url,
            timeout=25
        )

        response.raise_for_status()
        listing = BeautifulSoup(response.text, "html.parser")

        for link in listing.select('a[href*="/schedule/detail/"]'):
            detail_url = urljoin(artist["url"], link.get("href", ""))

            if detail_url in seen:
                continue
            seen.add(detail_url)

            
            # TOURとEVENTを取得対象にする
            label = link.get_text(" ", strip=True)
            if not re.search(r"\b(TOUR|EVENT)\b", label, re.I):
                continue


            detail = get_soup(detail_url)
            text = detail.get_text("\n", strip=True)

            date_match = re.search(
                r"(\d{4})\.(\d{1,2})\.(\d{1,2})",
                text
            )
            if not date_match:
                raise ValueError(f"公演日を取得できません: {detail_url}")

            show_date = date(*map(int, date_match.groups()))
            if show_date < today:
                continue

           
            # 一覧ページから公演タイトルを取得
            title = link.get_text(" ", strip=True)

            # 先頭の分類表示（TOUR / EVENT）を削除
            title = re.sub(
                r"^(?:TOUR|EVENT)\s+",
                "",
                title,
                flags=re.I
            ).strip()

            # 【NIGHTMARE】を付けるため、
            # タイトル先頭の重複するNIGHTMAREを削除
            title = re.sub(
                r"^NIGHTMARE\s+",
                "",
                title,
                flags=re.I
            ).strip()

            # リリースイベント以降の案内文を削除
            # 「リリースイベント」という名称は残す
           
            # リリースイベントの後ろにある時間・会場案内を削除
            if "リリースイベント" in title:
                title = re.sub(
                    r"(リリースイベント).*",
                    r"\1",
                    title
                ).strip()


            if not title:
                title = "LIVE"
                
            print(f"TITLE CHECK: {detail_url} -> {title!r}")



            time_match = re.search(
                r"OPEN\s*(\d{1,2}:\d{2})\s*/\s*"
                r"START\s*(\d{1,2}:\d{2})",
                text,
                re.I
            )

            if time_match:
                start_time = datetime.strptime(
                    time_match.group(2), "%H:%M"
                ).time()
                start = datetime.combine(show_date, start_time, TZ)
                end = start + timedelta(hours=3)
                hours = time_match.group(0)
            else:
                start = show_date
                end = show_date + timedelta(days=1)
                hours = "未掲載"

            
            
            # 公演日が記載された行から会場名を取得
            venue_match = re.search(
                r"\d{4}年\d{1,2}月\d{1,2}日"
                r"\s*[（(][^）)]+[）)]"
                r"\s*([^\n]+)",
                text
            )

            if venue_match:
                venue_text = venue_match.group(1).strip()
                # 都道府県名の後ろの「・」を除去
                location = venue_text.split("・", 1)[-1].strip()
            else:
                location = ""



            event_id = detail_url.rstrip("/").split("/")[-1]

            events.append({
                "uid": f'{artist["id"]}-{event_id}@live-calendar',
                "title": f'【{artist["name"]}】{title}',
                "start": start,
                "end": end,
                "location": location,
                "description": (
                    f"公式情報: {detail_url}\n"
                    f"開場/開演: {hours}\n"
                    "※終了時刻は未公表のため仮に3時間枠で表示"
                    "（時間未掲載なら終日）"
                ),
                "url": detail_url
            })

            print(f"EVENT CHECK: {events[-1]['title']!r}")

    print(f'NIGHTMARE: {len(events)} events')
    return events
