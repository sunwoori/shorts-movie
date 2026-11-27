"""publish/*.json 게시 요청을 읽어 유튜브에 영상을 올린다.

게시 요청 형식 (publish/2026-11-28.json):
{
  "video": "videos/issue_2026-11-28.mp4",
  "title": "오늘자 이슈 11월 28일",
  "description": "설명 #Shorts",
  "tags": ["오늘자이슈"],
  "privacy": "public"            # public | unlisted | private
}

필요한 환경 변수(GitHub Secrets): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
import json
import os
import pathlib
import subprocess
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = pathlib.Path(__file__).resolve().parent.parent


def added_requests():
    """직전 커밋에서 새로 추가된 게시 요청 파일만 고른다(수정·삭제는 무시)."""
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD", "--", "publish/"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p.endswith(".json")]


def load(path):
    req = json.loads((ROOT / path).read_text(encoding="utf-8"))
    video = (ROOT / req["video"]).resolve()
    if ROOT / "videos" not in video.parents or not video.is_file():
        raise SystemExit(f"{path}: video는 videos/ 폴더 안의 파일이어야 합니다: {req['video']}")
    privacy = req.get("privacy", "private")
    if privacy not in ("public", "unlisted", "private"):
        raise SystemExit(f"{path}: privacy 값이 잘못되었습니다: {privacy}")
    title = str(req["title"]).strip()
    if not title or len(title) > 100:
        raise SystemExit(f"{path}: title은 1~100자여야 합니다")
    return video, title, str(req.get("description", "")), list(req.get("tags", [])), privacy


def main():
    paths = sys.argv[1:] or added_requests()
    if not paths:
        print("새 게시 요청이 없습니다.")
        return
    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    summary = []
    for path in paths:
        video, title, description, tags, privacy = load(path)
        body = {
            "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        }
        req = yt.videos().insert(
            part="snippet,status", body=body,
            media_body=MediaFileUpload(str(video), mimetype="video/mp4", resumable=True))
        resp = None
        while resp is None:
            _, resp = req.next_chunk()
        status = resp.get("status", {}).get("privacyStatus")
        line = f"{path} -> https://youtu.be/{resp['id']} (요청: {privacy}, 실제: {status})"
        print(line)
        summary.append(line)
    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write("\n".join(f"- {s}" for s in summary) + "\n")


if __name__ == "__main__":
    main()
