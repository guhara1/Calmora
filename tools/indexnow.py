#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 일괄 통보 — 빙·네이버·얀덱스·Seznam에 즉시 색인 요청.
(구글은 IndexNow 미참여 → tools/google_indexing.py 또는 Search Console 사용)

사용:
    python3 tools/indexnow.py                # sitemap.xml의 모든 URL 통보
    python3 tools/indexnow.py https://calmora.pages.dev/yeonsu-gu/   # 특정 URL만

새 글/페이지를 올릴 때마다 이 스크립트를 실행하면 즉시 색인 통보됩니다.
의존성 없음(표준 라이브러리). 키는 build.py SITE["indexnow_key"]와 동일해야 합니다.
"""
import sys, os, json, re, urllib.request

HOST = "calmora.pages.dev"
KEY = "cc559fece0b5c126a4eb476e65135ded"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/IndexNow"  # 단일 제출 → 참여 엔진 전체 공유
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def urls_from_sitemap():
    p = os.path.join(ROOT, "sitemap.xml")
    with open(p, encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def submit(urls):
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow 응답: HTTP {r.status} · {len(urls)}개 URL 통보 완료")
            print("  (200/202 = 정상 접수)")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}")
    except Exception as e:
        print("오류:", e)


if __name__ == "__main__":
    urls = sys.argv[1:] or urls_from_sitemap()
    if not urls:
        print("통보할 URL이 없습니다. 먼저 python3 build.py 실행."); sys.exit(1)
    print(f"대상 {len(urls)}개 · keyLocation={KEY_LOCATION}")
    # IndexNow는 1회 최대 10,000 URL
    for i in range(0, len(urls), 10000):
        submit(urls[i:i+10000])
