import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def check_iris_final():
    print("🚀 [최종 로봇] 안전 모드로 브라우저 가동 시작...")

    # 1. 크롬 옵션 설정 (충돌 방지용 옵션 대거 추가)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new') # 최신 헤드리스 모드
    chrome_options.add_argument('--no-sandbox') # 리눅스 환경 필수
    chrome_options.add_argument('--disable-dev-shm-usage') # 메모리 부족 방지
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # 봇 탐지 회피 (User-Agent 설정)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

    driver = None
    try:
        # 2. 드라이버 자동 설치 및 실행
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ 브라우저 실행 성공! 사이트 접속 중...")
        driver.get(URL)

        # 3. 데이터 로딩 대기 (최대 30초)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        # 4. 제목 추출
        # IRIS 사이트 구조: table > tbody > tr > (class='tit' 또는 a태그)
        latest_row = driver.find_element(By.CSS_SELECTOR, "table tbody tr")
        
        try:
            title_el = latest_row.find_element(By.CLASS_NAME, "tit")
        except:
            title_el = latest_row.find_element(By.TAG_NAME, "a")
            
        current_title = title_el.text.strip()
        print(f"📌 현재 최신 공고: {current_title}")

        # 5. 저장 및 알림 로직
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                last_title = f.read().strip()
        except FileNotFoundError:
            last_title = "NONE"

        if current_title != last_title:
            print("🔔 새 공고 발견! 알림 전송.")
            msg = f"[IRIS 새 공고]\n{current_title}\n\n{URL}"
            send_telegram(msg)
            with open(FILE_NAME, 'w', encoding='utf-8') as f:
                f.write(current_title)
        else:
            print("✅ 새 공고 없음.")
            # 성공 확인용 (첫 성공 후에는 주석 처리 추천)
            send_telegram(f"[성공] 크롤링 완료. 최신글: {current_title}")

    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        error_msg = f"❌ [오류 발생]\n{str(e)[:200]}" # 내용이 길면 잘라서 보냄
        send_telegram(error_msg)

    finally:
        if driver:
            driver.quit()
            print("👋 브라우저 종료")

if __name__ == "__main__":
    check_iris_final()
