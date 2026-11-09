# Factory Test Room Panel Reservation Prototype

Panel 10개의 기간 예약을 여러 사용자가 공유하는 Flask 클라우드 프로토타입입니다.

## 포함 기능
- P1~P10 판넬 예약
- 예약자, 프로젝트명, 시작일, 종료일, 비고
- 기간 중복 예약 차단
- 조회일 기준 판넬 상태 표시
- 예약 내역 조회와 취소
- PostgreSQL 사용 시 판넬별 advisory lock으로 동시 등록 충돌 완화

## 로컬 테스트 (Windows)
1. Python 3.11 이상 설치
2. 이 폴더에서 명령 프롬프트 실행
3. 아래 명령 실행

    py -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

4. 브라우저에서 http://localhost:5000 접속

로컬 테스트는 SQLite를 자동 사용합니다.

## Render 배포
1. 이 폴더의 파일을 GitHub 저장소에 업로드합니다.
2. Render Dashboard에서 **New > Blueprint**를 선택합니다.
3. GitHub 저장소를 연결합니다.
4. `render.yaml`을 인식하면 Web Service와 PostgreSQL DB가 생성됩니다.
5. 배포 완료 후 Render가 제공하는 `https://...onrender.com` 주소로 접속합니다.

## 중요
- 프로토타입이라 로그인/권한 기능이 없습니다. 링크를 아는 사용자는 예약 취소가 가능합니다.
- 실제 회사 프로젝트명, 시험 일정, 개인정보를 입력하기 전에 회사 IT/정보보안 승인을 받으세요.
- 운영 전 Microsoft Entra ID 로그인, 관리자 권한, 감사 로그, 백업을 추가하는 것을 권장합니다.
