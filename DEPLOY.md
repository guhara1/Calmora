# 배포 가이드 · Cloudflare Pages

이 저장소는 **정적 HTML**(빌드 결과물이 이미 커밋되어 있음)이라, Cloudflare Pages에
연결만 하면 바로 서빙됩니다. 별도 빌드 없이 동작합니다.

## 1) GitHub 연동으로 배포 (권장)

1. Cloudflare 대시보드 → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
2. `guhara1/Calmora` 저장소 선택, 프로덕션 브랜치 **`main`**
3. **Build settings**:
   - Framework preset: **None**
   - Build command: **(비워둠)**  ← HTML이 이미 커밋되어 있어 빌드 불필요
   - Build output directory: **`/`**
4. **Save and Deploy**

배포가 끝나면 `https://<프로젝트명>.pages.dev` 로 접속됩니다.
- 홈은 루트(`/`)에서 바로 노출됩니다(`/incheon/` 접두어 없음).
- 구버전 `/incheon/*` 주소는 루트로 301 이동됩니다(`_redirects`).
- 없는 경로는 `404.html` 이 자동 노출됩니다.
- `/assets/*` 는 장기 캐시 헤더가 적용됩니다(`_headers`).

> 데이터(`data/incheon/*.json`)를 수정한 뒤 자동 재생성을 원하면, Build command 를
> `python3 build.py` 로 설정하세요. Cloudflare Pages 빌드 환경에 Python3가 있습니다.

## 2) 커스텀 도메인 연결 (calmora.co.kr)

1. Pages 프로젝트 → **Custom domains** → **Set up a custom domain**
2. `calmora.pages.dev`(및 `calmora.co.kr`) 추가 → 안내되는 CNAME/A 레코드를 DNS에 등록
3. 도메인이 활성화되면 canonical·og:image·sitemap(이미 `https://calmora.pages.dev` 기준)과
   완전히 일치합니다.

> 최종 도메인이 다르면 `build.py` 의 `SITE["url"]` 만 바꾸고 `python3 build.py` 재실행 후
> 커밋하면 canonical/og/sitemap/스키마가 일괄 갱신됩니다.

## 3) 배포 후 SEO 마무리

- Google Search Console에 도메인 등록 → `https://calmora.pages.dev/sitemap.xml` 제출
- `robots.txt` 는 2026 개편 준비 페이지(`/jemulpo-gu/` 등)를 차단하도록 이미 설정됨
- 색인 대상 페이지만 sitemap에 포함(noindex 페이지 제외됨)

## 참고: 왜 "푸시"만으로는 접속이 안 됐나

GitHub에 코드를 올리는 것은 **소스 보관**일 뿐, 실제 웹 서버에 올리는 **배포**가 아닙니다.
Cloudflare Pages 같은 호스트가 저장소를 가져와 서빙해야 비로소 인터넷에서 접속됩니다.
