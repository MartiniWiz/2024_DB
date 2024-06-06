#!/bin/bash

# 데이터베이스 파일 삭제
rm -f db.sqlite3

# 마이그레이션 폴더 삭제
rm -rf my_app/migrations/

# 마이그레이션 생성 및 적용
python manage.py makemigrations my_app
python manage.py migrate
