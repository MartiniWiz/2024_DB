import pandas as pd
from my_app.models import Region, Tabelog, Google, FinalScore, User, Favorites
from django.db import transaction

# 스프레드시트 파일 경로
tabelog_file = '/workspaces/2024_DB/StarMisik/data/tabelog_tokyo.xlsx'
google_file = '/workspaces/2024_DB/StarMisik/data/google_maps_results.xlsx'

# 데이터 읽기
tabelog_data = pd.read_excel(tabelog_file)
google_data = pd.read_excel(google_file)

# 데이터프레임을 딕셔너리로 변환
tabelog_dict = tabelog_data.to_dict('records')
google_dict = google_data.to_dict('records')

@transaction.atomic
def populate_db():
    # Region 및 Tabelog 데이터 삽입
    for record in tabelog_dict:
        station_detail = record['detail'].split('/')
        station = station_detail[0].strip()
        menu = station_detail[1].strip() if len(station_detail) > 1 else ''
        region, created = Region.objects.get_or_create(station=station)
        tabelog = Tabelog.objects.create(
            address=record['address'],
            name=record['name'],
            station=region,
            menu=menu,
            score=record['rating'],
            num_reviews=record['reviews']
        )
    
    # Google 데이터 삽입
    for record in google_dict:
        google = Google.objects.create(
            address=record['address'],
            name=record['name'],
            google_score=record.get('score', 0),
            num_reviews_google=record.get('user_rating_total', 0)
        )

    # FinalScore 계산 및 삽입
    for tabelog in Tabelog.objects.all():
        try:
            google = Google.objects.get(address=tabelog.address)
            tabelog_score = tabelog.score if tabelog.score > 0 else 0
            google_score = google.google_score if google.google_score > 0 else 0
            
            # 가중치 계산
            tabelog_weight = 1.5 if tabelog_score >= 3.5 else 1.0
            google_weight = 1.5 if google_score >= 4.2 else 1.0

            # 리뷰 수에 따른 가중치
            tabelog_reviews_weight = 1 + (tabelog.num_reviews / 1000)
            google_reviews_weight = 1 + (google.num_reviews_google / 1000)

            # 최종 점수 계산
            weighted_tabelog_score = tabelog_score * tabelog_weight * tabelog_reviews_weight
            weighted_google_score = google_score * google_weight * google_reviews_weight

            combined_score = (weighted_tabelog_score + weighted_google_score) / 2
            final_score = min(combined_score, 5.0)  # 최대 5점으로 제한

            FinalScore.objects.create(
                address=tabelog,
                new_score=final_score
            )
        except Google.DoesNotExist:
            # 구글 데이터가 없는 경우
            FinalScore.objects.create(
                address=tabelog,
                new_score=tabelog.score
            )

if __name__ == '__main__':
    populate_db()
