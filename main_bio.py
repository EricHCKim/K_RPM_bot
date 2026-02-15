# main_bio.py (바이오/의료 전용)
import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
FILE_NAME = "latest_bio.txt"  # 저장 파일 이름 변경!

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
    except: pass

def check_bio():
    print("🚀 [바이오/의료] 맞춤 확인 시작")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(3000)

            # 필터 클릭
            try:
                page.locator("label").filter(has_text="생명과학").click()
                page.locator("label").filter(has_text="보건의료").click()
                print("✅ 필터 적용 완료")
            except: pass

            page.wait_for_timeout(1000)

            # 검색 클릭
            try:
                page.get_by_role("button", name="검색").first.click()
            except:
                page.locator("a.btn_search").click()
            
            page.wait_for_timeout(5000)

            links = page.query_selector_all("a")
            latest_title = None
            for link in links:
                text = link.inner_text().strip()
                if len(text) > 10 and not any(x in text for x in ["NTIS", "API", "매뉴얼", "고객센터"]):
                    latest_title = text
                    break
            
            if latest_title:
                try:
                    with open(FILE_NAME, 'r', encoding='utf-8') as f:
                        last_title = f.read().strip()
                except FileNotFoundError:
                    last_title = "NONE"

                if latest_title != last_title:
                    print(f"🔔 바이오 공고 업데이트: {latest_title}")
                    send_telegram(f"🔥🔥 [IRIS 핵심! 바이오/의료 공고] 🔥🔥\n{latest_title}\n\n{URL}")
                    with open(FILE_NAME, 'w', encoding='utf-8') as f:
                        f.write(latest_title)
                else:
                    print("✅ 바이오 공고: 변동 없음")

        except Exception as e:
            print(f"⚠️ 에러: {e}")
            # send_telegram(f"에러: {e}") # 필요하면 주석 해제
        finally:
            browser.close()

if __name__ == "__main__":
    check_bio()
