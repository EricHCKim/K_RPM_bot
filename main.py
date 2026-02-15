import requests
from bs4 import BeautifulSoup

# 사용자님이 알려주신 IRIS 공고 게시판 URL
URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"

def debug_iris():
    print("🔍 [진단 시작] IRIS 사이트 접속을 시도합니다...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    try:
        # 1. 사이트 접속 (SSL 무시 포함)
        response = requests.get(URL, headers=headers, verify=False, timeout=15)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        
        print(f"📡 응답 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ 사이트 접속에 실패했습니다. (차단되었거나 주소가 잘못됨)")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. 'table' 태그가 있는지 확인
        tables = soup.find_all('table')
        print(f"📊 발견된 테이블 개수: {len(tables)}개")

        # 3. HTML 내용 일부 출력 (로그 확인용)
        print("\n-------- [HTML 내용 앞부분 500자] --------")
        print(soup.prettify()[:500])
        print("------------------------------------------\n")

        if len(tables) > 0:
            print("✅ 테이블을 찾았습니다! 첫 번째 테이블의 첫 줄을 분석합니다.")
            first_row = tables[0].select_one('tbody tr')
            if first_row:
                print(f"📝 첫 번째 줄 내용: {first_row.get_text(strip=True)[:50]}...")
            else:
                print("⚠️ 테이블은 있는데 내용(tbody tr)이 비어있습니다.")
        else:
            print("❌ 테이블 태그가 아예 없습니다. div나 ul 리스트 구조일 수 있습니다.")
            # 혹시 리스트가 div로 되어있는지 확인
            divs = soup.select('div.list_item') # 흔한 클래스 이름 추측
            print(f"🔎 div.list_item 개수: {len(divs)}개")

    except Exception as e:
        print(f"⚠️ 에러 발생: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    debug_iris()
