import os
from playwright.sync_api import sync_playwright

URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"

def debug_links():
    print("🕵️ [링크 탐정 모드] 페이지에 있는 모든 제목을 수집합니다...")

    with sync_playwright() as p:
        # 1. 브라우저 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            page.goto(URL, timeout=60000)
            
            # 2. 확실하게 로딩 기다리기 (5초)
            print("⏳ 데이터 로딩 대기 중...")
            page.wait_for_timeout(5000)

            # 3. [핵심] 페이지 내의 모든 링크(a 태그) 텍스트 수집
            # 너무 짧은 건(메뉴 등) 제외하고, 제목처럼 긴 것만 추려냅니다.
            links = page.query_selector_all("a")
            
            print(f"\n🔎 발견된 총 링크 개수: {len(links)}개")
            print("-" * 40)

            count = 0
            for link in links:
                text = link.inner_text().strip()
                # 글자 수가 10자 이상인 것만 출력 (공고 제목일 확률 높음)
                if len(text) > 10:
                    print(f"🔗 [후보] {text}")
                    count += 1
                    if count >= 10: break # 상위 10개만 확인
            
            print("-" * 40)
            
            if count == 0:
                print("❌ 긴 제목을 가진 링크가 하나도 없습니다. (구조가 아주 특이함)")
                # 혹시 모르니 화면 전체 텍스트를 더 길게 출력
                print("\n📜 [화면 전체 텍스트 (하단부 포함)]")
                print(page.inner_text("body")[:2000]) # 2000자까지 출력

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
        
        finally:
            browser.close()
            print("👋 탐색 종료")

if __name__ == "__main__":
    debug_links()
