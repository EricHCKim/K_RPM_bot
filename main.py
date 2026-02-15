import os
from playwright.sync_api import sync_playwright

URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"

def debug_cctv():
    print("🎥 [CCTV 모드] 로봇이 보는 화면을 그대로 출력합니다...")

    with sync_playwright() as p:
        # 브라우저 띄우기 (사람인 척 위장)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print(f"🌐 접속 시도: {URL}")
            page.goto(URL, timeout=60000)
            
            # 로딩 기다리기 (그냥 무식하게 10초 대기)
            print("⏳ 화면이 뜰 때까지 10초간 대기합니다...")
            page.wait_for_timeout(10000)

            # 📸 [핵심] 현재 화면 정보 출력
            print("\n" + "="*30)
            print(f"📌 페이지 제목: {page.title()}")
            print("="*30)
            
            # 본문 텍스트 긁어오기 (상위 500자)
            visible_text = page.inner_text("body")
            print("📜 [화면에 보이는 글자들 (앞부분)]")
            print(visible_text[:500]) 
            print("="*30 + "\n")

            # 테이블이 진짜 없는지 확인
            table_count = page.locator("table").count()
            print(f"📊 발견된 테이블 개수: {table_count}개")
            
            if table_count == 0:
                print("❌ 테이블이 없습니다. 차단되었거나 로딩 중입니다.")
            else:
                print("✅ 테이블이 있습니다! (그런데 왜 아까는 못 찾았지?)")

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
        
        finally:
            browser.close()
            print("👋 진단 종료")

if __name__ == "__main__":
    debug_cctv()
