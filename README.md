# Factory Test Room Panel Reservation

여러 사용자가 한 서버의 예약 내역을 공유하는 FastAPI + PostgreSQL 웹 애플리케이션입니다.

## 주요 기능
- 현재/기간별 예약 목록 조회
- 예약 행 클릭 시 Layout에서 해당 Panel 강조
- Layout의 Panel 클릭 시 예약 정보 조회 및 신규 예약 입력
- PostgreSQL exclusion constraint로 동시 요청에서도 기간 중복 예약 차단
- 프로젝트명, 발주번호, 담당자, 시작일, 종료일, 비고 관리
- 관리자 키를 이용한 예약 삭제
- 15초 자동 새로고침

## 실행
1. Docker Desktop 또는 Docker Engine + Compose를 설치합니다.
2. `.env.example`을 `.env`로 복사하고 비밀번호와 `ADMIN_KEY`를 변경합니다.
3. 프로젝트 폴더에서 실행합니다.

```bash
cp .env.example .env
docker compose up -d --build
```

4. 서버 PC에서 `http://localhost:8000`, 다른 PC에서 `http://서버IP:8000`으로 접속합니다.
5. Windows 방화벽을 사용하는 경우 TCP 8000 인바운드 허용 규칙이 필요합니다.

## 운영 권장
- 사내망에서도 Nginx 또는 Caddy를 앞단에 두고 HTTPS를 적용하십시오.
- 외부 인터넷에 직접 8000 포트를 공개하지 마십시오.
- PostgreSQL 데이터는 `postgres_data` Docker volume에 보존됩니다.
- 정기 백업 예시: `docker compose exec -T db pg_dump -U factory_app factory_booking > backup.sql`

## 실제 Layout 적용
`app/static/layout.png`를 실제 Layout PNG로 교체합니다. Panel 위치는 최초 실행 시 생성되는 `panels` 테이블의 `x`, `y`, `width`, `height` 값(%)으로 관리됩니다. 기본 화면에는 12개 샘플 Panel이 있습니다.

좌표 수정 예시:
```sql
UPDATE panels SET x=12.5, y=18, width=8, height=12 WHERE code='P01';
```

현재 좌표 단위는 이미지 컨테이너 대비 백분율입니다. 실제 Layout을 받으면 각 Panel 좌표를 맞추면 됩니다.
