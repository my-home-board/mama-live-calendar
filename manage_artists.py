
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

FILE = Path(__file__).resolve().parent / "artists.json"

action = os.environ["ACTION"].strip()
artist_id = os.environ["ARTIST_ID"].strip()
name = os.environ.get("ARTIST_NAME", "").strip()
url = os.environ.get("SCHEDULE_URL", "").strip()

if not re.fullmatch(r"[a-z0-9_-]+", artist_id):
    raise ValueError("IDは半角英小文字・数字・_・-のみ使用できます")

artists = json.loads(FILE.read_text(encoding="utf-8"))

if not isinstance(artists, list):
    raise ValueError("artists.json must contain a list")

matches = [a for a in artists if a["id"] == artist_id]

if len(matches) > 1:
    raise ValueError("同じIDが複数登録されています")

artist = matches[0] if matches else None

if action == "add":
    if artist:
        raise ValueError("このIDはすでに登録されています")

    if not name or not url:
        raise ValueError("追加時は名前とURLが必要です")

    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("有効なHTTPS URLを入力してください")

    # 現在の取得プログラムはFanpla形式のみ対応
    if not parsed.hostname.endswith(".fanpla.jp"):
        raise ValueError("現在はFanplaの公式サイトのみ登録できます")

    if parsed.path.rstrip("/") != "/live_information/schedule/list":
        raise ValueError("Fanplaのライブ一覧URLを指定してください")

    artists.append({
        "id": artist_id,
        "name": name,
        "enabled": False,
        "source": "fanpla_schedule",
        "url": url.split("?")[0].rstrip("/") + "/"
    })

elif action == "disable":
    if not artist:
        raise ValueError("指定したアーティストが見つかりません")
    artist["enabled"] = False

elif action == "enable":
    if not artist:
        raise ValueError("指定したアーティストが見つかりません")
    artist["enabled"] = True

elif action == "delete":
    if not artist:
        raise ValueError("指定したアーティストが見つかりません")
    artists = [a for a in artists if a["id"] != artist_id]

else:
    raise ValueError("不明な操作です")

FILE.write_text(
    json.dumps(artists, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print(f"Completed: {action} / {artist_id}")
