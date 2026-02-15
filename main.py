import requests
from bs4 import BeautifulSoup
import os

# ------------------------------------------------------
# [설정] GitHub Secret에서 텔레그램 정보를 가져옵니다
# ------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# IRIS 공고 게시판 URL
URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
FILE_NAME = "latest.txt"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("텔레그램 설정이 없습니다.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(url, json=payload)

def check_iris():
    print("🔍 IRIS 공고 확인 시작...")
    
    # 1. 이전에 저장된 최신글 제목 읽기
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            last_title = f.read().strip()
    except FileNotFoundError:
        last_title = "처음 실행"

    # 2. 웹사이트 접속 (정부 사이트 접속을 위해 SSL 무시, User-Agent 설정)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # verify=False: 공공기관 사이트 인증서 에러 방지
        response = requests.get(URL, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. 게시물 리스트에서 첫 번째 글 제목 추출
        # IRIS는 보통 table 구조이며, 제목은 td 태그 안에 있습니다.
        # 최신글 1개만 가져옵니다.
        latest_row = soup.select_one('table tbody tr')
        
        if not latest_row:
            print("❌ 게시물을 찾을 수 없습니다. HTML 구조가 변경되었을 수 있습니다.")
            return

        # 제목이 있는 td 찾기 (보통 두 번째나 세 번째 td, class가 'tit'인 경우 많음)
        title_element = latest_row.select_one('.tit') 
        if not title_element:
            # 클래스가 없으면 a 태그를 찾거나 두번째 td를 선택
             title_element = latest_row.select_one('a')

        if title_element:
            current_title = title_element.get_text(strip=True)
            print(f"📌 현재 웹사이트 최신글: {current_title}")
            print(f"💾 내 컴퓨터 저장 기록: {last_title}")

            # 4. 비교 및 알림 전송
            if current_title != last_title:
                print("🔔 새로운 공고 발견! 알림을 보냅니다.")
                
                msg = f"[IRIS 새 공고 알림]\n\n📄 제목: {current_title}\n\n🔗 링크: {URL}"
                send_telegram(msg)

                # 5. 최신글 제목을 파일에 업데이트
                with open(FILE_NAME, 'w', encoding='utf-8') as f:
                    f.write(current_title)
            else:
                print("✅ 새로운 공고가 없습니다.")
        else:
            print("❌ 제목 요소를 찾을 수 없습니다.")

    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")
        # 에러 발생 시 나에게 알림을 받고 싶다면 아래 주석 해제
        # send_telegram(f"[오류 발생] IRIS 크롤링 실패: {e}")

if __name__ == "__main__":
    # SSL 경고 메시지 숨기기
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    check_iris()