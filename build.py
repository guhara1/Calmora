#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calmora · 인천 방문형 관리(출장마사지) 정보 사이트 정적 생성기
- 프리미엄 토큰(딥 네이비 + 골드) / Pretendard
- 모든 페이지: 시맨틱 HTML + JSON-LD 스키마 + 오렌지 텔레그램 푸터 + 히어로 우측 이미지
- 지역명만 바꾼 대량 페이지 금지: 권역(신도시/원도심/공항/도서)별로 본문 차별화
- 디스크립션 80자 이내, 내부링크/롱테일 강화

산출물: 저장소 루트에 정적 HTML 트리 + sitemap.xml / robots.txt / 404.html + data/*.json
"""
import os, json, html, datetime, re

ROOT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
SITE = {
    "brand": "Calmora",
    "phone": "0508-202-4719",
    "phone_href": "tel:0508-202-4719",
    "telegram": "https://t.me/googleseolab",
    "url": "https://calmora.pages.dev",      # 배포 도메인(Cloudflare Pages)
    "locale": "ko_KR",
    "today": "2026-06-28",
    "author": "인천 지역 안내 콘텐츠 담당자",
    "reviewer": "운영 책임자 · 콘텐츠 품질 검수 담당자",
    "hero_img": "/assets/img/hero-spa.webp",       # 실제 사진(webp, ≤50KB)
    "hero_img_fallback": "/assets/img/hero-spa.svg",  # 파일이 없을 때 자동 폴백
    "hero_alt": "오션뷰 프리미엄 케어룸 · 인천 방문형 관리 안내 이미지",
}

# 권위 있는 외부 참고 링크(롱테일 보강용, nofollow 처리)
AUTHORITY = {
    "incheon": ("인천광역시 공식 누리집", "https://www.incheon.go.kr/"),
    "subway": ("인천교통공사 도시철도 안내", "https://www.ictr.or.kr/"),
    "airport": ("인천국제공항공사", "https://www.airport.kr/"),
    "ganghwa": ("강화군청", "https://www.ganghwa.go.kr/"),
    "ongjin": ("옹진군청", "https://www.ongjin.go.kr/"),
    "privacy": ("개인정보보호위원회", "https://www.pipc.go.kr/"),
}

# ----------------------------------------------------------------------------
# 상단 메뉴 (메뉴명에 "출장마사지"를 반복하지 않음)
# ----------------------------------------------------------------------------
NAV = [
    ("인천 홈", "/", None),
    ("구군 안내", "/#gu", [
        ("인천 전체", "/"),
        ("중구", "/jung-gu/"), ("동구", "/dong-gu/"),
        ("미추홀구", "/michuhol-gu/"), ("연수구", "/yeonsu-gu/"),
        ("남동구", "/namdong-gu/"), ("부평구", "/bupyeong-gu/"),
        ("계양구", "/gyeyang-gu/"), ("서구", "/seo-gu/"),
        ("강화군", "/ganghwa-gun/"), ("옹진군", "/ongjin-gun/"),
    ]),
    ("생활권", "/#life", [
        ("송도국제도시", "/life/songdo-international-city/"),
        ("청라국제도시", "/life/cheongna-international-city/"),
        ("검단신도시", "/life/geomdan-newtown/"),
        ("부평역·부평시장", "/life/bupyeong-station-market/"),
        ("구월·인천시청", "/life/guwol-incheon-cityhall/"),
        ("주안·도화", "/life/juan-dohwa/"),
        ("동인천·제물포", "/life/dongincheon-jemulpo/"),
        ("영종·운서", "/life/yeongjong-unseo/"),
    ]),
    ("지하철역", "/#station", [
        ("부평역", "/station/bupyeong-station/"),
        ("주안역", "/station/juan-station/"),
        ("인천시청역", "/station/incheon-cityhall-station/"),
        ("인천대입구역", "/station/incheon-univ-station/"),
        ("동인천역", "/station/dongincheon-station/"),
        ("계산역", "/station/gyesan-station/"),
    ]),
    ("이용 장소", "/#use", [
        ("자택 이용", "/use/home/"), ("호텔·숙소 이용", "/use/hotel/"),
        ("오피스텔 이용", "/use/officetel/"), ("업무지구 이용", "/use/business-district/"),
        ("역세권 이용", "/use/station-area/"), ("야간 예약", "/use/night/"),
        ("공항권 이용", "/use/airport-area/"), ("도서 지역 이용", "/use/island-area/"),
    ]),
    ("공항·도서", "/airport-island/", [
        ("영종·운서", "/life/yeongjong-unseo/"),
        ("인천공항", "/life/incheon-airport/"),
        ("강화", "/life/ganghwa/"),
        ("옹진 도서", "/life/ongjin-islands/"),
    ]),
    ("예약 전 확인", "/check/address/", [
        ("방문 주소 확인", "/check/address/"), ("건물 출입 방식", "/check/building-access/"),
        ("추가 이동비 기준", "/check/travel-fee/"), ("예약 가능 시간", "/check/time/"),
        ("예약 변경 기준", "/check/change-policy/"), ("개인정보 처리 기준", "/check/privacy/"),
        ("불법·선정적 서비스 불가", "/check/service-policy/"), ("고객 유의사항", "/check/customer-notice/"),
    ]),
    ("문의하기", "/policy/contact/", None),
]

# ----------------------------------------------------------------------------
# 데이터: 구군 / 대표지역 / 생활권 / 역세권 / 이용장소 / 예약전확인 / 운영기준
# areaType: newtown / old-town / airport / island / residential / business / station-area
# ----------------------------------------------------------------------------
GUS = [
    {"slug":"jung-gu","name":"중구","type":"airport","life":["동인천·제물포","영종·운서","인천공항"],
     "stations":["인천역","동인천역","운서역","인천공항1터미널역"],
     "focus":"원도심과 항만, 영종·공항권이 한 행정구역에 함께 있어 권역을 분리해 확인해야 하는 곳"},
    {"slug":"dong-gu","name":"동구","type":"old-town","life":["동인천","송림","화수"],
     "stations":["동인천역","도원역"],
     "focus":"전통 주거지와 원도심이 중심이며 2026 제물포구 개편 대응이 필요한 곳"},
    {"slug":"michuhol-gu","name":"미추홀구","type":"old-town","life":["주안·도화","용현·학익","숭의"],
     "stations":["주안역","제물포역","인하대역"],
     "focus":"역세권·대학가·원도심 주거지가 섞여 생활권별 동선이 다른 곳"},
    {"slug":"yeonsu-gu","name":"연수구","type":"newtown","life":["송도국제도시","연수·원인재"],
     "stations":["인천대입구역","센트럴파크역","원인재역"],
     "focus":"송도국제도시 중심의 신도시·업무지구·호텔·오피스텔 비중이 높은 곳"},
    {"slug":"namdong-gu","name":"남동구","type":"business","life":["구월·인천시청","논현·소래","간석"],
     "stations":["인천시청역","구월역","인천논현역","소래포구역"],
     "focus":"인천시청·행정과 상권이 모인 중심권과 논현·소래 주거권이 함께 있는 곳"},
    {"slug":"bupyeong-gu","name":"부평구","type":"station-area","life":["부평역·부평시장","삼산·부평구청","부개"],
     "stations":["부평역","부평시장역","부평구청역"],
     "focus":"부평역 환승 거점과 상권, 조밀한 주거지가 모인 역세권 중심 생활권"},
    {"slug":"gyeyang-gu","name":"계양구","type":"residential","life":["계산·작전","계양역 인접","효성"],
     "stations":["계산역","작전역","계양역"],
     "focus":"주거지 중심이며 서울·김포공항 인접 이동권에 가까운 곳"},
    {"slug":"seo-gu","name":"서구","type":"newtown","life":["청라국제도시","검단신도시","검암","가정·루원"],
     "stations":["청라국제도시역","검암역","검단사거리역"],
     "focus":"청라·검단 신도시가 빠르게 확장 중이며 2026 검단구 분리 대응이 필요한 곳"},
    {"slug":"ganghwa-gun","name":"강화군","type":"island","life":["강화읍","길상","선원","내가"],
     "stations":[],
     "focus":"지하철이 닿지 않는 외곽·도서형 권역으로 차량 이동과 사전 예약 확인이 먼저인 곳"},
    {"slug":"ongjin-gun","name":"옹진군","type":"island","life":["영흥","백령","대청","연평","자월"],
     "stations":[],
     "focus":"여러 섬으로 이루어진 도서권으로 방문 가능 여부와 이동 일정 확인이 핵심인 곳"},
]
GU_BY_SLUG = {g["slug"]: g for g in GUS}

AREAS = [
    {"slug":"songdo","name":"송도","gu":"yeonsu-gu","type":"newtown","life":"송도국제도시",
     "lifeslug":"songdo-international-city","stations":["인천대입구역","센트럴파크역"],
     "focus":"국제업무지구·호텔·오피스텔이 밀집한 신도시"},
    {"slug":"guwol-dong","name":"구월","gu":"namdong-gu","type":"business","life":"구월·인천시청",
     "lifeslug":"guwol-incheon-cityhall","stations":["인천시청역","구월역"],
     "focus":"인천시청과 상권이 모인 행정·생활 중심"},
    {"slug":"nonhyeon-dong","name":"논현","gu":"namdong-gu","type":"residential","life":"논현·소래",
     "lifeslug":"nonhyeon-sorae","stations":["인천논현역","소래포구역"],
     "focus":"대단지 주거지와 소래포구 인접 생활권"},
    {"slug":"juan-dong","name":"주안","gu":"michuhol-gu","type":"station-area","life":"주안·도화",
     "lifeslug":"juan-dohwa","stations":["주안역"],
     "focus":"환승 역세권과 원도심 주거지가 맞닿은 생활권"},
    {"slug":"dohwa-dong","name":"도화","gu":"michuhol-gu","type":"old-town","life":"주안·도화",
     "lifeslug":"juan-dohwa","stations":["주안역","제물포역"],
     "focus":"제물포 인접 원도심 주거지"},
    {"slug":"yonghyeon-dong","name":"용현","gu":"michuhol-gu","type":"old-town","life":"용현·학익",
     "lifeslug":"yonghyeon-hagik","stations":["인하대역","제물포역"],
     "focus":"인하대 인근 대학가와 원도심 주거지"},
    {"slug":"hagik-dong","name":"학익","gu":"michuhol-gu","type":"residential","life":"용현·학익",
     "lifeslug":"yonghyeon-hagik","stations":["인하대역"],
     "focus":"법조·행정 인접 주거지"},
    {"slug":"bupyeong-dong","name":"부평","gu":"bupyeong-gu","type":"station-area","life":"부평역·부평시장",
     "lifeslug":"bupyeong-station-market","stations":["부평역","부평시장역"],
     "focus":"인천 최대 환승 거점과 상권이 결합한 역세권"},
    {"slug":"samsan-dong","name":"삼산","gu":"bupyeong-gu","type":"residential","life":"삼산·부평구청",
     "lifeslug":"samsan-bupyeong-gu-office","stations":["부평구청역","삼산체육관역"],
     "focus":"부평구청·쇼핑 인접 주거지"},
    {"slug":"gyesan-dong","name":"계산","gu":"gyeyang-gu","type":"residential","life":"계산·작전",
     "lifeslug":"gyesan-jakjeon","stations":["계산역","경인교대입구역"],
     "focus":"계양 생활권의 대표 주거지이며 서울 인접 이동권"},
    {"slug":"jakjeon-dong","name":"작전","gu":"gyeyang-gu","type":"residential","life":"계산·작전",
     "lifeslug":"gyesan-jakjeon","stations":["작전역"],
     "focus":"계양 생활권 주거지"},
    {"slug":"cheongna","name":"청라","gu":"seo-gu","type":"newtown","life":"청라국제도시",
     "lifeslug":"cheongna-international-city","stations":["청라국제도시역"],
     "focus":"오피스텔·주거가 밀집한 국제도시형 신도시"},
    {"slug":"geomdan-area","name":"검단","gu":"seo-gu","type":"newtown","life":"검단신도시",
     "lifeslug":"geomdan-newtown","stations":["검단사거리역"],
     "focus":"빠르게 입주가 진행 중인 신도시이며 2026 검단구 분리 대응 권역"},
    {"slug":"yeongjong-area","name":"영종","gu":"jung-gu","type":"airport","life":"영종·운서",
     "lifeslug":"yeongjong-unseo","stations":["운서역","영종역"],
     "focus":"공항 배후 신도시이자 숙소·차량 이동 기준이 다른 공항권"},
    {"slug":"unseo-dong","name":"운서","gu":"jung-gu","type":"airport","life":"영종·운서",
     "lifeslug":"yeongjong-unseo","stations":["운서역"],
     "focus":"공항 인접 숙소·오피스텔이 모인 공항 생활권"},
    {"slug":"incheon-airport-area","name":"인천공항","gu":"jung-gu","type":"airport","life":"인천공항",
     "lifeslug":"incheon-airport","stations":["인천공항1터미널역","인천공항2터미널역"],
     "focus":"공항 터미널·인접 숙소권으로 이동 시간과 사전 예약 확인이 핵심"},
]

LIFE = [
    {"slug":"songdo-international-city","name":"송도국제도시","type":"newtown","gu":"yeonsu-gu",
     "stations":["인천대입구역","센트럴파크역","송도달빛축제공원역"],"areas":["송도"],
     "focus":"국제업무지구·컨벤시아·호텔·오피스텔이 밀집한 신도시 업무·숙박 중심권"},
    {"slug":"cheongna-international-city","name":"청라국제도시","type":"newtown","gu":"seo-gu",
     "stations":["청라국제도시역"],"areas":["청라"],
     "focus":"호수공원과 대단지 오피스텔·주거가 결합한 신도시 생활권"},
    {"slug":"geomdan-newtown","name":"검단신도시","type":"newtown","gu":"seo-gu",
     "stations":["검단사거리역","검단오류역"],"areas":["검단"],
     "focus":"신규 입주가 활발한 신도시이며 2026 검단구 분리 대응 권역"},
    {"slug":"yeongjong-unseo","name":"영종·운서","type":"airport","gu":"jung-gu",
     "stations":["운서역","영종역"],"areas":["영종","운서"],
     "focus":"공항 배후 신도시와 숙소권, 차량 이동 기준이 도심과 다른 공항권"},
    {"slug":"bupyeong-station-market","name":"부평역·부평시장","type":"station-area","gu":"bupyeong-gu",
     "stations":["부평역","부평시장역"],"areas":["부평"],
     "focus":"인천 최대 환승 거점과 전통 상권이 맞물린 역세권 중심 생활권"},
    {"slug":"juan-dohwa","name":"주안·도화","type":"old-town","gu":"michuhol-gu",
     "stations":["주안역","제물포역"],"areas":["주안","도화"],
     "focus":"역세권과 원도심 주거지가 이어지는 생활권"},
    {"slug":"guwol-incheon-cityhall","name":"구월·인천시청","type":"business","gu":"namdong-gu",
     "stations":["인천시청역","구월역","예술회관역"],"areas":["구월"],
     "focus":"인천시청·행정과 상권, 숙소가 모인 중심 생활권"},
    {"slug":"dongincheon-jemulpo","name":"동인천·제물포","type":"old-town","gu":"jung-gu",
     "stations":["동인천역","제물포역","인천역"],"areas":["동인천"],
     "focus":"개항장·항만과 맞닿은 인천의 대표 원도심 생활권"},
    {"slug":"yonghyeon-hagik","name":"용현·학익","type":"old-town","gu":"michuhol-gu",
     "stations":["인하대역","제물포역"],"areas":["용현","학익"],
     "focus":"대학가와 행정·주거가 섞인 원도심 생활권"},
    {"slug":"gyesan-jakjeon","name":"계산·작전","type":"residential","gu":"gyeyang-gu",
     "stations":["계산역","작전역","경인교대입구역"],"areas":["계산","작전"],
     "focus":"계양 생활권 주거지이며 서울·김포 인접 이동권"},
    {"slug":"yeonsu-woninjae","name":"연수·원인재","type":"residential","gu":"yeonsu-gu",
     "stations":["원인재역","연수역"],"areas":["연수"],
     "focus":"송도와 원도심을 잇는 주거 중심 생활권"},
    {"slug":"nonhyeon-sorae","name":"논현·소래","type":"residential","gu":"namdong-gu",
     "stations":["인천논현역","소래포구역"],"areas":["논현"],
     "focus":"대단지 주거지와 소래포구 인접권"},
    {"slug":"samsan-bupyeong-gu-office","name":"삼산·부평구청","type":"residential","gu":"bupyeong-gu",
     "stations":["부평구청역","삼산체육관역"],"areas":["삼산"],
     "focus":"부평구청·쇼핑 인접 주거 생활권"},
    {"slug":"incheon-airport","name":"인천공항","type":"airport","gu":"jung-gu",
     "stations":["인천공항1터미널역","인천공항2터미널역"],"areas":["인천공항"],
     "focus":"공항 터미널과 인접 숙소권, 이동 시간·사전 예약 확인이 핵심인 공항권"},
    {"slug":"ganghwa","name":"강화","type":"island","gu":"ganghwa-gun",
     "stations":[],"areas":[],
     "focus":"지하철이 닿지 않는 외곽·도서형 권역으로 차량 이동과 사전 예약이 먼저인 곳"},
    {"slug":"ongjin-islands","name":"옹진 도서","type":"island","gu":"ongjin-gun",
     "stations":[],"areas":[],
     "focus":"영흥·백령·대청·연평·자월 등 여러 섬으로 이루어진 도서권"},
]
LIFE_BY_SLUG = {l["slug"]: l for l in LIFE}

STATIONS = [
    {"slug":"incheon-cityhall-station","name":"인천시청역","gu":"namdong-gu","type":"business","life":"구월·인천시청","lifeslug":"guwol-incheon-cityhall","transfer":True,"near":["구월","간석"]},
    {"slug":"guwol-station","name":"구월역","gu":"namdong-gu","type":"business","life":"구월·인천시청","lifeslug":"guwol-incheon-cityhall","transfer":False,"near":["구월"]},
    {"slug":"ganseogogeori-station","name":"간석오거리역","gu":"namdong-gu","type":"residential","life":"구월·인천시청","lifeslug":"guwol-incheon-cityhall","transfer":False,"near":["간석"]},
    {"slug":"bupyeong-station","name":"부평역","gu":"bupyeong-gu","type":"station-area","life":"부평역·부평시장","lifeslug":"bupyeong-station-market","transfer":True,"near":["부평","부개"]},
    {"slug":"bupyeong-gu-office-station","name":"부평구청역","gu":"bupyeong-gu","type":"station-area","life":"삼산·부평구청","lifeslug":"samsan-bupyeong-gu-office","transfer":True,"near":["삼산"]},
    {"slug":"bupyeong-market-station","name":"부평시장역","gu":"bupyeong-gu","type":"station-area","life":"부평역·부평시장","lifeslug":"bupyeong-station-market","transfer":False,"near":["부평"]},
    {"slug":"dongam-station","name":"동암역","gu":"bupyeong-gu","type":"station-area","life":"부평역·부평시장","lifeslug":"bupyeong-station-market","transfer":False,"near":["십정"]},
    {"slug":"juan-station","name":"주안역","gu":"michuhol-gu","type":"station-area","life":"주안·도화","lifeslug":"juan-dohwa","transfer":True,"near":["주안","도화"]},
    {"slug":"jemulpo-station","name":"제물포역","gu":"michuhol-gu","type":"old-town","life":"용현·학익","lifeslug":"yonghyeon-hagik","transfer":False,"near":["도화","숭의"]},
    {"slug":"dongincheon-station","name":"동인천역","gu":"jung-gu","type":"old-town","life":"동인천·제물포","lifeslug":"dongincheon-jemulpo","transfer":False,"near":["동인천"]},
    {"slug":"incheon-station","name":"인천역","gu":"jung-gu","type":"old-town","life":"동인천·제물포","lifeslug":"dongincheon-jemulpo","transfer":True,"near":["개항장"]},
    {"slug":"incheon-univ-station","name":"인천대입구역","gu":"yeonsu-gu","type":"newtown","life":"송도국제도시","lifeslug":"songdo-international-city","transfer":False,"near":["송도"]},
    {"slug":"central-park-station","name":"센트럴파크역","gu":"yeonsu-gu","type":"newtown","life":"송도국제도시","lifeslug":"songdo-international-city","transfer":False,"near":["송도"]},
    {"slug":"songdo-moonlight-festival-park-station","name":"송도달빛축제공원역","gu":"yeonsu-gu","type":"newtown","life":"송도국제도시","lifeslug":"songdo-international-city","transfer":False,"near":["송도"]},
    {"slug":"woninjae-station","name":"원인재역","gu":"yeonsu-gu","type":"residential","life":"연수·원인재","lifeslug":"yeonsu-woninjae","transfer":True,"near":["연수"]},
    {"slug":"incheon-nonhyeon-station","name":"인천논현역","gu":"namdong-gu","type":"residential","life":"논현·소래","lifeslug":"nonhyeon-sorae","transfer":False,"near":["논현"]},
    {"slug":"soraepogu-station","name":"소래포구역","gu":"namdong-gu","type":"residential","life":"논현·소래","lifeslug":"nonhyeon-sorae","transfer":False,"near":["논현","소래"]},
    {"slug":"geomam-station","name":"검암역","gu":"seo-gu","type":"newtown","life":"청라국제도시","lifeslug":"cheongna-international-city","transfer":True,"near":["검암","청라"]},
    {"slug":"cheongna-international-city-station","name":"청라국제도시역","gu":"seo-gu","type":"newtown","life":"청라국제도시","lifeslug":"cheongna-international-city","transfer":False,"near":["청라"]},
    {"slug":"geomdan-sageori-station","name":"검단사거리역","gu":"seo-gu","type":"newtown","life":"검단신도시","lifeslug":"geomdan-newtown","transfer":False,"near":["검단"]},
    {"slug":"gyesan-station","name":"계산역","gu":"gyeyang-gu","type":"residential","life":"계산·작전","lifeslug":"gyesan-jakjeon","transfer":False,"near":["계산"]},
    {"slug":"jakjeon-station","name":"작전역","gu":"gyeyang-gu","type":"residential","life":"계산·작전","lifeslug":"gyesan-jakjeon","transfer":False,"near":["작전"]},
    {"slug":"gyeyang-station","name":"계양역","gu":"gyeyang-gu","type":"residential","life":"계산·작전","lifeslug":"gyesan-jakjeon","transfer":True,"near":["계양"]},
    {"slug":"unseo-station","name":"운서역","gu":"jung-gu","type":"airport","life":"영종·운서","lifeslug":"yeongjong-unseo","transfer":False,"near":["운서","영종"]},
    {"slug":"incheon-airport-terminal-1-station","name":"인천공항1터미널역","gu":"jung-gu","type":"airport","life":"인천공항","lifeslug":"incheon-airport","transfer":False,"near":["공항 제1터미널"]},
    {"slug":"incheon-airport-terminal-2-station","name":"인천공항2터미널역","gu":"jung-gu","type":"airport","life":"인천공항","lifeslug":"incheon-airport","transfer":False,"near":["공항 제2터미널"]},
]

STATION_SLUG = {s["name"]: s["slug"] for s in STATIONS}

# 실제 후기 데이터 로드(없거나 비어 있으면 후기 섹션·평점 스키마 미출력 = 가짜 후기 금지)
def load_reviews():
    p = os.path.join(ROOT, "data", "incheon", "reviews.json")
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        items = [r for r in data.get("items", []) if r.get("body") and r.get("rating")]
        return {"best": data.get("bestRating", 5), "items": items}
    except Exception:
        return {"best": 5, "items": []}

REVIEWS = load_reviews()

USES = [
    {"slug":"home","name":"자택 이용","kw":"자택","focus":"공동현관 출입과 정확한 동·호수 확인이 핵심인 가정 방문"},
    {"slug":"hotel","name":"호텔·숙소 이용","kw":"호텔·숙소","focus":"숙소 정책과 객실 호수, 프런트 출입 절차 확인이 필요한 이용"},
    {"slug":"officetel","name":"오피스텔 이용","kw":"오피스텔","focus":"관리실 규정·공동현관·주차 확인이 필요한 이용"},
    {"slug":"business-district","name":"업무지구 이용","kw":"업무지구","focus":"건물 출입증·로비 보안·예약 시간대 확인이 필요한 업무지구"},
    {"slug":"station-area","name":"역세권 이용","kw":"역세권","focus":"역명만으로 위치를 좁히되 실제 주소·건물 출입을 함께 확인하는 이용"},
    {"slug":"night","name":"야간 예약","kw":"야간","focus":"예약 가능 시간대·이동 동선·건물 야간 출입 확인이 필요한 야간"},
    {"slug":"airport-area","name":"공항권 이용","kw":"공항권","focus":"이동 시간·숙소 위치·추가 이동비 사전 확인이 핵심인 공항권"},
    {"slug":"island-area","name":"도서 지역 이용","kw":"도서 지역","focus":"방문 가능 여부와 이동 일정을 먼저 확인해야 하는 도서권"},
]

CHECKS = [
    {"slug":"address","name":"방문 주소 확인","h1":"예약 전 방문 주소 확인 안내",
     "focus":"도로명 주소, 동·호수, 공동현관 위치를 정확히 확인하는 단계"},
    {"slug":"building-access","name":"건물 출입 방식","h1":"건물 출입 방식 확인 안내",
     "focus":"공동현관 비밀번호, 경비·프런트 출입, 엘리베이터 카드 등 출입 방식 확인"},
    {"slug":"travel-fee","name":"추가 이동비 기준","h1":"추가 이동비 기준 안내",
     "focus":"이동 거리·시간대·외곽/공항/도서 여부에 따른 추가 이동비 확인"},
    {"slug":"time","name":"예약 가능 시간","h1":"예약 가능 시간 안내",
     "focus":"예약 가능 시간대와 마감 시간, 야간 가능 여부 확인"},
    {"slug":"change-policy","name":"예약 변경 기준","h1":"예약 변경·취소 기준 안내",
     "focus":"예약 변경과 취소가 가능한 시점, 사전 연락 기준 확인"},
    {"slug":"privacy","name":"개인정보 처리 기준","h1":"개인정보 처리 기준 안내",
     "focus":"예약 확인과 연락에 필요한 최소 정보만 안내·이용하는 기준"},
    {"slug":"service-policy","name":"불법·선정적 서비스 불가 안내","h1":"불법·선정적 서비스 불가 안내",
     "focus":"불법·선정적 서비스를 제공하거나 안내하지 않는 운영 기준"},
    {"slug":"customer-notice","name":"고객 유의사항","h1":"고객 유의사항 안내",
     "focus":"예약 전후 고객이 확인해야 할 유의사항 정리"},
]

# 운영 기준(정책) 페이지
POLICIES = [
    {"slug":"privacy-policy","name":"개인정보 처리방침","h1":"개인정보 처리방침"},
    {"slug":"service-standard","name":"서비스 이용 기준","h1":"서비스 이용 기준"},
    {"slug":"illegal-service","name":"불법·선정적 서비스 불가 안내","h1":"불법·선정적 서비스 불가 안내"},
    {"slug":"content-standard","name":"콘텐츠 작성 기준","h1":"콘텐츠 작성 기준"},
    {"slug":"authors","name":"작성자·검수자 안내","h1":"작성자·검수자 안내"},
    {"slug":"contact","name":"문의하기","h1":"문의하기"},
]

# 2026 행정개편 대응(draft / noindex)
REFORM = [
    {"slug":"jemulpo-gu","name":"제물포구","base":["중구","동구"]},
    {"slug":"yeongjong-gu","name":"영종구","base":["중구 영종·운서"]},
    {"slug":"geomdan-gu","name":"검단구","base":["서구 검단신도시"]},
]

TYPE_LABEL = {"newtown":"신도시형","old-town":"원도심형","airport":"공항권","island":"도서권",
              "residential":"주거형","business":"행정·상권형","station-area":"역세권형"}

# ----------------------------------------------------------------------------
# 렌더링 헬퍼
# ----------------------------------------------------------------------------
def esc(s): return html.escape(str(s), quote=True)

def clamp(text, n=80):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= n else text[:n-1].rstrip() + "…"

def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

def org_node():
    return {
        "@type": "Organization",
        "@id": SITE["url"] + "/#org",
        "name": SITE["brand"],
        "url": SITE["url"] + "/",
        "telephone": SITE["phone"],
        "areaServed": "인천광역시",
        "knowsLanguage": "ko",
        "sameAs": [SITE["telegram"]],
    }

def breadcrumb_ld(crumbs):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": name,
             "item": SITE["url"] + url} for i, (name, url) in enumerate(crumbs)
        ],
    }

def faq_ld(faqs):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs
        ],
    }

def image_ld(url, caption):
    return {"@type": "ImageObject", "contentUrl": SITE["url"] + url,
            "url": SITE["url"] + url, "caption": caption}

def build_nav_html(active=""):
    items = []
    for label, href, children in NAV:
        if children:
            sub = "".join(f'<a href="{esc(c_href)}">{esc(c_label)}</a>'
                          for c_label, c_href in children)
            items.append(
                f'<li class="dropdown"><a href="{esc(href)}" aria-haspopup="true">{esc(label)}</a>'
                f'<div class="dropdown-panel">{sub}</div></li>')
        else:
            items.append(f'<li><a href="{esc(href)}">{esc(label)}</a></li>')
    return (
        '<header class="site-header"><div class="container">'
        '<nav class="nav" aria-label="주 메뉴">'
        f'<a class="brand" href="/"><b>{esc(SITE["brand"])}</b><small>인천 방문형 관리 안내</small></a>'
        f'<ul class="nav-menu">{"".join(items)}</ul>'
        f'<a class="nav-call" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a>'
        '<button class="nav-toggle" data-nav-toggle aria-expanded="false" aria-label="메뉴 열기">☰</button>'
        '</nav></div></header>')

def hero_figure_html():
    # 실제 사진(jpg) 우선, 없으면 SVG로 자동 폴백
    fallback = esc(SITE["hero_img_fallback"])
    return (
        '<div class="hero-figure">'
        f'<img src="{esc(SITE["hero_img"])}" width="1200" height="900" '
        f'alt="{esc(SITE["hero_alt"])}" fetchpriority="high" decoding="async" '
        f'onerror="this.onerror=null;this.src=\'{fallback}\'">'
        '<span class="hero-badge">★ 프리미엄 케어 · 예약 안내</span>'
        '</div>')

def footer_html():
    tg = esc(SITE["telegram"])
    return (
      '<footer class="site-footer"><div class="container">'
      # CTA: 오렌지 텔레그램 버튼 2종
      '<div class="footer-cta">'
        '<div><h3>웹사이트 제작·제휴가 필요하신가요?</h3>'
        '<p>홈페이지 제작 문의와 제휴 제안을 텔레그램으로 빠르게 도와드립니다.</p></div>'
        '<div class="btn-row">'
          f'<a class="btn btn-orange" href="{tg}" target="_blank" rel="noopener nofollow">웹사이트 제작문의</a>'
          f'<a class="btn btn-orange" href="{tg}" target="_blank" rel="noopener nofollow">제휴문의</a>'
        '</div>'
      '</div>'
      # 그리드
      '<div class="footer-grid">'
        '<div class="footer-brand">'
          f'<a class="brand" href="/"><b>{esc(SITE["brand"])}</b></a>'
          '<p>인천 원도심·신도시·공항권·도서권을 권역으로 나누어 방문형 관리 예약 전 확인사항을 안내합니다.</p>'
          f'<a class="footer-phone" href="{SITE["phone_href"]}">📞 전화예약 {esc(SITE["phone"])}</a>'
        '</div>'
        '<div class="footer-col"><h4>지역 안내</h4><ul>'
          '<li><a href="/">인천 홈</a></li>'
          '<li><a href="/yeonsu-gu/">연수구</a></li>'
          '<li><a href="/bupyeong-gu/">부평구</a></li>'
          '<li><a href="/seo-gu/">서구</a></li>'
          '<li><a href="/life/songdo-international-city/">송도국제도시</a></li>'
        '</ul></div>'
        '<div class="footer-col"><h4>예약 전 확인</h4><ul>'
          '<li><a href="/check/address/">방문 주소 확인</a></li>'
          '<li><a href="/check/travel-fee/">추가 이동비 기준</a></li>'
          '<li><a href="/check/time/">예약 가능 시간</a></li>'
          '<li><a href="/check/privacy/">개인정보 처리 기준</a></li>'
        '</ul></div>'
        '<div class="footer-col"><h4>운영 기준</h4><ul>'
          '<li><a href="/policy/privacy-policy/">개인정보 처리방침</a></li>'
          '<li><a href="/policy/illegal-service/">불법·선정적 서비스 불가</a></li>'
          '<li><a href="/policy/authors/">작성자·검수자 안내</a></li>'
          '<li><a href="/policy/contact/">문의하기</a></li>'
          '<li><a href="/sitemap.xml">사이트맵</a></li>'
        '</ul></div>'
      '</div>'
      '<p class="footer-disclaimer">방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다. '
      '본 사이트는 불법·선정적 서비스를 제공하거나 안내하지 않으며, 허위 후기·과장된 가격 문구를 사용하지 않습니다. '
      '개인정보는 예약 확인과 연락 목적에 필요한 최소 범위만 이용합니다.</p>'
      f'<div class="footer-bottom"><span>© 2026 {esc(SITE["brand"])}. 인천 방문형 관리 안내.</span>'
      f'<span>전화예약 {esc(SITE["phone"])}</span></div>'
      '</div></footer>')

def eeat_block():
    return (
      '<section class="eeat" aria-label="작성자 및 검수 정보">'
      '<h4>작성자·검수 안내</h4>'
      '<dl>'
        f'<dt>작성</dt><dd>{esc(SITE["author"])}</dd>'
        f'<dt>검수</dt><dd>{esc(SITE["reviewer"])}</dd>'
        f'<dt>업데이트</dt><dd>{esc(SITE["today"])} · 인천 행정구역·생활권·역세권 변화 반영</dd>'
      '</dl></section>')

def whohowwhy_block(who, how, why):
    return (
      '<div class="whohowwhy">'
      f'<div><b>Who</b><p>{esc(who)}</p></div>'
      f'<div><b>How</b><p>{esc(how)}</p></div>'
      f'<div><b>Why</b><p>{esc(why)}</p></div>'
      '</div>')

def faq_html(faqs):
    items = "".join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    return f'<div class="faq">{items}</div>'

def breadcrumb_html(crumbs):
    lis = "".join(
        (f'<li><a href="{esc(url)}">{esc(name)}</a></li>' if i < len(crumbs)-1
         else f'<li aria-current="page">{esc(name)}</li>')
        for i, (name, url) in enumerate(crumbs))
    return f'<nav class="breadcrumb" aria-label="위치"><div class="container"><ol>{lis}</ol></div></nav>'

def aside_html(title, links, authority=None):
    ll = "".join(f'<li><a href="{esc(u)}">{esc(n)}</a></li>' for n, u in links)
    auth = ""
    if authority:
        a = "".join(
            f'<li><a href="{esc(u)}" target="_blank" rel="noopener nofollow">{esc(n)} ↗</a></li>'
            for n, u in authority)
        auth = f'<h4 style="margin-top:1rem">공식 참고</h4><ul class="link-list">{a}</ul>'
    return (f'<aside class="aside-card"><h4>{esc(title)}</h4>'
            f'<ul class="link-list">{ll}</ul>{auth}</aside>')

# ----------------------------------------------------------------------------
# 페이지 문서 래퍼
# ----------------------------------------------------------------------------
def document(*, path, title, description, body, schema_nodes, noindex=False,
             og_image=None, hero=None):
    canonical = SITE["url"] + path
    og_image = og_image or SITE["hero_img"]
    robots = "noindex, nofollow" if noindex else "index, follow, max-image-preview:large"
    graph = {"@context": "https://schema.org", "@graph": schema_nodes}
    head = [
        '<!doctype html>',
        '<html lang="ko">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{esc(title)}</title>',
        f'<meta name="description" content="{esc(description)}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta name="author" content="{esc(SITE["author"])}">',
        # Favicon
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">',
        '<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">',
        '<meta name="theme-color" content="#0A0D12">',
        # Open Graph / Twitter — 선호 썸네일 명시
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{esc(SITE["brand"])}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:locale" content="{SITE["locale"]}">',
        f'<meta property="og:image" content="{esc(SITE["url"] + og_image)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:image" content="{esc(SITE["url"] + og_image)}">',
        # Pretendard (preconnect + CDN)
        '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>',
        '<link rel="stylesheet" as="style" crossorigin '
        'href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">',
        '<link rel="stylesheet" href="/assets/css/tokens.css">',
        '<link rel="stylesheet" href="/assets/css/styles.css">',
        jsonld(graph),
        '</head>',
        f'<body>',
        '<a class="skip-link" href="#main">본문 바로가기</a>',
        build_nav_html(),
    ]
    tail = ['<script src="/assets/js/main.js" defer></script>', '</body>', '</html>']
    hero_html = hero or ""
    return "\n".join(head) + "\n" + hero_html + f'<main id="main">{body}</main>' + footer_html() + "\n".join(tail)

def write_page(path, content):
    rel = path.strip("/")
    out_dir = os.path.join(ROOT, rel)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)

# ----------------------------------------------------------------------------
# 본문 콘텐츠 빌더 (권역별 차별화)
# ----------------------------------------------------------------------------
USECASE_BANK = {
    "newtown": "신도시 생활권에서는 오피스텔과 주상복합, 호텔이 함께 있어 공동현관 비밀번호와 동·호수, 엘리베이터 카드 사용 여부를 먼저 확인하는 것이 좋습니다. 주차가 필요한 위치인지, 방문 차량 등록 절차가 있는지, 관리실 운영 시간은 어떤지에 따라 도착 동선이 달라집니다. 업무지구가 인접한 경우 로비 보안과 방문 등록 절차가 추가될 수 있으므로 예약 시간대를 여유 있게 잡는 편이 안전합니다.",
    "old-town": "원도심 주거지는 단독·다세대 주택과 노후 아파트가 섞여 있어 도로명 주소와 건물 외형, 공동현관 위치를 정확히 확인하는 것이 중요합니다. 골목 진입과 주차 공간이 제한적일 수 있어 가까운 하차 지점과 도보 동선을 미리 알려주시면 도착이 빨라집니다. 같은 동이라도 번지에 따라 위치 차이가 크므로 동·호수까지 함께 확인합니다.",
    "airport": "공항권은 도심과 이동 기준이 다릅니다. 영종·운서·공항 인접 숙소는 이동 시간과 거리가 길어질 수 있어 예약 가능 시간, 추가 이동비, 숙소 위치(터미널·배후 숙소권)를 사전에 확인합니다. 호텔·게스트하우스 이용 시 프런트 출입 절차와 객실 호수, 체크인 상태를 함께 알려주시면 도착 후 대기를 줄일 수 있습니다.",
    "island": "도서 지역은 일반 도심형과 완전히 다릅니다. 방문 가능 여부 자체를 먼저 확인해야 하며, 차량 이동 시간과 일정, 추가 이동비를 사전에 협의합니다. 선편·교량 이용 여부, 숙소 위치, 예약 가능 시간대에 따라 방문 일정이 달라지므로 여유 있게 미리 문의하시는 것을 권합니다.",
    "residential": "주거 생활권은 아파트 단지와 빌라가 중심이라 단지명, 동·호수, 공동현관 출입 방식 확인이 핵심입니다. 방문 차량 등록과 지상·지하 주차 동선, 관리실 운영 시간에 따라 도착 시간이 달라질 수 있습니다. 야간 예약은 공동현관 야간 출입 방식을 함께 확인합니다.",
    "business": "행정·상권 중심 생활권은 오피스텔과 숙소, 업무용 건물이 섞여 있습니다. 건물 출입증·로비 보안·예약 시간대를 확인하고, 숙소를 이용하는 경우 객실 호수와 프런트 출입 절차를 알려주시면 동선이 빨라집니다. 주중·주말 상권 혼잡도에 따라 이동 시간이 달라질 수 있습니다.",
    "station-area": "역세권 이용은 역명으로 위치를 좁히되, 실제 방문 가능 여부는 주소와 건물 출입 방식까지 함께 확인해야 합니다. 환승 거점 인근은 상권과 주거가 밀집해 같은 역이라도 출구 방향에 따라 거리 차이가 큽니다. 정확한 도로명 주소와 동·호수, 공동현관 위치를 알려주시면 가장 가까운 동선으로 안내합니다.",
}

# 권역 특성 상세(차별화 본문) — 지역명만 바꾼 페이지 방지
TYPE_DETAIL = {
    "newtown": "신도시 권역은 대단지 아파트와 주상복합, 오피스텔, 비즈니스호텔이 한 블록 안에 함께 들어선 경우가 많습니다. 같은 단지 안에서도 동과 출입구가 여러 곳으로 나뉘고 공동현관·엘리베이터가 카드키로 운영되는 곳이 흔해, 방문 전에 동·호수와 공동현관 출입 방식을 정확히 확인해야 도착 동선이 빨라집니다. 지상 차량 통제가 적용되는 단지에서는 방문 차량 등록 절차와 지하주차장 진입 동선을, 업무지구가 인접한 위치에서는 로비 보안과 방문 등록 절차를 함께 살펴보는 것이 좋습니다.",
    "old-town": "원도심 권역은 단독·다세대 주택과 노후 아파트, 상가 주택이 섞여 있어 같은 동이라도 번지에 따라 위치 차이가 큽니다. 골목 진입과 주차 공간이 제한적인 곳이 많으므로 도로명 주소와 건물 외형, 공동현관 위치를 미리 알려주시면 가까운 하차 지점에서 도보로 빠르게 이동할 수 있습니다. 야간에는 골목 조명과 출입 동선을 함께 확인하면 도착 시간을 줄일 수 있습니다.",
    "airport": "공항 권역은 도심과 이동 기준이 완전히 다릅니다. 공항 터미널과 배후 숙소권은 거리가 멀고 이동 시간이 길어질 수 있어, 예약 가능 시간과 추가 이동비, 숙소의 정확한 위치(터미널·인접 호텔·운서 배후권)를 먼저 확인합니다. 비행 일정과 체크인 상태에 따라 가능 시간대가 달라지므로 여유 있게 미리 문의하시는 것이 좋습니다.",
    "island": "도서·외곽 권역은 일반 도심형 안내를 그대로 적용하지 않습니다. 가장 먼저 방문 가능 여부 자체를 확인하고, 차량 이동 시간과 일정, 추가 이동비를 사전에 협의합니다. 교량·선편 이용 여부와 숙소 위치, 예약 가능 시간대에 따라 방문 일정이 크게 달라지므로 충분한 시간을 두고 예약하시는 것을 권합니다.",
    "residential": "주거 권역은 아파트 단지와 빌라가 중심이라 단지명, 동·호수, 공동현관 출입 방식 확인이 가장 중요합니다. 방문 차량 등록과 지상·지하 주차 동선, 관리실 운영 시간에 따라 도착 시간이 달라질 수 있고, 야간 예약은 공동현관 야간 출입 방식을 함께 확인합니다.",
    "business": "행정·상권 권역은 오피스텔과 숙소, 업무용 건물이 섞여 있습니다. 건물 출입증과 로비 보안, 예약 시간대를 확인하고 숙소를 이용하는 경우 객실 호수와 프런트 출입 절차를 알려주시면 동선이 빨라집니다. 주중과 주말의 상권 혼잡도에 따라 이동 시간이 달라질 수 있습니다.",
    "station-area": "역세권 권역은 환승 거점과 상권, 주거가 밀집해 같은 역이라도 출구 방향에 따라 거리 차이가 큽니다. 출구 번호나 노선으로 나누어 안내하지 않고, 정확한 도로명 주소와 동·호수, 공동현관 위치로 가장 가까운 동선을 안내합니다. 상권 인접 지역은 시간대별 혼잡도를 함께 고려합니다.",
}

USECASE_DETAIL_LIST = [
    ("자택 이용", "/use/home/", "공동현관 비밀번호와 정확한 동·호수, 방문 차량 등록 여부를 확인합니다. 단독·다세대는 건물 외형과 골목 동선을 함께 알려주시면 도착이 빨라집니다."),
    ("호텔·숙소 이용", "/use/hotel/", "객실 호수와 프런트 출입 절차, 숙소의 외부 방문 정책을 확인합니다. 체크인 상태와 로비 위치를 미리 알려주시면 대기 시간을 줄일 수 있습니다."),
    ("오피스텔 이용", "/use/officetel/", "관리실 규정과 공동현관·엘리베이터 카드, 방문 주차 가능 여부를 확인합니다. 동·호수와 출입구가 여러 곳인 경우 정확한 출입구를 함께 확인합니다."),
    ("업무지구 이용", "/use/business-district/", "건물 출입증과 로비 보안, 예약 가능 시간대를 확인합니다. 주중 업무 시간과 그 외 시간대의 출입 방식이 다를 수 있습니다."),
]

def usecase_detail_html(type_):
    rows = "".join(f'<li><a href="{u}">{esc(n)}</a> — {esc(d)}</li>' for n,u,d in USECASE_DETAIL_LIST)
    night = "야간 예약은 공동현관·로비의 야간 출입 방식과 예약 마감 시간을 함께 확인합니다." if type_ != "island" else "도서·외곽 야간은 이동 일정과 숙소 위치를 먼저 확인합니다."
    return (f'<p>{USECASE_BANK[type_]}</p><ul>{rows}</ul>'
            f'<p class="muted">{esc(night)} 자세한 기준은 '
            '<a href="/use/night/">야간 예약</a>, <a href="/check/travel-fee/">추가 이동비 기준</a>에서 확인할 수 있습니다.</p>')

def topic_cluster(groups, title="함께 보면 좋은 안내"):
    """롱테일 앵커 텍스트 기반 내부링크 클러스터. groups=[(라벨,[(앵커,url),...]),...]"""
    blocks = []
    for label, links in groups:
        if not links:
            continue
        items = "".join(
            f'<a class="topic-link" href="{esc(u)}">{esc(a)}</a>' for a, u in links)
        blocks.append(f'<div class="group-label">{esc(label)}</div>'
                      f'<div class="topic-grid">{items}</div>')
    if not blocks:
        return ""
    return ('<section class="section alt topic-cluster"><div class="container">'
            f'<div class="section-head"><span class="eyebrow">주제별 빠른 안내</span><h2>{esc(title)}</h2></div>'
            + "".join(blocks) + '</div></section>')

# 코스 기본 금액(스키마 Offer와 화면 표를 한 곳에서 관리)
COURSES = [
    ("60분 코스", 90000, 60, "핵심 부위 위주 가벼운 이완"),
    ("90분 코스", 150000, 90, "전신 균형 표준 구성·아로마 포함"),
    ("120분 코스", 180000, 120, "구석구석 집중하는 프리미엄 구성"),
]

def review_items_for(area=None):
    """area가 주어지면 해당 지역 후기만, 없으면 전체 후기."""
    items = REVIEWS["items"]
    if area:
        return [r for r in items if area and area in (r.get("area") or "")]
    return items

def aggregate_rating_ld(items):
    if not items:
        return None
    vals = [float(r["rating"]) for r in items]
    avg = round(sum(vals) / len(vals), 1)
    return {"@type": "AggregateRating", "ratingValue": avg, "reviewCount": len(items),
            "bestRating": REVIEWS["best"], "worstRating": 1}

def review_ld(items):
    out = []
    for r in items:
        node = {"@type": "Review",
                "reviewRating": {"@type": "Rating", "ratingValue": r["rating"],
                                 "bestRating": REVIEWS["best"], "worstRating": 1},
                "author": {"@type": "Person", "name": r.get("author", "고객")},
                "reviewBody": r["body"]}
        if r.get("date"):
            node["datePublished"] = r["date"]
        out.append(node)
    return out

def stars_html(rating, best=5):
    full = int(round(float(rating)))
    return ('<span class="stars" aria-label="별점 %s점">' % rating
            + "★" * full + '<span class="off">' + "★" * (best - full) + '</span></span>')

def reviews_section(cards_items, heading="고객 후기", more_link=None):
    """실제 후기 카드 + 평균 별점. 요약(평균·건수)은 전체 후기 기준으로 표기."""
    if not cards_items:
        return ""
    allitems = REVIEWS["items"]
    avg = round(sum(float(r["rating"]) for r in allitems) / len(allitems), 1)
    cards = "".join(
        '<div class="review-card">'
        + stars_html(r["rating"], REVIEWS["best"])
        + f'<p class="body">{esc(r["body"])}</p>'
        + f'<div class="meta"><b>{esc(r.get("author","고객"))}</b>'
        + (f'<span>{esc(r.get("area",""))}{" · " if r.get("area") and r.get("date") else ""}{esc(r.get("date",""))}</span>' if (r.get("area") or r.get("date")) else "")
        + '</div></div>'
        for r in cards_items)
    more = (f'<p class="muted" style="text-align:center;margin-top:1.4rem">'
            f'<a href="{esc(more_link)}">전체 후기 {len(allitems)}건 보기 →</a></p>') if more_link else ""
    return ('<section class="section reviews" id="reviews"><div class="container">'
            f'<div class="section-head"><span class="eyebrow">실제 이용 후기</span><h2>{esc(heading)}</h2></div>'
            '<div class="reviews-summary">'
            f'<span class="reviews-score">{avg}</span>{stars_html(avg, REVIEWS["best"])}'
            f'<span class="reviews-count">실제 후기 {len(allitems)}건 · 평균 {avg} / {REVIEWS["best"]}</span></div>'
            f'<div class="review-grid">{cards}</div>{more}</div></section>')

def service_node(page_id, area_served="인천광역시", name_prefix="인천", reviews=None):
    """방문형 관리 서비스 + 실제 가격 Offer(화면 표와 일치). 실제 후기가 있을 때만 Review/Rating 포함."""
    node = {
        "@type": "Service",
        "@id": page_id + "#service",
        "serviceType": "방문형 관리(출장마사지·홈타이)",
        "name": f"{name_prefix} 방문형 관리",
        "provider": {"@id": SITE["url"] + "/#org"},
        "areaServed": {"@type": "City", "name": area_served},
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "KRW",
            "lowPrice": 90000, "highPrice": 180000, "offerCount": 3,
            "offers": [
                {"@type": "Offer", "name": c[0], "price": c[1], "priceCurrency": "KRW",
                 "description": f"{c[2]}분 · {c[3]}",
                 "availability": "https://schema.org/InStock"}
                for c in COURSES
            ],
        },
    }
    if reviews:  # 집계는 전체 실제 후기 기준, review[]는 화면에 노출된 것만
        ar = aggregate_rating_ld(REVIEWS["items"])
        if ar:
            node["aggregateRating"] = ar
            node["review"] = review_ld(reviews)
    return node

def pricing_section():
    """마사지 금액표(코스 기준 기본 금액) — 메인 + 전 지역 페이지 공통."""
    return (
      '<section class="section alt" id="price"><div class="container">'
      '<div class="section-head"><span class="eyebrow">코스 시간으로 보는 기본 요금</span>'
      '<h2>관리 시간 기준 기본 금액</h2>'
      '<p class="lead">관리 시간(60·90·120분)을 기준으로 정리한 기본 금액입니다. 표시되지 않은 별도 비용을 두지 않는 것을 원칙으로 안내합니다.</p></div>'
      '<div class="price-grid">'
        '<div class="price-card"><div class="course">60분 코스</div>'
        '<div class="amount">90,000<span>원</span></div><div class="dur">60분</div>'
        '<div class="desc">핵심 부위 위주 가벼운 이완</div></div>'
        '<div class="price-card featured"><span class="price-pick">추천</span><div class="course">90분 코스</div>'
        '<div class="amount">150,000<span>원</span></div><div class="dur">90분</div>'
        '<div class="desc">전신 균형 표준 구성·아로마 포함</div></div>'
        '<div class="price-card"><div class="course">120분 코스</div>'
        '<div class="amount">180,000<span>원</span></div><div class="dur">120분</div>'
        '<div class="desc">구석구석 집중하는 프리미엄 구성</div></div>'
      '</div>'
      '<p class="muted" style="text-align:center;margin-top:1.2rem">방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다. '
      '<a href="/check/travel-fee/">요금·예약 기준 자세히 보기 →</a></p>'
      '</div></section>')

def customer_notice_html():
    return ('<h2>고객 유의사항</h2>'
            '<p>예약 전에는 방문 주소와 동·호수, 공동현관 또는 건물 출입 방식을 정확히 확인해 주세요. 잘못된 주소나 출입 정보는 '
            '도착 지연의 가장 큰 원인입니다. 예약 변경이나 취소가 필요할 때는 가능한 한 빨리 사전에 연락 주시면 일정을 조정하기 쉽습니다. '
            '외곽·공항·도서 지역은 이동 시간이 길어 예약 가능 시간대가 제한될 수 있으므로 여유 있게 문의하시는 것을 권합니다. '
            '본 사이트는 불법·선정적 서비스를 제공하거나 안내하지 않으며, 모든 안내는 안전한 방문과 정확한 위치 확인을 돕기 위한 것입니다. '
            '자세한 기준은 <a href="/check/customer-notice/">고객 유의사항</a>과 '
            '<a href="/check/change-policy/">예약 변경 기준</a>에서 확인할 수 있습니다.</p>')

def section(title, html_body, idattr=""):
    idp = f' id="{idattr}"' if idattr else ""
    return f'<section class="section"{idp}><div class="container"><div class="prose">' \
           f'<h2>{esc(title)}</h2>{html_body}</div></div></section>'

def checklist_block(items):
    li = "".join(f'<li>{esc(x)}</li>' for x in items)
    return f'<ul class="checklist">{li}</ul>'

COMMON_CHECK = [
    "방문 주소(도로명·동·호수)를 정확히 확인했나요?",
    "공동현관 또는 건물 출입 방식이 있나요?",
    "주차나 차량 이동이 필요한 위치인가요?",
    "예약 가능 시간대를 확인했나요?",
    "추가 이동비가 필요한 외곽·공항·도서 지역인가요?",
    "개인정보 처리 기준을 확인했나요?",
    "불법·선정적 서비스 불가 안내를 확인했나요?",
]

def policy_para():
    return ('<h3>운영 기준 · 개인정보 · 불법 서비스 불가</h3>'
            '<p>본 사이트는 불법·선정적 서비스를 제공하거나 안내하지 않습니다. 허위 후기와 가짜 평점, '
            '과장된 가격 문구를 사용하지 않으며, 모든 지역 안내는 생활권·역세권·이용 장소·예약 전 확인사항을 '
            '근거로 작성합니다. 개인정보는 예약 확인과 연락에 필요한 최소 범위만 이용하며 자세한 기준은 '
            '<a href="/policy/privacy-policy/">개인정보 처리방침</a>과 '
            '<a href="/policy/illegal-service/">불법·선정적 서비스 불가 안내</a>에서 확인할 수 있습니다.</p>')

# ----------------------------------------------------------------------------
# 메인 페이지
# ----------------------------------------------------------------------------
def gu_card(g):
    rep = " · ".join(g["life"][:2])
    st = g["stations"][0] if g["stations"] else "지하철역 없음"
    return (f'<a class="card" href="/{g["slug"]}/">'
            f'<span class="tag">{TYPE_LABEL[g["type"]]}</span>'
            f'<h3>{esc(g["name"])}</h3>'
            f'<p>{esc(rep)} · {esc(st)}</p>'
            f'<span class="card-meta">생활권·예약 전 확인 보기 →</span></a>')

def life_card(l):
    return (f'<a class="card" href="/life/{l["slug"]}/">'
            f'<h3>{esc(l["name"])}</h3><p>{esc(clamp(l["focus"], 60))}</p>'
            f'<span class="card-meta">{TYPE_LABEL[l["type"]]} →</span></a>')

def use_card(u):
    return (f'<a class="card" href="/use/{u["slug"]}/">'
            f'<h3>{esc(u["name"])}</h3><p>{esc(clamp(u["focus"], 56))}</p>'
            f'<span class="card-meta">이용 기준 보기 →</span></a>')

def build_main():
    path = "/"
    title = "인천 출장마사지｜송도·부평·구월·청라·검단 홈타이 지역 안내"
    desc = clamp("인천 출장마사지·홈타이 예약 전 송도·부평·구월·청라·검단·영종 주요 생활권과 이용 기준 안내", 80)

    hero = (
      '<section class="hero"><div class="container"><div class="hero-grid">'
      '<div class="hero-copy">'
      '<span class="eyebrow">인천 방문형 관리 · 권역별 안내</span>'
      '<h1>인천 출장마사지 · 구군별 생활권 예약 안내</h1>'
      '<p class="lead">송도, 부평, 구월, 주안, 청라, 검단, 영종, 인천공항 등 인천 주요 생활권과 '
      '자택·호텔·오피스텔 이용 전 확인사항을 안내합니다.</p>'
      '<div class="hero-cta">'
        '<a class="btn btn-gold" href="#gu">구군 안내</a>'
        '<a class="btn btn-ghost" href="#life">생활권 보기</a>'
        '<a class="btn btn-ghost" href="#use">이용 장소</a>'
        '<a class="btn btn-ghost" href="/check/address/">예약 전 확인</a>'
      '</div>'
      '<ul class="hero-chips"><li>원도심</li><li>신도시</li><li>공항권</li><li>도서권</li>'
      '<li>2026 행정개편 대응</li></ul>'
      '</div>'
      + hero_figure_html() +
      '</div></div></section>')

    # 가격(스크린샷 기준) — 통화 시 확정 안내
    pricing = pricing_section()

    s1 = (
      '<section class="section"><div class="container"><div class="prose">'
      '<h2>인천 출장마사지는 원도심·신도시·공항권·도서권을 나누어 봐야 합니다</h2>'
      '<p>인천은 하나의 도시 안에 성격이 전혀 다른 생활권이 함께 있습니다. 송도·청라·검단은 신도시형 생활권이고, '
      '부평·주안·구월은 원도심과 역세권 성격이 강합니다. 영종·운서·인천공항은 공항권으로 이동 기준이 다르고, '
      '강화와 옹진은 도서권 또는 외곽 이동 기준을 먼저 확인해야 합니다. 이 사이트는 지역명을 나열하는 데 그치지 않고 '
      '구군, 생활권, 지하철역, 이용 장소, 예약 전 확인사항을 함께 안내합니다.</p>'
      f'<p class="muted">권역 구분은 인천광역시의 행정구역을 기준으로 정리했습니다. '
      f'행정구역 안내는 <a href="{AUTHORITY["incheon"][1]}" target="_blank" rel="noopener nofollow">{AUTHORITY["incheon"][0]} ↗</a>에서 확인할 수 있습니다.</p>'
      '</div></div></section>')

    gu_section = ('<section class="section alt" id="gu"><div class="container">'
      '<div class="section-head"><span class="eyebrow">현행 2군·8구</span><h2>인천 구군별 방문 가능 지역</h2>'
      '<p class="lead">각 구의 대표 생활권과 대표 역, 이용 장소 기준을 함께 확인하세요.</p></div>'
      f'<div class="grid grid-3">{"".join(gu_card(g) for g in GUS)}</div></div></section>')

    life_section = ('<section class="section" id="life"><div class="container">'
      '<div class="section-head"><span class="eyebrow">권역별 생활권</span><h2>인천 주요 생활권 안내</h2></div>'
      f'<div class="grid grid-4">{"".join(life_card(l) for l in LIFE)}</div></div></section>')

    use_section = ('<section class="section alt" id="use"><div class="container">'
      '<div class="section-head"><span class="eyebrow">이용 장소</span><h2>이용 장소에 따라 확인할 내용이 다릅니다</h2></div>'
      f'<div class="grid grid-4">{"".join(use_card(u) for u in USES)}</div></div></section>')

    check_section = section("예약 전 확인해야 할 내용",
        checklist_block([c+"" for c in [
            "방문 주소를 정확히 확인했나요?",
            "공동현관 또는 건물 출입 방식이 있나요?",
            "호텔·숙소 이용 가능 여부를 확인했나요?",
            "오피스텔 관리 규정이 있나요?",
            "주차나 차량 이동이 필요한 위치인가요?",
            "공항권 또는 도서 지역 추가 확인이 필요한가요?",
            "예약 가능 시간대를 확인했나요?",
            "개인정보 처리 기준을 확인했나요?",
            "불법·선정적 서비스 불가 안내를 확인했나요?",
        ]]) +
        '<p><a class="btn btn-ghost" href="/check/address/">예약 전 확인 전체 보기 →</a></p>',
        idattr="check")

    reform_section = ('<section class="section alt"><div class="container"><div class="prose">'
      '<h2>인천 행정체제 개편 대응 안내</h2>'
      '<p>인천은 2026년 행정체제 개편을 앞두고 있습니다. 개편 전에는 기존 구군 기준으로 페이지를 운영하고, '
      '제물포구·영종구·검단구 등 개편 대응 페이지는 준비 단계(noindex)로 관리합니다. 개편 이후에는 canonical, '
      'redirect, 사이트맵, 내부링크를 새 행정체계에 맞게 조정합니다. 준비 페이지는 검색 노출 목적이 아니라 행정 변화 대응용입니다.</p>'
      '</div></div></section>')

    ops_section = ('<section class="section"><div class="container"><div class="prose">'
      '<h2>안전한 이용을 위한 운영 기준</h2>'
      '<p>이 사이트는 불법·선정적 서비스를 안내하지 않습니다. 허위 후기, 가짜 평점, 과장된 가격 문구를 사용하지 않으며, '
      '개인정보는 예약 확인과 연락 목적에 필요한 최소 범위만 안내합니다. 모든 지역 페이지는 지역명만 바꾸지 않고 생활권, '
      '역세권, 이용 장소, 예약 전 확인사항을 다르게 구성합니다.</p>'
      + policy_para() +
      whohowwhy_block(
        "이 페이지는 인천 지역 방문형 관리 서비스 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        "인천 행정구역, 주요 생활권, 지하철역, 공항권, 도서권, 이용 장소별 예약 전 확인사항을 기준으로 구성했습니다.",
        "인천에서 방문형 서비스를 찾는 사용자가 자신의 지역과 이용 장소를 안전하게 확인하도록 돕기 위해 작성했습니다.")
      + eeat_block() +
      '</div></div></section>')

    main_faqs = [
        ("인천 전 지역 방문이 가능한가요?", "실제 방문 주소, 가까운 생활권, 예약 가능 시간, 이동 기준을 확인한 뒤 안내합니다."),
        ("송도나 청라 같은 신도시도 확인해야 할 내용이 있나요?", "오피스텔, 공동현관, 주차, 건물 출입 방식, 예약 가능 시간대를 확인해야 합니다."),
        ("부평역이나 주안역처럼 역세권 기준으로도 찾을 수 있나요?", "역명은 위치 설명에 도움이 되지만, 실제 방문 가능 여부는 주소와 건물 출입 방식까지 함께 확인해야 합니다."),
        ("인천공항이나 영종도도 가능한가요?", "공항권은 이동 시간, 숙소 위치, 예약 가능 시간, 추가 이동비를 사전에 확인해야 합니다."),
        ("강화나 옹진 같은 도서 지역은 어떻게 확인하나요?", "도서 지역은 일반 도심형과 다르게 방문 가능 여부와 이동 일정을 먼저 확인해야 합니다."),
        ("개인정보는 어떻게 처리하나요?", "예약 확인과 연락에 필요한 최소 정보만 안내하며, 개인정보 처리방침 페이지로 연결합니다."),
        ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
    ]
    faq_section = ('<section class="section alt"><div class="container"><div class="prose">'
      '<h2>자주 묻는 질문</h2>' + faq_html(main_faqs) + '</div></div></section>')

    main_topics = topic_cluster([
        ("지역·생활권 주제별 안내", [
            ("송도국제도시 오피스텔 방문형 관리 안내", "/life/songdo-international-city/"),
            ("부평역 역세권 출장마사지 예약 안내", "/station/bupyeong-station/"),
            ("구월·인천시청 상권 홈타이 안내", "/life/guwol-incheon-cityhall/"),
            ("청라국제도시 신도시 방문 안내", "/life/cheongna-international-city/"),
            ("검단신도시 입주 단지 방문 안내", "/life/geomdan-newtown/"),
            ("영종·운서 공항권 숙소 이동 안내", "/life/yeongjong-unseo/"),
            ("인천공항 인접 숙소 예약 안내", "/life/incheon-airport/"),
            ("주안·도화 원도심 역세권 안내", "/life/juan-dohwa/"),
            ("강화 도서권 방문 가능 여부 안내", "/life/ganghwa/"),
        ]),
        ("이용 장소별 주제 안내", [
            ("인천 자택 방문 마사지 이용 안내", "/use/home/"),
            ("인천 호텔·숙소 출장마사지 안내", "/use/hotel/"),
            ("인천 오피스텔 홈타이 이용 안내", "/use/officetel/"),
            ("인천 업무지구 예약 이용 안내", "/use/business-district/"),
            ("인천 야간 예약 이용 안내", "/use/night/"),
            ("인천 공항권 이동·이용 안내", "/use/airport-area/"),
        ]),
        ("예약 전 확인 주제 안내", [
            ("인천 출장마사지 방문 주소 확인", "/check/address/"),
            ("인천 추가 이동비·요금 기준 안내", "/check/travel-fee/"),
            ("인천 예약 가능 시간 안내", "/check/time/"),
            ("인천 건물 출입 방식 확인 안내", "/check/building-access/"),
            ("개인정보 처리 기준 안내", "/check/privacy/"),
            ("불법·선정적 서비스 불가 안내", "/check/service-policy/"),
        ]),
    ], title="인천 방문형 관리 주제별 안내")

    reviews_block = reviews_section(REVIEWS["items"], heading="Calmora 실제 이용 후기")

    body = (hero + pricing + s1 + gu_section + life_section + use_section +
            check_section + reviews_block + main_topics + reform_section + ops_section + faq_section)

    crumbs = [("인천 홈", "/")]
    schema = [org_node(),
              {"@type": "WebPage", "@id": SITE["url"]+path+"#webpage", "url": SITE["url"]+path,
               "name": title, "description": desc, "inLanguage": "ko",
               "isPartOf": {"@id": SITE["url"]+"/#org"},
               "dateModified": SITE["today"], "primaryImageOfPage": image_ld(SITE["hero_img"], SITE["hero_alt"])},
              breadcrumb_ld(crumbs), faq_ld(main_faqs), image_ld(SITE["hero_img"], SITE["hero_alt"]),
              service_node(SITE["url"]+path, area_served="인천광역시", name_prefix="인천",
                           reviews=REVIEWS["items"])]

    write_page(path, document(path=path, title=title, description=desc, body=body,
                              schema_nodes=schema))

# ----------------------------------------------------------------------------
# 지역형 상세 페이지 (구군 / 대표지역 / 생활권 / 역세권) 공통 본문
# ----------------------------------------------------------------------------
def region_intro(name, focus, type_):
    return (f'<p>{esc(name)}은(는) {esc(focus)}입니다. {TYPE_LABEL[type_]} 권역의 특성에 맞게 '
            f'방문 주소 확인, 건물 출입 방식, 이용 장소 기준을 다르게 살펴보는 것이 좋습니다. '
            f'아래에서 {esc(name)}의 생활권과 가까운 역, 이용 장소별 확인사항, 예약 전 체크리스트를 함께 정리했습니다.</p>')

def related_links_html(links):
    a = "".join(f'<li><a href="{esc(u)}">{esc(n)}</a></li>' for n, u in links)
    return f'<h3>관련 지역 바로가기</h3><ul>{a}</ul>'

def build_region_page(*, path, h1, title, desc, name, focus, type_,
                      life_list, station_list, crumbs, related, aside_links,
                      authority=None, noindex=False, extra_intro="", faqs=None,
                      who=None, how=None, why=None, og_caption=None):
    type_label = TYPE_LABEL[type_]
    og_caption = og_caption or f"{name} 생활권 방문형 관리 안내 이미지"

    hero = (
      '<section class="hero"><div class="container"><div class="hero-grid">'
      '<div class="hero-copy">'
      f'<span class="eyebrow">인천 {esc(type_label)} · 예약 안내</span>'
      f'<h1>{esc(h1)}</h1>'
      f'<p class="lead">{esc(clamp(focus, 90))}. 자택·호텔·오피스텔 이용 전 확인사항을 함께 안내합니다.</p>'
      '<div class="hero-cta">'
      f'<a class="btn btn-gold" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a>'
      '<a class="btn btn-ghost" href="/check/address/">예약 전 확인</a>'
      '</div></div>'
      + hero_figure_html() +
      '</div></div></section>')

    life_html = ""
    if life_list:
        items = "".join(f'<li><a href="/life/{s}/">{esc(n)}</a></li>' for n, s in life_list)
        life_html = f'<h3>대표 생활권</h3><ul>{items}</ul>'
    station_html = ""
    if station_list:
        items = "".join(f'<li>{esc(s)}</li>' for s in station_list)
        station_html = (f'<h3>가까운 지하철역</h3><ul>{items}</ul>'
                        '<p class="muted">역명은 위치 설명을 돕기 위한 것이며, 출구별·노선별 개별 안내 페이지는 두지 않습니다. '
                        '실제 방문 가능 여부는 주소와 건물 출입 방식까지 함께 확인합니다.</p>')
    else:
        station_html = ('<h3>가까운 지하철역</h3><p>해당 권역은 지하철이 닿지 않아 차량 이동이 기본입니다. '
                        '하차 지점과 도보 동선, 추가 이동비를 사전에 확인합니다.</p>')

    body = (
      hero +
      pricing_section() +
      breadcrumb_html(crumbs) +
      '<section class="section"><div class="container"><div class="content-layout">'
      '<div class="prose">'
      '<h2>지역 개요</h2>' + region_intro(name, focus, type_) + extra_intro +
      f'<h3>{esc(type_label)} 권역의 특성</h3><p>{TYPE_DETAIL[type_]}</p>'
      '<h2>생활권 · 가까운 역</h2>' + life_html + station_html +
      f'<p class="muted">권역 구분: {esc(type_label)}. 신도시·원도심·공항권·도서권에 따라 도착 동선과 확인 항목이 달라집니다.</p>'
      '<h2>이용 장소별 확인 기준</h2>'
      + usecase_detail_html(type_) +
      '<h2>이동·예약 진행 안내</h2>'
      '<p>예약은 전화 통화로 방문 주소와 가까운 생활권, 예약 가능 시간을 확인하면서 진행합니다. 외곽·공항·도서 지역이거나 '
      '이동 거리가 긴 경우 추가 이동비가 발생할 수 있으며, 방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다. '
      '표시되지 않은 별도 비용을 두지 않는 것을 원칙으로 안내합니다.</p>'
      '<h2>예약 전 체크리스트</h2>' + checklist_block(COMMON_CHECK) +
      customer_notice_html() +
      '<h2>운영 기준 안내</h2>' + policy_para() +
      '<h2>자주 묻는 질문</h2>' + faq_html(faqs) +
      '<h2>관련 지역</h2>' + related_links_html(related) +
      whohowwhy_block(who, how, why) + eeat_block() +
      '</div>' +
      aside_html(f"{name} 주변 안내", aside_links, authority) +
      '</div></div></section>')

    # 롱테일 내부링크 클러스터(지역명 접두 앵커)
    use_links = [
        (f"{name} 자택 방문 마사지 안내", "/use/home/"),
        (f"{name} 호텔·숙소 출장마사지 안내", "/use/hotel/"),
        (f"{name} 오피스텔 홈타이 이용 안내", "/use/officetel/"),
        (f"{name} 업무지구 예약 이용 안내", "/use/business-district/"),
        (f"{name} 역세권 방문형 관리 안내", "/use/station-area/"),
        (f"{name} 야간 예약 이용 안내", "/use/night/"),
    ]
    check_links = [
        (f"{name} 출장마사지 방문 주소 확인", "/check/address/"),
        (f"{name} 추가 이동비·요금 기준", "/check/travel-fee/"),
        (f"{name} 예약 가능 시간 안내", "/check/time/"),
        (f"{name} 건물 출입 방식 확인", "/check/building-access/"),
        ("개인정보 처리 기준 안내", "/check/privacy/"),
    ]
    area_links = [(f"{ln} 생활권 방문형 관리 안내", f"/life/{ls}/") for ln, ls in life_list]
    for st in station_list:
        if st in STATION_SLUG:
            area_links.append((f"{st} 역세권 예약 안내", f"/station/{STATION_SLUG[st]}/"))
    cluster = topic_cluster(
        [(f"{name} 이용 장소별 안내", use_links),
         (f"{name} 예약 전 확인", check_links),
         ("주변 지역·생활권 안내", area_links)],
        title=f"{name} 방문형 관리 주제별 안내")

    # 지역 후기(있으면) 우선, 없으면 전체 후기 일부를 노출 — 화면 노출분만 review[]로 마크업
    area_reviews = review_items_for(name)
    shown_reviews = area_reviews if area_reviews else REVIEWS["items"][:6]
    reviews_block = reviews_section(shown_reviews, heading=f"Calmora 실제 이용 후기",
                                    more_link="/#reviews")
    body = body + reviews_block + cluster

    schema = [org_node(),
              {"@type": "WebPage", "@id": SITE["url"]+path+"#webpage", "url": SITE["url"]+path,
               "name": title, "description": desc, "inLanguage": "ko",
               "isPartOf": {"@id": SITE["url"]+"/#org"}, "dateModified": SITE["today"],
               "primaryImageOfPage": image_ld(SITE["hero_img"], og_caption)},
              breadcrumb_ld(crumbs), faq_ld(faqs), image_ld(SITE["hero_img"], og_caption),
              service_node(SITE["url"]+path, area_served=name, name_prefix=name,
                           reviews=shown_reviews)]
    write_page(path, document(path=path, title=title, description=desc, body=body,
                              schema_nodes=schema, noindex=noindex))

# ---- 구군 페이지 ----
def build_gu(g):
    name = g["name"]; slug = g["slug"]
    path = f"/{slug}/"
    rep_life = " · ".join(g["life"][:2])
    h1 = f"{name} 출장마사지 · {rep_life} 생활권 예약 안내"
    title = f"{name} 출장마사지｜{rep_life} 생활권·이용 안내 - {SITE['brand']}"
    desc = clamp(f"{name} 출장마사지·홈타이 {rep_life} 생활권과 자택·호텔·오피스텔 이용 전 확인사항 안내", 80)

    # 해당 구의 생활권 링크 매핑
    life_list = [(l["name"], l["slug"]) for l in LIFE if l["gu"] == slug]
    # 대표지역
    gu_areas = [a for a in AREAS if a["gu"] == slug]
    related = [(a["name"]+" 안내", f"/{slug}/{a['slug']}/") for a in gu_areas[:4]]
    related += [("예약 전 방문 주소 확인", "/check/address/"),
                ("이용 장소별 안내", "/use/home/")]
    aside_links = [(l["name"], f"/life/{l['slug']}/") for l in LIFE if l["gu"] == slug][:5] \
                  or [("인천 홈", "/")]
    aside_links += [("추가 이동비 기준", "/check/travel-fee/")]

    authority = None
    if slug == "ganghwa-gun": authority = [AUTHORITY["ganghwa"], AUTHORITY["incheon"]]
    elif slug == "ongjin-gun": authority = [AUTHORITY["ongjin"], AUTHORITY["incheon"]]
    elif g["type"] == "airport": authority = [AUTHORITY["airport"], AUTHORITY["incheon"]]
    else: authority = [AUTHORITY["incheon"], AUTHORITY["subway"]]

    extra = ""
    if slug == "jung-gu":
        extra = ('<p>중구는 동인천·제물포 원도심과 영종·운서·인천공항 공항권이 한 행정구역에 함께 있어 권역을 분리해 확인해야 합니다. '
                 '원도심은 도로명 주소와 골목 동선을, 공항권은 이동 시간과 숙소 위치, 추가 이동비를 먼저 봅니다.</p>')
    elif slug == "seo-gu":
        extra = ('<p>서구는 청라국제도시와 검단신도시가 빠르게 확장 중이며, 2026년 검단구 분리 대응 권역입니다. '
                 '신규 입주 단지는 동·호수와 공동현관, 주차 등록 절차 확인이 중요합니다.</p>')
    elif slug in ("ganghwa-gun", "ongjin-gun"):
        extra = ('<p>이 권역은 도심형 안내를 그대로 적용하지 않습니다. 방문 가능 여부와 이동 일정, 추가 이동비를 '
                 '가장 먼저 확인하고, 섬·외곽 특성에 맞춰 예약 시간을 여유 있게 잡습니다.</p>')

    faqs = [
        (f"{name} 전 지역 방문이 가능한가요?", "방문 주소와 가까운 생활권, 예약 가능 시간, 이동 기준을 확인한 뒤 안내합니다."),
        (f"{name}에서 호텔·오피스텔도 이용할 수 있나요?", "객실 호수와 프런트 출입, 관리실 규정, 공동현관 출입 방식을 함께 확인하면 도착이 빨라집니다."),
        ("추가 이동비는 어떻게 확인하나요?", "이동 거리와 시간대, 외곽·공항·도서 여부에 따라 달라지며 예약 시 안내합니다."),
        ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
    ]
    build_region_page(
        path=path, h1=h1, title=title, desc=desc, name=name, focus=g["focus"], type_=g["type"],
        life_list=life_list, station_list=g["stations"],
        crumbs=[("인천 홈","/"),(name, path)],
        related=related, aside_links=aside_links, authority=authority, extra_intro=extra, faqs=faqs,
        who=f"이 페이지는 인천 {name} 지역 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        how=f"{name}의 행정구역, 대표 생활권, 가까운 역, 이용 장소별 예약 전 확인사항을 기준으로 구성했습니다.",
        why=f"{name}에서 방문형 서비스를 찾는 사용자가 지역과 이용 장소를 안전하게 확인하도록 돕기 위해 작성했습니다.",
        og_caption=f"{name} 생활권 방문형 관리 안내 이미지")

# ---- 대표지역 페이지 ----
def build_area(a):
    name = a["name"]; gu = GU_BY_SLUG[a["gu"]]
    path = f"/{a['gu']}/{a['slug']}/"
    h1 = f"{name} 출장마사지 · {a['life']} 예약 안내"
    title = f"{name} 출장마사지｜{a['life']} 생활권 이용 안내 - {SITE['brand']}"
    desc = clamp(f"{name} 출장마사지·홈타이 {a['life']} 생활권과 자택·호텔·오피스텔 이용 전 확인사항 안내", 80)
    related = [(gu["name"]+" 전체", f"/{a['gu']}/"),
               (a["life"]+" 생활권", f"/life/{a['lifeslug']}/"),
               ("예약 전 방문 주소 확인", "/check/address/"),
               ("추가 이동비 기준", "/check/travel-fee/")]
    aside_links = [(gu["name"], f"/{a['gu']}/"),
                   (a["life"]+" 생활권", f"/life/{a['lifeslug']}/"),
                   ("이용 장소별 안내", "/use/hotel/")]
    authority = [AUTHORITY["airport"], AUTHORITY["incheon"]] if a["type"]=="airport" else [AUTHORITY["incheon"], AUTHORITY["subway"]]
    faqs = [
        (f"{name} 어디까지 방문하나요?", "정확한 도로명 주소와 동·호수, 건물 출입 방식을 확인한 뒤 가장 가까운 동선으로 안내합니다."),
        (f"{name} 신도시·오피스텔도 가능한가요?", "공동현관·관리실 규정·주차 동선을 확인하면 도착이 빨라집니다." if a["type"] in ("newtown","airport") else "단지명과 동·호수, 공동현관 출입 방식을 확인합니다."),
        ("개인정보는 어떻게 처리하나요?", "예약 확인과 연락에 필요한 최소 정보만 이용하며 개인정보 처리방침을 따릅니다."),
    ]
    build_region_page(
        path=path, h1=h1, title=title, desc=desc, name=name, focus=a["focus"], type_=a["type"],
        life_list=[(a["life"], a["lifeslug"])], station_list=a["stations"],
        crumbs=[("인천 홈","/"),(gu["name"], f"/{a['gu']}/"),(name, path)],
        related=related, aside_links=aside_links, authority=authority, faqs=faqs,
        who=f"이 페이지는 {name} 지역 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        how=f"{name}의 상위 구({gu['name']}), {a['life']} 생활권, 가까운 역, 이용 장소 기준을 반영했습니다.",
        why=f"{name}에서 방문형 서비스를 찾는 사용자가 위치와 이용 장소를 안전하게 확인하도록 돕기 위해 작성했습니다.",
        og_caption=f"{name} 인근 생활권 안내 이미지")

# ---- 생활권 페이지 ----
def build_life(l):
    name = l["name"]; gu = GU_BY_SLUG[l["gu"]]
    path = f"/life/{l['slug']}/"
    h1 = f"{name} 출장마사지 생활권 안내"
    title = f"{name} 출장마사지｜생활권·이용 기준 안내 - {SITE['brand']}"
    desc = clamp(f"{name} 출장마사지·홈타이 생활권과 가까운 역, 자택·호텔·오피스텔 이용 전 확인사항 안내", 80)
    related = [(gu["name"]+" 전체", f"/{l['gu']}/"),
               ("예약 전 방문 주소 확인", "/check/address/"),
               ("추가 이동비 기준", "/check/travel-fee/"),
               ("문의하기", "/policy/contact/")]
    # 관련 대표지역
    for a in AREAS:
        if a["lifeslug"] == l["slug"]:
            related.insert(1, (a["name"]+" 안내", f"/{a['gu']}/{a['slug']}/"))
    aside_links = [(gu["name"], f"/{l['gu']}/"),
                   ("이용 장소별 안내", "/use/hotel/"),
                   ("예약 가능 시간", "/check/time/")]
    authority = [AUTHORITY["airport"], AUTHORITY["incheon"]] if l["type"]=="airport" else \
                ([AUTHORITY["ganghwa"], AUTHORITY["incheon"]] if l["slug"]=="ganghwa" else
                 ([AUTHORITY["ongjin"], AUTHORITY["incheon"]] if l["slug"]=="ongjin-islands" else
                  [AUTHORITY["incheon"], AUTHORITY["subway"]]))
    faqs = [
        (f"{name}은 어떤 생활권인가요?", f"{clamp(l['focus'], 70)} 권역입니다."),
        ("예약 전 무엇을 확인하나요?", "방문 주소와 건물 출입 방식, 예약 가능 시간, 추가 이동비 여부를 확인합니다."),
        ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
    ]
    build_region_page(
        path=path, h1=h1, title=title, desc=desc, name=name, focus=l["focus"], type_=l["type"],
        life_list=[], station_list=l["stations"],
        crumbs=[("인천 홈","/"),("생활권","/#life"),(name, path)],
        related=related, aside_links=aside_links, authority=authority, faqs=faqs,
        who=f"이 페이지는 {name} 생활권 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        how=f"{name}의 포함 구역, 가까운 역, 대표 이용 장소, 예약 전 확인사항을 기준으로 구성했습니다.",
        why=f"{name} 생활권에서 방문형 서비스를 찾는 사용자가 안전하게 위치와 이용 장소를 확인하도록 돕기 위해 작성했습니다.",
        og_caption=f"{name} 생활권 안내 이미지")

# ---- 역세권 페이지 ----
def build_station(s):
    name = s["name"]; gu = GU_BY_SLUG[s["gu"]]
    path = f"/station/{s['slug']}/"
    h1 = f"{name} 출장마사지 · 역세권 예약 안내"
    title = f"{name} 출장마사지｜역세권 이용 안내 - {SITE['brand']}"
    desc = clamp(f"{name} 인근 출장마사지·홈타이 역세권 생활권과 자택·호텔·오피스텔 이용 전 확인사항 안내", 80)
    transfer_txt = "환승역으로 출구 방향에 따라 거리 차이가 큽니다." if s["transfer"] else "단일 노선역으로 출구 방향과 도보 동선을 확인하면 도착이 빨라집니다."
    extra = (f'<p>{esc(name)}은(는) {esc(gu["name"])} {esc(s["life"])} 생활권에 가깝습니다. {esc(transfer_txt)} '
             '출구별 페이지나 노선별 페이지를 따로 만들지 않는 이유는, 같은 역이라도 실제 방문 가능 여부가 출구가 아니라 '
             '도로명 주소와 건물 출입 방식으로 결정되기 때문입니다.</p>')
    related = [(gu["name"]+" 전체", f"/{s['gu']}/"),
               (s["life"]+" 생활권", f"/life/{s['lifeslug']}/"),
               ("역세권 이용 안내", "/use/station-area/"),
               ("예약 전 방문 주소 확인", "/check/address/")]
    aside_links = [(gu["name"], f"/{s['gu']}/"),
                   (s["life"]+" 생활권", f"/life/{s['lifeslug']}/"),
                   ("추가 이동비 기준", "/check/travel-fee/")]
    faqs = [
        (f"{name} 몇 번 출구로 가야 하나요?", "출구보다 정확한 도로명 주소와 건물 출입 방식이 중요합니다. 주소를 알려주시면 가장 가까운 동선으로 안내합니다."),
        (f"{name} 인근 호텔·오피스텔도 가능한가요?", "객실 호수·프런트 출입 또는 관리실 규정·공동현관 출입 방식을 함께 확인합니다."),
        ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
    ]
    build_region_page(
        path=path, h1=h1, title=title, desc=desc, name=name,
        focus=f"{gu['name']} {s['life']} 생활권에 가까운 역세권", type_=s["type"],
        life_list=[(s["life"], s["lifeslug"])], station_list=[name],
        crumbs=[("인천 홈","/"),("지하철역","/#station"),(name, path)],
        related=related, aside_links=aside_links,
        authority=[AUTHORITY["subway"], AUTHORITY["incheon"]], extra_intro=extra, faqs=faqs,
        who=f"이 페이지는 {name} 역세권 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        how=f"{name}의 가까운 구군({gu['name']}), {s['life']} 생활권, 환승 여부, 이용 장소 기준을 반영했습니다.",
        why=f"{name} 인근에서 방문형 서비스를 찾는 사용자가 위치를 정확히 확인하도록 돕기 위해 작성했습니다.",
        og_caption=f"{name} 인근 생활권 안내 이미지")

# ---- 이용 장소 페이지 ----
def build_use(u):
    name = u["name"]; path = f"/use/{u['slug']}/"
    h1 = f"인천 {name} 출장마사지 이용 안내"
    title = f"인천 {name}｜출장마사지 이용 기준 안내 - {SITE['brand']}"
    desc = clamp(f"인천 {name} 출장마사지·홈타이 방문 주소·건물 출입·예약 시간·개인정보 확인 안내", 80)
    type_map = {"home":"residential","hotel":"business","officetel":"newtown","business-district":"business",
                "station-area":"station-area","night":"residential","airport-area":"airport","island-area":"island"}
    type_ = type_map[u["slug"]]
    hero = ('<section class="hero"><div class="container"><div class="hero-grid">'
      '<div class="hero-copy">'
      '<span class="eyebrow">이용 장소 안내</span>'
      f'<h1>{esc(h1)}</h1>'
      f'<p class="lead">{esc(clamp(u["focus"], 90))}.</p>'
      f'<div class="hero-cta"><a class="btn btn-gold" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a>'
      '<a class="btn btn-ghost" href="/check/address/">예약 전 확인</a></div></div>'
      + hero_figure_html() + '</div></div></section>')
    faqs = [
        (f"인천 {name} 예약 시 무엇을 확인하나요?", f"{clamp(u['focus'],60)}을(를) 중심으로 확인합니다."),
        ("주소만 알려주면 되나요?", "도로명 주소와 함께 동·호수, 공동현관·프런트 출입 방식을 알려주시면 도착이 빨라집니다."),
        ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
    ]
    body = (hero + pricing_section() + breadcrumb_html([("인천 홈","/"),("이용 장소","/#use"),(name, path)]) +
      '<section class="section"><div class="container"><div class="content-layout"><div class="prose">'
      f'<h2>{esc(name)}란</h2><p>인천에서 {esc(u["focus"])} 유형입니다. 인천은 신도시·원도심·공항권·도서권의 건물 형태와 출입 방식이 '
      f'서로 달라, {esc(name)}을(를) 이용할 때 확인할 항목도 권역마다 차이가 있습니다. 정확한 위치와 출입 정보를 미리 확인할수록 '
      '도착 동선이 빨라지고 예약이 원활하게 진행됩니다. 아래에서 권역별 차이와 방문 주소·건물 출입 확인 방법, 예약 진행 안내를 함께 정리했습니다.</p>'
      '<h2>인천에서 이 장소를 확인해야 하는 이유</h2>'
      f'<p>{USECASE_BANK[type_]}</p>'
      f'<p>{TYPE_DETAIL[type_]}</p>'
      '<h2>권역별 차이</h2>'
      '<ul><li><a href="/life/songdo-international-city/">신도시(송도·청라·검단)</a> — 오피스텔·공동현관·주차 등록</li>'
      '<li><a href="/life/bupyeong-station-market/">원도심·역세권(부평·주안)</a> — 도로명 주소·골목 동선</li>'
      '<li><a href="/life/incheon-airport/">공항권(영종·인천공항)</a> — 이동 시간·추가 이동비</li>'
      '<li><a href="/life/ganghwa/">도서권(강화·옹진)</a> — 방문 가능 여부·이동 일정</li></ul>'
      '<h2>방문 주소·건물 출입 확인</h2>'
      '<ul><li>도로명 주소와 동·호수를 정확히 확인합니다.</li>'
      '<li>공동현관 비밀번호, 프런트·경비 출입, 엘리베이터 카드 사용 여부를 확인합니다.</li>'
      '<li>주차 또는 차량 이동이 필요한 위치인지 확인합니다.</li>'
      '<li>예약 가능 시간대와 마감 시간을 확인합니다.</li></ul>'
      '<h2>예약 진행 방법</h2>'
      '<p>예약은 전화 통화로 진행하며, 방문 주소와 가까운 생활권, 예약 가능 시간을 함께 확인합니다. 외곽·공항·도서 지역이거나 '
      '이동 거리가 긴 경우 추가 이동비가 발생할 수 있고, 방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다. '
      '표시되지 않은 별도 비용을 두지 않는 것을 원칙으로 안내합니다. 야간 이용은 건물의 야간 출입 방식과 마감 시간을 함께 확인합니다.</p>'
      '<h2>관련 예약 전 확인</h2>'
      '<ul><li><a href="/check/address/">방문 주소 확인</a> · <a href="/check/building-access/">건물 출입 방식</a></li>'
      '<li><a href="/check/time/">예약 가능 시간</a> · <a href="/check/travel-fee/">추가 이동비 기준</a></li></ul>'
      '<h2>관련 생활권·구군</h2>'
      '<p>인천 전역에서 이용 장소 기준을 적용할 수 있습니다. 권역별 대표 생활권으로 바로 이동해 가까운 지역의 안내를 확인하세요.</p>'
      '<ul><li>신도시 — <a href="/life/songdo-international-city/">송도국제도시</a>, '
      '<a href="/life/cheongna-international-city/">청라국제도시</a>, <a href="/life/geomdan-newtown/">검단신도시</a></li>'
      '<li>원도심·역세권 — <a href="/life/bupyeong-station-market/">부평역·부평시장</a>, '
      '<a href="/life/juan-dohwa/">주안·도화</a>, <a href="/life/guwol-incheon-cityhall/">구월·인천시청</a></li>'
      '<li>공항·도서 — <a href="/life/incheon-airport/">인천공항</a>, '
      '<a href="/life/ganghwa/">강화</a>, <a href="/life/ongjin-islands/">옹진 도서</a></li>'
      '<li><a href="/">인천 구군 전체 보기</a></li></ul>'
      '<h2>예약 전 체크리스트</h2>' + checklist_block(COMMON_CHECK) +
      '<h2>운영 기준 안내</h2>' + policy_para() +
      customer_notice_html() +
      '<h2>자주 묻는 질문</h2>' + faq_html(faqs) +
      whohowwhy_block(
        f"이 페이지는 인천 이용 장소 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        f"인천에서 {name}을(를) 이용할 때의 주소·출입·시간·개인정보 확인 기준을 정리했습니다.",
        f"이용 장소에 따라 달라지는 확인사항을 사용자가 안전하게 점검하도록 돕기 위해 작성했습니다.")
      + eeat_block() + '</div>' +
      aside_html("이용 장소 바로가기",
                 [(x["name"], f"/use/{x['slug']}/") for x in USES if x["slug"]!=u["slug"]][:6],
                 [AUTHORITY["privacy"]]) +
      '</div></div></section>')
    schema = [org_node(),
              {"@type":"WebPage","@id":SITE["url"]+path+"#webpage","url":SITE["url"]+path,"name":title,
               "description":desc,"inLanguage":"ko","isPartOf":{"@id":SITE["url"]+"/#org"},
               "dateModified":SITE["today"],"primaryImageOfPage":image_ld(SITE["hero_img"], f"인천 {name} 안내 이미지")},
              breadcrumb_ld([("인천 홈","/"),("이용 장소","/#use"),(name, path)]),
              faq_ld(faqs), image_ld(SITE["hero_img"], f"인천 {name} 안내 이미지")]
    write_page(path, document(path=path, title=title, description=desc, body=body, schema_nodes=schema))

# ---- 예약 전 확인 페이지 ----
def build_check(c):
    name = c["name"]; path = f"/check/{c['slug']}/"
    h1 = f"인천 출장마사지 {c['h1']}"
    title = f"인천 출장마사지 {c['name']}｜예약 전 확인 - {SITE['brand']}"
    desc = clamp(f"인천 출장마사지·홈타이 예약 전 {c['name']} 안내. 구군·생활권·권역별 확인 기준 정리", 80)
    hero = ('<section class="hero"><div class="container"><div class="hero-grid">'
      '<div class="hero-copy"><span class="eyebrow">예약 전 확인</span>'
      f'<h1>{esc(h1)}</h1><p class="lead">{esc(clamp(c["focus"],90))}.</p>'
      f'<div class="hero-cta"><a class="btn btn-gold" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a></div></div>'
      + hero_figure_html() + '</div></div></section>')
    body = (hero + pricing_section() + breadcrumb_html([("인천 홈","/"),("예약 전 확인","/check/address/"),(name, path)]) +
      '<section class="section"><div class="container"><div class="content-layout"><div class="prose">'
      f'<h2>{esc(name)} 안내</h2><p>{esc(c["focus"])} 단계입니다. 인천은 신도시·원도심·공항권·도서권에 따라 건물 형태와 '
      f'이동 기준이 달라, {esc(name)}도 권역별로 확인 포인트가 다릅니다.</p>'
      '<h2>인천에서 왜 중요한가요</h2>'
      '<p>같은 인천이라도 송도·청라 같은 신도시는 오피스텔·공동현관 중심, 부평·주안 같은 원도심·역세권은 골목과 출입 방식 중심, '
      '영종·공항권은 이동 시간 중심, 강화·옹진 같은 도서권은 방문 가능 여부 중심으로 확인합니다. 인천은 행정구역 하나 안에서도 '
      '생활권 성격이 크게 달라, 같은 확인 항목이라도 권역에 따라 우선순위가 달라집니다.</p>'
      '<h2>이용 장소별 확인 포인트</h2>' + usecase_detail_html("business") +
      '<h2>이동·추가 이동비</h2>'
      '<p>외곽·공항·도서 지역이거나 이동 거리가 긴 경우 추가 이동비가 발생할 수 있습니다. 방문 지역과 시간대, 이동 거리에 따라 '
      '최종 금액은 통화 시 확정되며, 표시되지 않은 별도 비용을 두지 않는 것을 원칙으로 안내합니다.</p>'
      '<h3>권역별 차이</h3>'
      '<ul><li><a href="/life/songdo-international-city/">신도시(송도·청라·검단)</a> — 오피스텔·주차·공동현관</li>'
      '<li><a href="/life/bupyeong-station-market/">원도심·역세권(부평·주안·구월)</a> — 도로명 주소·골목 동선</li>'
      '<li><a href="/life/incheon-airport/">공항권(영종·인천공항)</a> — 이동 시간·추가 이동비</li>'
      '<li><a href="/life/ganghwa/">도서권(강화·옹진)</a> — 방문 가능 여부·이동 일정</li></ul>'
      '<h2>이용 장소별 확인</h2>'
      '<p>같은 확인 단계라도 자택·호텔·오피스텔·업무지구에 따라 점검 항목이 달라집니다. 자택은 공동현관과 동·호수, 호텔은 객실 호수와 '
      '프런트 출입, 오피스텔은 관리실 규정과 주차, 업무지구는 출입증과 로비 보안을 함께 확인합니다.</p>'
      '<ul><li><a href="/use/home/">자택 이용</a> · <a href="/use/hotel/">호텔·숙소 이용</a></li>'
      '<li><a href="/use/officetel/">오피스텔 이용</a> · <a href="/use/business-district/">업무지구 이용</a></li></ul>'
      '<h2>예약 전 체크리스트</h2>' + checklist_block(COMMON_CHECK) +
      '<h2>운영 기준 안내</h2>' + policy_para() +
      '<h2>예약 진행 안내</h2>'
      '<p>예약은 전화 통화로 진행하며, 위 확인 항목을 함께 점검합니다. 정확한 주소와 출입 정보가 준비되면 도착 동선이 빨라지고 '
      '예약이 원활하게 진행됩니다. 외곽·공항·도서 지역은 이동 시간이 길어 예약 가능 시간대가 제한될 수 있으므로 여유 있게 문의해 주세요. '
      '예약 변경·취소는 가능한 한 빨리 사전에 연락 주시면 일정 조정이 쉽습니다.</p>'
      '<h2>자주 묻는 질문</h2>' + faq_html([
          (f"{name}은 왜 확인하나요?", f"{clamp(c['focus'],60)} 때문에 도착 동선과 예약 진행이 달라집니다."),
          ("권역마다 다른가요?", "네. 신도시·원도심·공항권·도서권에 따라 확인 항목이 다릅니다."),
          ("개인정보는 안전한가요?", "예약 확인과 연락에 필요한 최소 정보만 이용합니다."),
          ("불법·선정적 서비스도 가능한가요?", "불법·선정적 서비스는 제공하거나 안내하지 않습니다."),
      ]) +
      whohowwhy_block(
        "이 페이지는 인천 예약 전 확인 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        f"{name}을(를) 구군·생활권·권역별로 어떻게 확인하는지 기준을 정리했습니다.",
        "예약 전 확인 단계에서 사용자가 안전하게 점검하도록 돕기 위해 작성했습니다.")
      + eeat_block() + '</div>' +
      aside_html("예약 전 확인 바로가기",
                 [(x["name"], f"/check/{x['slug']}/") for x in CHECKS if x["slug"]!=c["slug"]],
                 [AUTHORITY["privacy"]]) +
      '</div></div></section>')
    schema = [org_node(),
              {"@type":"WebPage","@id":SITE["url"]+path+"#webpage","url":SITE["url"]+path,"name":title,
               "description":desc,"inLanguage":"ko","isPartOf":{"@id":SITE["url"]+"/#org"},"dateModified":SITE["today"]},
              breadcrumb_ld([("인천 홈","/"),("예약 전 확인","/check/address/"),(name, path)]),
              faq_ld([("개인정보는 안전한가요?","예약 확인과 연락에 필요한 최소 정보만 이용합니다.")]),
              image_ld(SITE["hero_img"], f"인천 {name} 안내 이미지")]
    write_page(path, document(path=path, title=title, description=desc, body=body, schema_nodes=schema))

# ---- 운영 기준(정책) 페이지 ----
def policy_body(slug):
    if slug == "privacy-policy":
        return ('<p>본 사이트는 예약 확인과 연락에 필요한 최소한의 개인정보만 이용합니다. 수집 항목은 예약자가 직접 제공하는 '
                '연락처와 방문 주소 등으로 한정하며, 마케팅 목적의 별도 수집·제3자 제공·국외 이전을 하지 않습니다. 통화 과정에서 '
                '확인된 정보는 해당 예약을 처리하는 목적 외로 사용하지 않습니다.</p>'
                '<h3>수집 항목</h3><ul><li>예약자 연락처(전화번호)</li><li>방문 주소 및 건물 출입 관련 정보</li><li>예약 일시·시간대</li></ul>'
                '<h3>이용 목적</h3><ul><li>예약 접수 및 방문 일정 확인</li><li>방문 위치·이동 동선 안내</li><li>예약 변경·취소 연락</li></ul>'
                '<h3>보유 및 파기</h3><p>이용 목적이 끝나면 관련 정보를 지체 없이 파기합니다. 법령에 따라 보관이 필요한 경우 해당 기간 동안만 보관합니다.</p>'
                '<h3>이용자 권리</h3><p>이용자는 자신의 개인정보에 대한 열람·정정·삭제·처리정지를 요청할 수 있으며, 요청 시 지체 없이 조치합니다.</p>'
                f'<p class="muted">개인정보 관련 일반 기준은 <a href="{AUTHORITY["privacy"][1]}" target="_blank" rel="noopener nofollow">{AUTHORITY["privacy"][0]} ↗</a>를 참고할 수 있습니다.</p>')
    if slug == "service-standard":
        return ('<p>본 사이트는 인천 지역 방문형 관리 안내를 제공합니다. 모든 안내는 생활권·역세권·이용 장소·예약 전 확인사항을 '
                '근거로 작성하며, 방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다.</p>'
                '<h3>이용 기준</h3><ul><li>실제 방문 가능 여부는 주소와 건물 출입 방식으로 확인합니다.</li>'
                '<li>외곽·공항·도서 지역은 추가 이동비가 발생할 수 있습니다.</li>'
                '<li>표시되지 않은 별도 비용을 두지 않는 것을 원칙으로 합니다.</li>'
                '<li>예약 가능 시간대와 마감 시간은 통화 시 안내합니다.</li></ul>'
                '<h3>예약 진행</h3><p>예약은 전화 통화로 진행하며, 방문 주소와 가까운 생활권, 예약 가능 시간을 확인합니다. '
                '예약 변경·취소는 사전 연락을 기준으로 안내합니다. 자세한 내용은 '
                '<a href="/check/change-policy/">예약 변경 기준</a>과 <a href="/check/time/">예약 가능 시간</a>에서 확인할 수 있습니다.</p>'
                '<h3>권역별 안내</h3><p>인천은 신도시·원도심·공항권·도서권의 이동 기준이 달라, 예약 전 확인 항목도 권역마다 다릅니다. '
                '<a href="/">인천 홈</a>에서 구군·생활권별 안내를 확인할 수 있습니다.</p>')
    if slug == "illegal-service":
        return ('<p>본 사이트는 불법·선정적 서비스를 제공하거나 안내하지 않습니다. 성매매 등 불법 행위를 암시하는 표현, '
                '허위 후기, 가짜 평점, 과장된 가격 문구를 사용하지 않습니다. 이 기준은 모든 지역 페이지와 콘텐츠에 동일하게 적용됩니다.</p>'
                '<h3>금지 사항</h3><ul><li>불법·선정적 서비스 제공 및 암시</li><li>허위 후기·가짜 평점·허위 평점</li>'
                '<li>지역명만 바꾼 대량 저품질 페이지</li><li>키워드 반복(스터핑)·과장 문구</li>'
                '<li>출구별·노선별로 쪼갠 저가치 페이지</li><li>상위노출 보장 등 과장 표현</li></ul>'
                '<h3>운영 원칙</h3><p>본 사이트는 사용자가 실제로 확인할 정보를 먼저 제공하며, 생활권·역세권·이용 장소·예약 전 확인사항을 '
                '근거로 안내합니다. 개인정보는 예약 확인과 연락 목적에 필요한 최소 범위만 이용합니다. 관련 기준은 '
                '<a href="/policy/content-standard/">콘텐츠 작성 기준</a>과 <a href="/policy/privacy-policy/">개인정보 처리방침</a>에서 확인할 수 있습니다.</p>')
    if slug == "content-standard":
        return ('<p>모든 색인 페이지는 지역명만 바꾸지 않고 생활권·역세권·이용 장소·예약 전 확인사항을 다르게 구성합니다. '
                '신도시·원도심·공항권·도서권의 특성을 반영하며, 본문은 사용자가 실제로 확인할 정보를 먼저 제공합니다. '
                '어디서나 볼 수 있는 일반 요약이 아니라, 인천 권역별 방문·이동 기준이라는 실제 확인 정보를 담는 것을 원칙으로 합니다.</p>'
                '<h3>작성 원칙</h3><ul><li>권역별 차별화(신도시/원도심/공항/도서)</li>'
                '<li>번호동은 대표 지역·생활권으로 묶고 개별 URL을 만들지 않음</li>'
                '<li>출구별·노선별 역 페이지를 만들지 않음</li>'
                '<li>본문 품질과 검색 의도가 분명한 페이지부터 단계적으로 색인</li>'
                '<li>키워드 반복·과장 표현·상위노출 보장 문구 금지</li></ul>'
                '<h3>품질 점검</h3><p>본문 길이, 중복 위험, 내부링크 정확성, 메타 정보 중복 여부를 주기적으로 점검하고, '
                '검색 수요와 본문 품질이 확보된 페이지부터 단계적으로 공개합니다. 준비 중이거나 본문이 부족한 페이지는 noindex로 관리합니다.</p>'
                '<h3>책임</h3><p>모든 색인 페이지에는 작성자와 검수자, 업데이트 기준을 명시합니다. 자세한 내용은 '
                '<a href="/policy/authors/">작성자·검수자 안내</a>에서 확인할 수 있습니다.</p>')
    if slug == "authors":
        return (f'<p>본 사이트의 지역 안내 콘텐츠는 <b>{esc(SITE["author"])}</b>가 작성하고 '
                f'<b>{esc(SITE["reviewer"])}</b>가 검수합니다. 모든 색인 페이지 하단에 작성·검수 정보와 업데이트 기준을 표시합니다.</p>'
                '<h3>작성 기준</h3><p>인천 행정구역, 생활권, 지하철역, 공항권, 도서권, 이용 장소별 예약 전 확인사항을 기준으로 작성합니다. '
                '실제 방문·이동 시 확인해야 하는 정보를 우선으로 다루며, 권역(신도시·원도심·공항·도서)별로 본문을 다르게 구성합니다.</p>'
                '<h3>검수 기준</h3><p>운영 책임자가 본문 정확성, 불법·선정적 표현 여부, 과장 문구, 내부링크와 메타 정보를 점검한 뒤 공개합니다.</p>'
                '<h3>업데이트 기준</h3><p>인천 행정체제 개편, 구군 명칭 변경, 생활권·지하철역 변화, 사용자 문의 패턴, 콘텐츠 품질 점검 결과를 반영해 수정하며, '
                '수정일은 각 페이지 하단에 표시합니다. 콘텐츠 작성 원칙은 <a href="/policy/content-standard/">콘텐츠 작성 기준</a>을 따릅니다.</p>')
    if slug == "contact":
        return (f'<p>예약과 지역 안내 문의는 전화로 도와드립니다.</p>'
                f'<p class="footer-phone" style="font-size:1.4rem"><a href="{SITE["phone_href"]}">📞 전화예약 {esc(SITE["phone"])}</a></p>'
                '<h3>웹사이트 제작·제휴 문의</h3>'
                f'<p>홈페이지 제작 문의와 제휴 제안은 텔레그램으로 받습니다.</p>'
                f'<p><a class="btn btn-orange" href="{SITE["telegram"]}" target="_blank" rel="noopener nofollow">웹사이트 제작문의</a> '
                f'<a class="btn btn-orange" href="{SITE["telegram"]}" target="_blank" rel="noopener nofollow">제휴문의</a></p>')
    return '<p>운영 기준 안내입니다.</p>'

def build_policy(p):
    name = p["name"]; path = f"/policy/{p['slug']}/"
    title = f"{name}｜{SITE['brand']} 인천 방문형 관리 안내"
    desc = clamp(f"{SITE['brand']} 인천 방문형 관리 {name} 안내. 운영 기준과 개인정보·서비스 원칙 정리", 80)
    # 순수 CTA 유틸리티 페이지(문의)는 noindex, 신뢰/정책 페이지는 색인 허용
    noindex = p["slug"] == "contact"
    body = ('<section class="section"><div class="container">'
      + breadcrumb_html([("인천 홈","/"),("운영 기준","/policy/service-standard/"),(name, path)]).replace('class="breadcrumb"','class="breadcrumb"') +
      f'<div class="prose"><h1>{esc(p["h1"])}</h1>' + policy_body(p["slug"]) +
      eeat_block() + '</div></div></section>')
    schema = [org_node(),
              {"@type":"WebPage","@id":SITE["url"]+path+"#webpage","url":SITE["url"]+path,"name":title,
               "description":desc,"inLanguage":"ko","isPartOf":{"@id":SITE["url"]+"/#org"},"dateModified":SITE["today"]},
              breadcrumb_ld([("인천 홈","/"),("운영 기준","/policy/service-standard/"),(name, path)])]
    write_page(path, document(path=path, title=title, description=desc, body=body,
                              schema_nodes=schema, noindex=noindex))

# ---- 공항·도서 허브 ----
def build_airport_island_hub():
    path = "/airport-island/"
    name = "공항·도서 안내"
    title = f"인천 공항·도서 안내｜영종·인천공항·강화·옹진 - {SITE['brand']}"
    desc = clamp("인천 공항권·도서권 방문 안내. 영종·인천공항·강화·옹진 이동 시간·추가 이동비 확인", 80)
    cards = [
        ("영종·운서","/life/yeongjong-unseo/","공항 배후 신도시·숙소권"),
        ("인천공항","/life/incheon-airport/","터미널·인접 숙소, 이동 시간 확인"),
        ("강화","/life/ganghwa/","외곽·도서형, 차량 이동·사전 예약"),
        ("옹진 도서","/life/ongjin-islands/","영흥·백령·대청·연평·자월 도서권"),
    ]
    card_html = "".join(f'<a class="card" href="{u}"><h3>{esc(n)}</h3><p>{esc(d)}</p>'
                        f'<span class="card-meta">자세히 보기 →</span></a>' for n,u,d in cards)
    hero = ('<section class="hero"><div class="container"><div class="hero-grid">'
      '<div class="hero-copy"><span class="eyebrow">공항권 · 도서권</span>'
      '<h1>인천 공항·도서 지역 방문 안내</h1>'
      '<p class="lead">영종·인천공항 공항권과 강화·옹진 도서권은 도심과 이동 기준이 다릅니다. '
      '이동 시간·숙소 위치·추가 이동비를 먼저 확인하세요.</p>'
      f'<div class="hero-cta"><a class="btn btn-gold" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a>'
      '<a class="btn btn-ghost" href="/check/travel-fee/">추가 이동비 기준</a></div></div>'
      + hero_figure_html() + '</div></div></section>')
    body = (hero + pricing_section() + breadcrumb_html([("인천 홈","/"),(name, path)]) +
      f'<section class="section"><div class="container"><div class="grid grid-4">{card_html}</div>'
      '<div class="prose" style="margin-top:2rem"><h2>공항·도서 권역 확인 기준</h2>'
      f'<p>{USECASE_BANK["airport"]}</p><p>{TYPE_DETAIL["airport"]}</p>'
      f'<p>{USECASE_BANK["island"]}</p><p>{TYPE_DETAIL["island"]}</p>'
      '<h2>공항권 이용 안내</h2>'
      '<p>영종·운서와 인천공항 인접 숙소권은 터미널·호텔·배후 주거지의 위치가 제각각이라, 예약 전에 숙소의 정확한 위치와 객실 호수, '
      '프런트 출입 절차를 확인합니다. 공항 이용객은 비행·체크인 일정에 따라 가능 시간대가 달라지므로 예약 가능 시간과 추가 이동비를 '
      '먼저 협의하는 것이 좋습니다. 자세한 기준은 <a href="/use/airport-area/">공항권 이용</a>과 '
      '<a href="/check/travel-fee/">추가 이동비 기준</a>에서 확인할 수 있습니다.</p>'
      '<h2>도서권 이용 안내</h2>'
      '<p>강화·옹진(영흥·백령·대청·연평·자월) 등 도서권은 방문 가능 여부와 이동 일정을 먼저 확인합니다. 교량·선편 이용 여부와 '
      '이동 시간, 숙소 위치에 따라 일정이 크게 달라지므로 충분한 시간을 두고 예약해 주세요. 관련 안내는 '
      '<a href="/use/island-area/">도서 지역 이용</a>, <a href="/life/ganghwa/">강화</a>, '
      '<a href="/life/ongjin-islands/">옹진 도서</a>에서 확인할 수 있습니다.</p>'
      '<h2>예약 전 체크리스트</h2>' + checklist_block(COMMON_CHECK) +
      customer_notice_html() +
      '<h2>관련 구군 · 예약 전 확인</h2>'
      '<ul><li>공항권 — <a href="/jung-gu/">중구</a>, <a href="/jung-gu/yeongjong-area/">영종</a>, '
      '<a href="/jung-gu/incheon-airport-area/">인천공항</a></li>'
      '<li>도서권 — <a href="/ganghwa-gun/">강화군</a>, <a href="/ongjin-gun/">옹진군</a></li>'
      '<li>확인 — <a href="/check/travel-fee/">추가 이동비 기준</a>, <a href="/check/time/">예약 가능 시간</a></li></ul>'
      f'<p class="muted">공항 이용 정보는 <a href="{AUTHORITY["airport"][1]}" target="_blank" rel="noopener nofollow">{AUTHORITY["airport"][0]} ↗</a>, '
      f'도서권은 <a href="{AUTHORITY["ganghwa"][1]}" target="_blank" rel="noopener nofollow">{AUTHORITY["ganghwa"][0]} ↗</a> · '
      f'<a href="{AUTHORITY["ongjin"][1]}" target="_blank" rel="noopener nofollow">{AUTHORITY["ongjin"][0]} ↗</a>를 참고할 수 있습니다.</p>'
      + policy_para() +
      whohowwhy_block(
        "이 페이지는 인천 공항·도서 권역 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.",
        "영종·인천공항 공항권과 강화·옹진 도서권의 이동·숙소·예약 기준을 정리했습니다.",
        "공항권·도서권에서 방문형 서비스를 찾는 사용자가 이동과 일정을 안전하게 확인하도록 돕기 위해 작성했습니다.")
      + eeat_block() + '</div></div></section>')
    schema = [org_node(),
              {"@type":"WebPage","@id":SITE["url"]+path+"#webpage","url":SITE["url"]+path,"name":title,
               "description":desc,"inLanguage":"ko","isPartOf":{"@id":SITE["url"]+"/#org"},"dateModified":SITE["today"],
               "primaryImageOfPage": image_ld(SITE["hero_img"], "인천 공항·도서 안내 이미지")},
              breadcrumb_ld([("인천 홈","/"),(name, path)]),
              image_ld(SITE["hero_img"], "인천 공항·도서 안내 이미지")]
    write_page(path, document(path=path, title=title, description=desc, body=body, schema_nodes=schema))

# ---- 2026 개편 대응(draft / noindex) ----
def build_reform(r):
    name = r["name"]; path = f"/{r['slug']}/"
    title = f"{name} 준비 안내(개편 예정 지역) - {SITE['brand']}"
    desc = clamp(f"인천 2026 행정개편 {name} 준비 안내. 현재 예약은 기존 구군 페이지로 연결됩니다", 80)
    body = ('<section class="section"><div class="container"><div class="prose">'
      + breadcrumb_html([("인천 홈","/"),(name+" 준비", path)]) +
      f'<h1>{esc(name)} 준비 안내 (개편 예정 지역)</h1>'
      '<div class="notice warn">이 페이지는 2026년 인천 행정체제 개편에 대비한 준비용 안내입니다. '
      '검색 노출 목적이 아니며(noindex), 현재 예약 안내는 기존 구군 페이지로 연결됩니다.</div>'
      f'<p>{esc(name)}은(는) {esc(" · ".join(r["base"]))} 일대를 기준으로 준비 중인 개편 대응 페이지입니다. '
      '개편 확정 전까지는 기존 행정구역 기준으로 안내하며, 개편 이후 canonical·redirect·사이트맵·내부링크를 새 체계에 맞게 조정합니다.</p>'
      '<h2>현재 예약 안내</h2><ul>'
      + "".join(
          f'<li><a href="/{g["slug"]}/">{esc(g["name"])} 안내</a></li>'
          for g in GUS if g["name"] in " ".join(r["base"]) or any(b.startswith(g["name"]) for b in r["base"]))
      + '</ul>' + eeat_block() + '</div></div></section>')
    schema = [org_node(),
              {"@type":"WebPage","@id":SITE["url"]+path+"#webpage","url":SITE["url"]+path,"name":title,
               "description":desc,"inLanguage":"ko","isPartOf":{"@id":SITE["url"]+"/#org"},"dateModified":SITE["today"]},
              breadcrumb_ld([("인천 홈","/"),(name, path)])]
    write_page(path, document(path=path, title=title, description=desc, body=body,
                              schema_nodes=schema, noindex=True))

# ----------------------------------------------------------------------------
# 루트 / sitemap / robots / 404
# ----------------------------------------------------------------------------
def collect_urls():
    urls = []  # (path, priority, noindex)
    urls.append(("/", "1.0", False))
    for g in GUS: urls.append((f"/{g['slug']}/", "0.8", False))
    for a in AREAS: urls.append((f"/{a['gu']}/{a['slug']}/", "0.7", False))
    for l in LIFE: urls.append((f"/life/{l['slug']}/", "0.7", False))
    for s in STATIONS: urls.append((f"/station/{s['slug']}/", "0.6", False))
    for u in USES: urls.append((f"/use/{u['slug']}/", "0.6", False))
    for c in CHECKS: urls.append((f"/check/{c['slug']}/", "0.6", False))
    for p in POLICIES: urls.append((f"/policy/{p['slug']}/", "0.4", False))
    urls.append(("/airport-island/", "0.7", False))
    for r in REFORM: urls.append((f"/{r['slug']}/", "0.1", True))  # noindex → 제외
    return urls

def build_sitemap():
    rows = []
    for path, pri, noindex in collect_urls():
        if noindex:  # noindex 페이지는 사이트맵에서 제외
            continue
        rows.append(
          f'  <url><loc>{SITE["url"]}{path}</loc>'
          f'<lastmod>{SITE["today"]}</lastmod>'
          f'<changefreq>weekly</changefreq><priority>{pri}</priority></url>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + '\n</urlset>\n')
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    return len(rows)

def build_robots():
    txt = ("User-agent: *\n"
           "Allow: /\n"
           "Disallow: /jemulpo-gu/\n"
           "Disallow: /yeongjong-gu/\n"
           "Disallow: /geomdan-gu/\n\n"
           f"Sitemap: {SITE['url']}/sitemap.xml\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)

def build_404():
    body = ('<section class="hero"><div class="container"><div class="prose" style="text-align:center;max-width:640px;margin-inline:auto">'
      '<h1>페이지를 찾을 수 없습니다</h1>'
      '<p class="lead">요청하신 페이지가 이동되었거나 존재하지 않습니다. 인천 방문형 관리 안내 홈에서 다시 찾아보세요.</p>'
      '<p><a class="btn btn-gold" href="/">인천 홈으로</a> '
      f'<a class="btn btn-ghost" href="{SITE["phone_href"]}">전화예약 {esc(SITE["phone"])}</a></p>'
      '</div></div></section>')
    schema = [org_node()]
    doc = document(path="/404.html", title="404 · 페이지를 찾을 수 없습니다 - "+SITE["brand"],
                   description="요청하신 페이지를 찾을 수 없습니다. 인천 방문형 관리 안내 홈으로 이동하세요.",
                   body=body, schema_nodes=schema, noindex=True)
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(doc)

def dump_data():
    """spec section 25: /data/*.json 산출"""
    d = os.path.join(ROOT, "data", "incheon")
    os.makedirs(d, exist_ok=True)
    mapping = {
        "gu-gun.json": GUS, "areas.json": AREAS, "life-areas.json": LIFE,
        "stations.json": STATIONS, "use-cases.json": USES, "checklists.json": CHECKS,
        "policies.json": POLICIES, "reform-2026.json": REFORM,
        "authors.json": {"author": SITE["author"], "reviewer": SITE["reviewer"]},
    }
    for fn, obj in mapping.items():
        with open(os.path.join(d, fn), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    # pages.json: 전체 인덱스
    pages = [{"path": p, "priority": pri, "noindex": ni} for p, pri, ni in collect_urls()]
    with open(os.path.join(d, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

# ----------------------------------------------------------------------------
def main():
    build_main()
    for g in GUS: build_gu(g)
    for a in AREAS: build_area(a)
    for l in LIFE: build_life(l)
    for s in STATIONS: build_station(s)
    for u in USES: build_use(u)
    for c in CHECKS: build_check(c)
    for p in POLICIES: build_policy(p)
    build_airport_island_hub()
    for r in REFORM: build_reform(r)
    n = build_sitemap()
    build_robots()
    build_404()
    dump_data()
    total = 1 + len(GUS) + len(AREAS) + len(LIFE) + len(STATIONS) + len(USES) + len(CHECKS) + len(POLICIES) + 1 + len(REFORM)
    print(f"생성 완료: 페이지 {total}개 / 사이트맵 {n}개 URL")

if __name__ == "__main__":
    main()
