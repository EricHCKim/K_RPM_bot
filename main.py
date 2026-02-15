import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# ------------------------------------------------------
# [설정] 텔레그램 정보 (GitHub Secret에서 가져옴)
# ------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
FILE_NAME = "latest.txt"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("텔레그램 설정이 없습니다.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, json=payload)

def check_iris_with_browser():
    print("🚀 [고성능 로봇] 브라우저를 실행합니다...")

    # 1. 브라우저 설정 (화면 없이 실행하는 '헤드리스' 모드)
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 화면 없이 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 2. 사이트 접속
        driver.get(URL)
        print("⏳ 사이트 로딩 대기 중...")

        # 3. 데이터가 뜰 때까지 최대 20초 기다림 (테이블이 나타날 때까지)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # 4. 첫 번째 공고 찾기
        # IRIS 사이트 구조상 첫 번째 행(tr)의 제목을 가져옵니다.
        # (JavaScript가 실행된 후의 진짜 HTML을 봅니다)
        latest_row = driver.find_element(By.CSS_SELECTOR, "table tbody tr")
        
        # 제목이 들어있는 요소 찾기 (상황에 따라 class가 다를 수 있어 여러 시도)
        try:
            title_element = latest_row.find_element(By.CLASS_NAME, "tit") # 일반적인 경우
        except:
            title_element = latest_row.find_element(By.TAG_NAME, "a") # 링크 태그인 경우

        current_title = title_element.text.strip()
        print(f"📌 현재 최신 공고: {current_title}")

        # 5. 저장된 기록과 비교
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                last_title = f.read().strip()
        except FileNotFoundError:
            last_title = "처음 실행"

        if current_title != last_title:
            print("🔔 새로운 공고 발견! 알림을 보냅니다.")
            msg = f"[IRIS 새 공고 알림]\n\n📄 제목: {current_title}\n🔗 링크: {URL}"
            send_telegram(msg)
            
            # 파일 업데이트
            with open(FILE_NAME, 'w', encoding='utf-8') as f:
                f.write(current_title)
        else:
            print("✅ 새로운 공고가 없습니다.")
            # 테스트용: 매번 알림 받고 싶으면 아래 주석 해제
            # send_telegram(f"[생존신고] 이상 무. 최신글: {current_title}")

    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        # 에러 내용을 나에게 보내고 싶으면 주석 해제
        # send_telegram(f"[오류 발생] {e}")

    finally:
        driver.quit() # 브라우저 종료

if __name__ == "__main__":
    check_iris_with_browser()
