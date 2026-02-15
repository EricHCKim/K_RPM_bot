import os
import requests
from playwright.sync_api import sync_playwright

# ------------------------------------------------------
# [설정] 텔레그램 정보
# ------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
FILE_NAME = "latest.txt"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
    except: pass

def check_iris_playwright():
    print("🚀 [최신형 로봇] Playwright 가동 시작...")

    with sync_playwright() as p:
        # 1. 브라우저 실행 (크롬보다 훨씬 가볍고 빠름)
        browser = p.chromium.launch(headless=True)
        
        # 2. 사람처럼 보이기 위한 설정 (User-Agent)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            # 3. 사이트 접속
            print(f"⏳ 사이트 접속 중: {URL}")
            page.goto(URL, timeout=60000) # 60초 대기

            # 4. 테이블이 뜰 때까지 기다림 (가장 확실한 방법)
            print("⏳ 데이터 로딩 대기 중...")
            page.wait_for_selector("table tbody tr", timeout=30000)

            # 5. 제목 추출
            # 첫 번째 줄(tr) 안의 제목(.tit 또는 a태그) 가져오기
            title_element = page.query_selector("table tbody tr .tit")
            if not title_element:
                title_element = page.query_selector("table tbody tr a")
            
            if title_element:
                current_title = title_element.inner_text().strip()
            else:
                # 제목을 못 찾으면 첫 줄 전체 텍스트라도 가져옴
                current_title = page.query_selector("table tbody tr").inner_text().strip()

            print(f"📌 추출된 제목: {current_title}")

            # 6. 저장 및 알림 로직
            try:
                with open(FILE_NAME, 'r', encoding='utf-8') as f:
                    last_title = f.read().strip()
            except FileNotFoundError:
                last_title = "NONE"

            if current_title != last_title:
                print("🔔 새 공고 발견!")
                msg = f"[IRIS 새 공고]\n{current_title}\n\n{URL}"
                send_telegram(msg)
                with open(FILE_NAME, 'w', encoding='utf-8') as f:
                    f.write(current_title)
            else:
                print("✅ 새 공고 없음.")
                # 성공 확인용 (첫 성공 후 주석 처리)
                # send_telegram(f"[생존신고] 이상 무. 최신: {current_title}")

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
            send_telegram(f"❌ [오류 발생]\n{str(e)[:200]}")

        finally:
            browser.close()
            print("👋 브라우저 종료")

if __name__ == "__main__":
    check_iris_playwright()
