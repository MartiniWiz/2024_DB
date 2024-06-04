import requests
import pandas as pd
import os

# Google Places API 키, 보안을 위해 대체
API_KEY = 'API_KEY'

def get_place_details(place_name):
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': place_name,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch place_id for {place_name}: {response.status_code}")
        return None
    results = response.json().get('candidates')
    if not results:
        print(f"No place_id found for {place_name}")
        return None
    place_id = results[0]['place_id']
    
    # Get detailed information
    detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
    detail_params = {
        'place_id': place_id,
        'fields': 'name,rating,user_ratings_total,formatted_address',
        'key': API_KEY
    }
    detail_response = requests.get(detail_url, params=detail_params)
    if detail_response.status_code != 200:
        print(f"Failed to fetch details for {place_name}: {detail_response.status_code}")
        return None
    details = detail_response.json().get('result')
    return details

# 기존 엑셀 파일 경로
input_file = os.path.join('..', 'data', 'tabelog_tokyo.xlsx') # 환경에 따라 경로 수정 필요
df = pd.read_excel(input_file, sheet_name='output')

# 결과를 저장할 리스트
results = []

# 각 가게 이름에 대해 Google Places API 호출
for idx, name in enumerate(df['name']):
    print(f"Processing {idx+1}/{len(df)}: {name}")
    details = get_place_details(name)
    if details:
        results.append({
            'name': details.get('name', ''),
            'address': details.get('formatted_address', ''),
            'rating': details.get('rating', ''),
            'user_ratings_total': details.get('user_ratings_total', '')
        })
        print(f"Found details for {name}")
    else:
        results.append({
            'name': name,
            'address': 'Not Found',
            'rating': 'Not Found',
            'user_ratings_total': 'Not Found'
        })
        print(f"No details found for {name}")

# 결과를 새로운 데이터프레임으로 변환
results_df = pd.DataFrame(results)

# 결과를 새로운 엑셀 파일에 저장
output_file = os.path.join('..', 'data', 'google_maps_results.xlsx') # 환경에 따라 경로 수정 필요
results_df.to_excel(output_file, index=False)
print(f"Results saved to {output_file}")
