# shorts-movie

매일 만드는 카드뉴스 쇼츠 영상 보관용 저장소입니다.

- `videos/` : 날짜별 mp4
- `publish/` : 게시 요청(json). 새 파일이 추가되면 GitHub Actions가 해당 영상을 유튜브에 올립니다.
- `tools/upload_youtube.py` : 업로드 스크립트

인증 값(클라이언트 ID·비밀, 갱신 토큰)은 저장소 Secrets에만 두고 파일로 올리지 않습니다.
