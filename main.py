import os
from playwright.sync_api import sync_playwright

URL = "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"

def debug_network_and_click():
    print("🕵️ [심화 진단] 검색 버튼 클릭 & 네트워크 감청 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 화면 크기를 넉넉하게 잡아야 버튼이 잘 눌립니다
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # 1. [핵심] 네트워크 통신 로그를 기록하는 리스너 설치
        # 데이터가 오가는지, 에러가 나는지 훔쳐봅니다.
        page.on("response", lambda response: check_response(response))

        try:
            print(f"🌐 사이트 접속 중: {URL}")
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(5000) # 5초 대기

            print("\n🖱️ '검색' 버튼을 찾아서 클릭을 시도합니다...")
            # '검색' 이라는 글자가 들어간 버튼이나 링크를 찾아서 클릭
            # (보통 조회 버튼을 누르면 리스트가 새로고침 됩니다)
            try:
                # 검색 버튼의 정확한 선택자를 모르니 텍스트로 찾습니다
                search_btn = page.get_by_role("button", name="검색").first
                if search_btn.is_visible():
                    search_btn.click()
                    print("✅ '검색' 버튼 클릭 성공! 데이터 로딩을 기다립니다...")
                else:
                    # 버튼이 없으면 '조회'나 돋보기 아이콘일 수 있음
                    print("⚠️ '검색' 버튼을 못 찾았습니다. 다른 버튼을 찾아봅니다.")
                    page.locator("a.btn_search").click() # 흔한 클래스명 시도
                    print("✅ 대체 버튼(a.btn_search) 클릭 시도함.")
            except Exception as e:
                print(f"⚠️ 버튼 클릭 중 에러(무시 가능): {e}")

            # 데이터가 뜰 때까지 5초 더 대기
            page.wait_for_timeout(5000)

            # 2. 다시 링크 수집 (이번엔 리스트가 떴는지 확인)
            print("\n🔎 [재확인] 화면에 새로 뜬 공고 제목이 있는지 봅니다...")
            links = page.query_selector_all("a")
            
            notice_found = False
            for link in links:
                text = link.inner_text().strip()
                # 공고 제목 같은 긴 텍스트만 출력
                if len(text) > 15 and "시스템" not in text and "매뉴얼" not in text:
                    print(f"✨ [발견된 공고?] {text}")
                    notice_found = True
            
            if not notice_found:
                print("❌ 여전히 공고 제목이 안 보입니다.")
                # 최후의 수단: 페이지 전체 텍스트 덤프 (중간 부분)
                print("\n📜 화면 중간 내용 텍스트:")
                body_text = page.inner_text("body")
                # 필터 영역 다음 부분을 보기 위해 자름
                start_idx = body_text.find("검색")
                print(body_text[start_idx:start_idx+500])

        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")
        
        finally:
            browser.close()
            print("👋 진단 종료")

def check_response(response):
    # 뒤에서 몰래 일어나는 데이터 통신 중 '수상한 실패'가 있는지 감시
    status = response.status
    url = response.url
    
    # 200(성공)이 아닌 것들, 특히 데이터 관련(.do, .json) 에러만 출력
    if status != 200 and status != 204 and status != 302:
        print(f"🚨 [통신 에러] {status} | {url[-40:]}") # URL 뒷부분만 출력
    
    # 만약 리스트 데이터 통신이 성공했다면?
    if "retrieve" in url and "List" in url and status == 200:
        # print(f"📡 [데이터 수신됨] {url[-30:]}") # 너무 많이 뜨면 주석 처리
        pass

if __name__ == "__main__":
    debug_network_and_click()
