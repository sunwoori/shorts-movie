# publish

유튜브 게시 요청 파일(`YYYY-MM-DD.json`)을 두는 폴더입니다.

- 새 `.json` 파일이 추가되면 GitHub Actions가 `video` 항목의 영상을 유튜브에 올립니다.
- 수정·삭제 커밋은 업로드를 일으키지 않고, `.md` 같은 다른 파일도 무시됩니다.
- 형식: `{"video": "videos/issue_YYYY-MM-DD.mp4", "title": "...", "description": "... #Shorts ...", "tags": ["..."], "privacy": "public"}`
- 업로드가 끝나면 게시 요청 파일은 삭제하므로 평소에는 이 README만 남습니다.
