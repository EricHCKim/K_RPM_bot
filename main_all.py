import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
FILE_NAME = "latest_all.txt"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={'chat_id': CHAT_ID, 'text': message})
    except: pass

def check_all():
    print("🚀 [전체 공고] 확인 중...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(3000)

            try:
                page.get_by_role("button", name="검색").first.click()
            except:
                page.locator("a.btn_search").click()
            
            page.wait_for_timeout(5000)

            links = page.query_selector_all("a")
            current_titles = []
            
            for link in links:
                text = link.inner_text().strip()
                if len(text) > 10 and not any(x in text for x in ["NTIS", "API", "매뉴얼", "고객센터"]):
                    current_titles.append(text)

            if not current_titles: return

            try:
                with open(FILE_NAME, 'r', encoding='utf-8') as f:
                    last_saved_title = f.read().strip()
            except FileNotFoundError:
                last_saved_title = "NONE"

            new_announcements = []
            for title in current_titles:
                if title == last_saved_title:
                    break
                new_announcements.append(title)

            if new_announcements:
                count = len(new_announcements)
                list_text = "\n".join([f"📄 {t}" for t in new_announcements])
                
                msg = f"📢 [IRIS 전체 새 공고 {count}건]\n\n{list_text}\n\n🔗 접속하기:\n{URL}"
                send_telegram(msg)
                
                with open(FILE_NAME, 'w', encoding='utf-8') as f:
                    f.write(new_announcements[0])
            else:
                print("✅ 전체 공고: 변동 없음")
                # ▼ 여기가 추가된 부분입니다!
                latest_one = current_titles[0] if current_titles else "없음"
                send_telegram(f"✅ [전체 공고] 현재 변동 사항 없습니다.\n(최신글: {latest_one})")

        except Exception as e:
            print(f"⚠️ 에러: {e}")
            send_telegram(f"⚠️ [전체 공고] 오류 발생: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_all()
