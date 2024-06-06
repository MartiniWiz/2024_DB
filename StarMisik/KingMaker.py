from django.contrib.auth import get_user_model

User = get_user_model()
admin_user = User.objects.get(username='Misik')  # 'admin'을 생성한 관리자 계정으로 변경

# 관리자 권한 설정
admin_user.is_staff = True
admin_user.is_admin = True
admin_user.is_superuser = True
admin_user.save()
