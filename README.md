# Calmora · 인천 방문형 관리(출장마사지) 정보 사이트

인천 권역형(원도심·신도시·공항권·도서권) + 2026 행정개편 대응형 정적 사이트입니다.
Google 검색 가이드라인(E-E-A-T, 도움되는 콘텐츠, Who·How·Why, 스팸 정책)을 반영해 설계했습니다.

## 빌드

```bash
python3 build.py
```

`build.py` 하나가 데이터(Python dict) → 정적 HTML 트리 + `sitemap.xml` / `robots.txt` /
`404.html` / `data/*.json` 을 생성합니다. 외부 의존성 없음(Python 3.8+).

## 구조

```
build.py                  생성기(데이터 + 템플릿 + 스키마)
assets/css/tokens.css     프리미엄 토큰(딥 네이비 + 골드, 오렌지 CTA)
assets/css/styles.css     컴포넌트 오버레이
assets/js/main.js         모바일 내비 토글
assets/img/hero-spa.svg   히어로 우측 이미지(아래 "이미지 교체" 참고)
index.html                홈(루트). 구군·대표지역·생활권·역세권·이용장소·예약전확인·운영기준은
                          /jung-gu/ · /life/ · /station/ · /use/ · /check/ · /policy/ 등 루트 하위에 생성
data/incheon/*.json       구조화 데이터(지시서 25항)
sitemap.xml / robots.txt / 404.html
```

## 핵심 설정 (`build.py` 상단 `SITE`)

| 항목 | 값 |
|---|---|
| 상호 | Calmora |
| 전화예약 | 0508-202-4719 |
| 텔레그램(제작/제휴 문의) | https://t.me/googleseolab |
| 배포 도메인 | `https://calmora.pages.dev` (실제 도메인으로 수정) |

> **도메인 변경**: `SITE["url"]` 만 바꾸고 `python3 build.py` 재실행하면 canonical·og·sitemap·스키마가 일괄 갱신됩니다.

## 히어로 이미지 교체

기본값은 깨지지 않도록 SVG(`/assets/img/hero-spa.svg`)를 사용합니다.
첨부하신 실제 오션뷰 케어룸 사진을 쓰려면:

1. 사진을 `assets/img/hero-spa.jpg` 로 저장
2. `build.py` 의 `SITE["hero_img"]` 를 `"/assets/img/hero-spa.jpg"` 로 변경
3. `python3 build.py` 재실행

히어로 이미지는 메인 + 모든 지역/생활권/역세권/이용장소/예약전확인 페이지 우측에 노출됩니다.

## SEO / 가이드라인 반영

- **스키마(필수)**: 모든 페이지 `WebPage` + `BreadcrumbList` + `Organization`,
  콘텐츠 페이지 `FAQPage` + `ImageObject`. 실제 매장이 없어 `LocalBusiness`·`Review`·`AggregateRating` 미사용.
- **메타 디스크립션**: 전 페이지 80자 이내.
- **선호 썸네일**: `og:image` + schema `ImageObject` 동시 지정.
- **E-E-A-T**: 전 페이지 작성자·검수자·업데이트 기준 + Who·How·Why 블록.
- **내부링크**: 메인 → 구군 → 대표지역/생활권/역세권/이용장소/예약전확인 롱테일 연결.
  공식 출처(인천시·인천교통공사·인천공항공사·강화/옹진군청·개인정보위)는 `rel="nofollow"` 외부 링크.
- **권역별 차별화**: 신도시/원도심/공항/도서 타입별 본문 분기 — 지역명만 바꾼 페이지 금지.
- **번호동/출구/노선별 페이지 미생성**, 색인 본문 2,000자 이상 기준.
- **2026 행정개편 대응**: 제물포구·영종구·검단구 준비 페이지는 `noindex` + `robots.txt` 차단 + 사이트맵 제외.

## 페이지 인벤토리 (생성 95개)

메인 1 · 현행 구군 10 · 대표지역 16 · 생활권 16 · 역세권 26 · 이용장소 8 ·
예약전확인 8 · 운영기준 6 · 공항·도서 허브 1 · 2026 개편 draft 3(noindex)

> 세부 행정동은 `data/` 에 보관(DB)하고, 검색 수요·본문 품질이 확보된 페이지부터 단계적으로 추가·색인합니다.
