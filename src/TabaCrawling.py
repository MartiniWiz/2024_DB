import traceback
import sys
import requests
from bs4 import BeautifulSoup
import abc
import pandas as pd
import os
import re
import time

def Err(TryFunction):
    """
    traceback 기능 전용 함수
    """
    try:
        TryFunction()
    except:
        print(traceback.format_exc(), file=sys.stderr)

class ExcelConvertible(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def column_names(self):
        pass

def to_excel(convertible, filename):
    """
    엑셀로 변환할 수 있는 객체들을 엑셀 파일로 저장합니다. 저장 경로는 {working directory}/tmp/{filename}입니다.
    :param convertible: ExcelConvertible을 구현한 클래스의 객체 또는 그 리스트
    :type convertible: Union[ExcelConvertible, Iterable[ExcelConvertible]]
    :param filename: 저장할 파일의 이름.
    :type filename: str
    """
    df_dict = {}
    try:
        for x in iter(convertible):
            for col in x.column_names():
                if col in df_dict:
                    df_dict[col].append(x.__dict__[col])
                else:
                    df_dict[col] = [x.__dict__[col]]
    except TypeError:
        df_dict = {col: [convertible.__dict__[col]] for col in convertible.column_names()}

    writer = pd.ExcelWriter(os.path.join('tmp', filename))
    df = pd.DataFrame(data=df_dict)
    df.to_excel(writer, sheet_name='output')
    writer.save()

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

class TabeURL():

    def __init__(self, city, area, page):
        """
        city = 도시 (도쿄, 오사카 etc.)
        area = 지역 분류 코드 (도쿄 기준: 1301, 1302, ... 1331)
        page = 현 타베로그 페이지  
        """

        self.city = city
        self.area = area
        self.page = page
    
    # 일정 url 구조를 자동으로 생성
    def url(self):
        return "https://tabelog.com/kr/{:s}/{:s}/rstLst/{:d}/".format(self.city, self.area, self.page)
    
class TabelogInfo(ExcelConvertible):
    
    def __init__(self, name, rating, reviews, detail):

        """
        name = 가게 이름 (str)
        rating = 별점 (float)
        reviews = 평가 개수 (int)
        detail = 가게 정보 (str)
        """

        self.name = name
        self.rating = rating
        self.reviews = reviews
        self.detail = detail

    def column_names(self):
        return ['name', 'rating', 'reviews', 'detail']
    
def collect_info(area, page):

    url_tokyo = TabeURL(city='tokyo', area=area, page=page)

    body, ok = get_html(url=url_tokyo.url())
    if not ok:
        return False, []
    
    # start parsing
    soup = BeautifulSoup(body, features="lxml")
    shops = soup.select('#container > div.rstlist-contents.clearfix > div.flexible-rstlst > div > div.js-rstlist-info.rstlist-info')

    info_list = []
    for shop in shops:
        name_soup = shop.select('div.list-rst__contents > div > div.list-rst__rst-name-wrap > h3 > a')
        if not name_soup:
            continue

        rate_soup = shop.select('div.list-rst__contents > div > div.list-rst__rate')[0]

        rating_soup = rate_soup.find_all('p', class_=re.compile("^c-rating"))
        review_soup = rate_soup.select('p.list-rst__rvw-count > a')
        detail_soup = shop.select('div.list-rst__contents > div > div.list-rst__rst-name-wrap > div')

        name = name_soup[0].text
        rating = rating_soup[0].text if rating_soup else '-1'
        review = review_soup[0].text if review_soup else '0件'
        detail = detail_soup[0].text

        def reformat_str(s):
            return str(s).lstrip().rstrip()

        name = reformat_str(name)
        try:
            rating = float(reformat_str(rating))
        except:
            rating = -1

        try:
            review = int(reformat_str(review).rstrip("件"))
        except:
            review = 0

        detail = reformat_str(detail)

        info = TabelogInfo(name=name, rating=rating, reviews=review, detail=detail)
        info_list.append(info)

    return True, info_list

restaurants = []
Areas = ['A1301', 'A1302', 'A1303', 'A1304', 'A1305', 'A1306', 'A1307', 'A1308', 'A1309', 'A1310'
         'A1311', 'A1312', 'A1313', 'A1314', 'A1315', 'A1316', 'A1317', 'A1318', 'A1319', 'A1320'
         'A1321', 'A1322', 'A1323', 'A1324', 'A1325', 'A1326', 'A1327', 'A1328', 'A1329', 'A1330'
         'A1331']

for area in range(1301, ):
    for page in range(1, 30):
        _, infos = collect_info(area, page)
        restaurants += infos
        time.sleep(0.5)