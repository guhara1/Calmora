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

## 3) 배포 후 SEO 마무리 (색인 가장 빠르게)

사이트맵·RSS·robots·IndexNow가 모두 자동 생성됩니다.
- 사이트맵: `https://calmora.pages.dev/sitemap.xml` (91개, noindex 제외)
- RSS 피드: `https://calmora.pages.dev/rss.xml`
- IndexNow 키: `https://calmora.pages.dev/cc559fece0b5c126a4eb476e65135ded.txt`
- `robots.txt` 에 두 사이트맵 등록 + 네이버 로봇(Yeti) 허용 + 개편 준비 페이지 차단

### 검색엔진 등록
1. **구글 Search Console**: 속성 등록(소유확인) → `sitemap.xml` 제출. 빠른 색인은 URL 검사 → '색인 생성 요청'.
2. **네이버 서치어드바이저**: 사이트 등록(메인에 `naver-site-verification` 메타 이미 삽입됨) → `sitemap.xml`/`rss.xml` 제출.
3. **빙 Webmaster**: 사이트 등록 → `sitemap.xml` 제출.

### 즉시 색인 통보 (배포 완료 후 실행)
```bash
python3 tools/indexnow.py            # sitemap의 모든 URL을 빙·네이버·얀덱스에 즉시 통보
python3 tools/indexnow.py https://calmora.pages.dev/yeonsu-gu/   # 특정 URL만
```
> ⚠️ 키 파일(`/cc559...txt`)이 **라이브에 올라간 뒤** 실행해야 검증됩니다(배포 후 1회 실행 권장).
> 새 페이지를 추가/수정할 때마다 해당 URL로 다시 실행하면 즉시 재색인 통보됩니다.

### 구글은 IndexNow 미참여
구글은 IndexNow를 쓰지 않습니다. 가장 확실한 방법은 **Search Console + 사이트맵 + URL 검사**입니다.
정책상 제한이 있지만 자동화가 필요하면 `tools/google_indexing.py`(서비스 계정 필요, 파일 상단 안내 참고)를 사용하세요.
(참고: 구글·빙의 `ping?sitemap=` 방식은 2023년 폐기되어 더 이상 동작하지 않습니다.)

## 참고: 왜 "푸시"만으로는 접속이 안 됐나

GitHub에 코드를 올리는 것은 **소스 보관**일 뿐, 실제 웹 서버에 올리는 **배포**가 아닙니다.
Cloudflare Pages 같은 호스트가 저장소를 가져와 서빙해야 비로소 인터넷에서 접속됩니다.
