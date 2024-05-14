import traceback
import sys
import requests
from bs4 import BeautifulSoup4 

def Err(TryFunction):
    """
    traceback 기능 전용 함수
    """
    try:
        TryFunction()
    except:
        print(traceback.format_exc(), file=sys.stderr)

#HTML String으로 받기
def get_html(url):
    """
    FState = 성공 확인
    Body = HTML Body String
    """
    FState = False
    Body = ''

    def request():
        res = requests.get(url=url)
        nonlocal Body
        nonlocal FState

        FState = res.ok
        Body = res.text

    Err(request)

    return Body, FState

class TabeURL(URL):

    def __init__(self, city, area, page):
        """
        city = 도시 (도쿄, 오사카 etc.)
        area = 지역 분류 코드 (도쿄 기준: 1301, 1302 etc.)
        page = 현 타베로그 페이지  
        """

        self.city = city
        self.area = area
        self.page = page
    
    # 일정 url 구조를 자동으로 생성
    def url(self):
        return "https://tabelog.com/{:s}/{:s}/rstLst/{:d}/".format(self.city, self.area, self.page)
