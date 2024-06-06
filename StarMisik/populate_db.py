import os
import django
import pandas as pd
from django.db import transaction
from my_app.models import Region, Tabelog, Google, FinalScore

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StarMisik.settings')
django.setup()

# 스프레드시트 파일 경로
tabelog_file = '/workspaces/2024_DB/StarMisik/data/tabelog_tokyo.xlsx'
google_file = '/workspaces/2024_DB/StarMisik/data/google_maps_results.xlsx'

# 데이터 읽기
print("Reading Excel files...")
tabelog_data = pd.read_excel(tabelog_file, engine='openpyxl')
google_data = pd.read_excel(google_file, engine='openpyxl')

# 데이터 확인
print("Tabelog Data:")
print(tabelog_data.head())
print("Google Data:")
print(google_data.head())

# 'Not Found' 또는 NaN 값을 0으로 대체
google_data['rating'] = google_data['rating'].replace('Not Found', 0).fillna(0)
google_data['user_ratings_total'] = google_data['user_ratings_total'].replace('Not Found', 0).fillna(0)

# 데이터프레임을 딕셔너리로 변환
tabelog_dict = tabelog_data.to_dict('records')
google_dict = google_data.to_dict('records')

# 데이터베이스 채우기
@transaction.atomic
def populate_db():
    print("Starting database population...")
    
    # Region 및 Tabelog 데이터 삽입
    for record in tabelog_dict:
        station_detail = record['detail'].split('/')
        station = station_detail[0].strip()
        menu = station_detail[1].strip() if len(station_detail) > 1 else ''
        region, created = Region.objects.get_or_create(station=station)

        google_record = next((item for item in google_dict if item['name'] == record['name']), None)
        if google_record:
            address = google_record['address']
            google_instance, created = Google.objects.get_or_create(
                address=google_record['address'],
                defaults={
                    'name': google_record['name'],
                    'google_score': google_record['rating'],
                    'num_reviews_google': google_record['user_ratings_total']
                }
            )
        else:
            address = 'Not Found'
            google_instance = None

        tabelog = Tabelog.objects.create(
            address=address,
            name=record['name'],
            station=region,
            menu=menu,
            score=record['rating'],
            num_reviews=record['reviews'],
            google=google_instance
        )
        print(f"Inserted Tabelog record: {tabelog}")

    # Google 데이터 삽입
    for record in google_dict:
        # 중복된 주소를 가진 레코드 처리
        Google.objects.update_or_create(
            address=record['address'],
            defaults={
                'name': record['name'],
                'google_score': record['rating'],
                'num_reviews_google': record['user_ratings_total']
            }
        )
        print(f"Inserted/Updated Google record: {record['name']} - {record['address']}")

    # FinalScore 계산 및 삽입
    for tabelog in Tabelog.objects.all():
        google = Google.objects.filter(address=tabelog.address).first()
        if google:
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
                tabelog=tabelog,
                new_score=final_score
            )
            print(f"Inserted FinalScore record for address: {tabelog.address}, score: {final_score}")

        else:
            # 구글 데이터가 없는 경우
            FinalScore.objects.create(
                tabelog=tabelog,
                new_score=tabelog.score
            )
            print(f"Inserted FinalScore record for address: {tabelog.address}, score: {tabelog.score}")

populate_db()
