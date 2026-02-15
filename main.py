import os
import requests
from playwright.sync_api import sync_playwright

# ------------------------------------------------------
# [설정] 텔레그램 정보 및 URL
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

def check_iris_final():
    print("🚀 [최종] IRIS 공고 크롤러 가동 (검색 버튼 클릭 모드)")

    with sync_playwright() as p:
        # 1. 브라우저 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            # 2. 사이트 접속
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(3000) # 3초 대기

            # 3. [핵심] '검색' 버튼 클릭
            print("🖱️ 데이터 로딩을 위해 '검색' 버튼을 클릭합니다...")
            try:
                search_btn = page.get_by_role("button", name="검색").first
                if search_btn.is_visible():
                    search_btn.click()
                else:
                    page.locator("a.btn_search").click()
            except:
                # 버튼을 못 찾아도 혹시 모르니 진행
                print("⚠️ 버튼 클릭 중 경미한 오류 발생 (무시하고 진행)")
            
            # 4. 데이터 로딩 대기 (넉넉하게 5초)
            print("⏳ 공고 목록 갱신 대기 중...")
            page.wait_for_timeout(5000)

            # 5. 공고 제목 추출 (알고리즘: 고정 공지 제외하고 첫 번째 글)
            links = page.query_selector_all("a")
            
            latest_title = None
            latest_link = URL # 링크는 상세페이지를 못 잡으므로 목록 페이지로 대체

            for link in links:
                text = link.inner_text().strip()
                
                # [필터링 규칙] 
                # 1. 길이가 너무 짧으면(10자 이하) 메뉴 버튼임 -> 제외
                # 2. 'NTIS', 'API', '매뉴얼', '고객센터'는 매일 떠있는 고정 공지임 -> 제외
                if len(text) > 10:
                    if "NTIS" in text or "API" in text or "매뉴얼" in text or "고객센터" in text:
                        continue # 고정 공지 건너뛰기
                    
                    # 여기까지 통과한 첫 번째 글이 '진짜 최신 공고'
                    latest_title = text
                    print(f"📌 추출된 최신 공고: {latest_title}")
                    break
            
            if not latest_title:
                print("❌ 유효한 공고 제목을 찾지 못했습니다.")
                return

            # 6. 저장된 파일과 비교
            try:
                with open(FILE_NAME, 'r', encoding='utf-8') as f:
                    last_title = f.read().strip()
            except FileNotFoundError:
                last_title = "NONE"

            if latest_title != last_title:
                print("🔔 새로운 공고 발견! 알림을 보냅니다.")
                msg = f"[IRIS 새 공고 알림]\n\n📄 제목:\n{latest_title}\n\n🔗 바로가기:\n{URL}"
                send_telegram(msg)
                
                # 파일 업데이트
                with open(FILE_NAME, 'w', encoding='utf-8') as f:
                    f.write(latest_title)
            else:
                print("✅ 새로운 공고가 없습니다.")

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
            send_telegram(f"❌ [크롤러 오류]\n{str(e)[:200]}")

        finally:
            browser.close()
            print("👋 종료")

if __name__ == "__main__":
    check_iris_final()
