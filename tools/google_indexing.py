#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구글 Indexing API 일괄 통보(선택) — 구글은 IndexNow에 참여하지 않습니다.

중요:
- 구글 Indexing API는 공식적으로 JobPosting / BroadcastEvent(라이브) 페이지용입니다.
  일반 페이지는 정책상 대상이 아니며, 가장 확실한 방법은
  Search Console에 sitemap.xml 제출 + URL 검사(색인 요청)입니다.
- 그래도 자동화를 원하면 아래 절차로 사용하세요.

준비:
1) Google Cloud 프로젝트 생성 → "Indexing API" 사용 설정
2) 서비스 계정 생성 → JSON 키 다운로드 → tools/service_account.json 로 저장(절대 커밋 금지)
3) Search Console 속성에 해당 서비스 계정 이메일을 '소유자'로 추가
4) 의존성 설치:
       pip install google-auth requests

사용:
    python3 tools/google_indexing.py            # sitemap.xml 전체 URL_UPDATED 통보
    python3 tools/google_indexing.py URL ...    # 특정 URL만
"""
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA = os.path.join(ROOT, "tools", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def urls_from_sitemap():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def main():
    if not os.path.exists(SA):
        print("service_account.json 이 없습니다. 상단 준비 1~3 단계를 먼저 완료하세요.")
        sys.exit(1)
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("의존성 필요: pip install google-auth requests"); sys.exit(1)

    creds = service_account.Credentials.from_service_account_file(SA, scopes=SCOPES)
    session = AuthorizedSession(creds)
    urls = sys.argv[1:] or urls_from_sitemap()
    ok = 0
    for u in urls:
        body = {"url": u, "type": "URL_UPDATED"}
        resp = session.post(ENDPOINT, json=body)
        if resp.status_code == 200:
            ok += 1
        else:
            print(f"  실패 {resp.status_code}: {u} · {resp.text[:120]}")
    print(f"완료: {ok}/{len(urls)} URL 통보(URL_UPDATED)")


if __name__ == "__main__":
    main()
