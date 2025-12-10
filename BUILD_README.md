# EXE 빌드 가이드

## 준비 사항

### 1. PyInstaller 설치
```bash
pip install pyinstaller
```

### 2. 필요한 패키지 확인
```bash
pip install -r requirements.txt
```

## 빌드 방법

### 방법 1: spec 파일 사용 (권장)
```bash
pyinstaller build_exe.spec
```

### 방법 2: 명령줄 직접 사용
```bash
pyinstaller --name "OKX_Trading_Bot" ^
    --windowed ^
    --onedir ^
    --add-data "env/Lib/site-packages/PySide6/plugins;PySide6/plugins" ^
    app/main.py
```

## 빌드 후 구조

```
dist/
└── OKX_Trading_Bot/
    ├── OKX_Trading_Bot.exe  ← 실행 파일
    ├── _internal/           ← 내부 파일들
    └── data/                ← 자동 생성됨
        ├── trading_bot.db   ← 데이터베이스
        └── credentials.enc  ← 암호화된 자격증명
```

## 데이터 저장 위치

### 개발 환경
```
프로젝트폴더/
├── app/
├── data/              ← 여기에 저장
│   ├── trading_bot.db
│   └── credentials.enc
└── ...
```

### 실행 파일 (exe)
```
OKX_Trading_Bot.exe가 있는 폴더/
├── OKX_Trading_Bot.exe
├── _internal/
└── data/              ← 여기에 저장
    ├── trading_bot.db
    └── credentials.enc
```

## 배포 시 주의사항

### 1. 첫 실행
- `data` 폴더가 자동으로 생성됩니다
- `trading_bot.db` 파일이 자동으로 생성됩니다
- API 자격증명은 설정에서 입력해야 합니다

### 2. 업데이트
- **exe만 교체**: `data` 폴더는 그대로 유지 → 기존 데이터 보존
- **전체 삭제 후 설치**: 데이터 백업 필요

### 3. 데이터 백업
중요한 데이터:
- `data/trading_bot.db` - 모든 거래 기록, 설정
- `data/credentials.enc` - API 자격증명 (암호화됨)

백업 방법:
```bash
# data 폴더 전체 복사
xcopy data data_backup /E /I
```

### 4. 포터블 사용
exe와 함께 `data` 폴더를 USB에 넣으면 어디서든 사용 가능합니다:
```
USB:/
└── OKX_Trading_Bot/
    ├── OKX_Trading_Bot.exe
    ├── _internal/
    └── data/           ← 설정과 데이터가 함께 이동
```

## 빌드 최적화

### 단일 파일로 빌드 (느리지만 배포 간편)
```bash
pyinstaller --name "OKX_Trading_Bot" ^
    --windowed ^
    --onefile ^
    app/main.py
```
→ `OKX_Trading_Bot.exe` 하나만 생성됨
→ 실행 시 임시 폴더에 압축 해제 (느림)
→ `data` 폴더는 exe와 같은 위치에 생성

### 폴더로 빌드 (빠르고 권장)
```bash
pyinstaller build_exe.spec
```
→ `dist/OKX_Trading_Bot/` 폴더 생성
→ 실행 빠름
→ 폴더 전체를 배포

## 문제 해결

### "모듈을 찾을 수 없습니다" 에러
```bash
# spec 파일의 hiddenimports에 추가
hiddenimports=[
    'PySide6.QtCore',
    '누락된_모듈_이름',
]
```

### 실행 시 콘솔 창 보기 (디버깅용)
```python
# build_exe.spec 수정
console=True,  # False → True로 변경
```

### 데이터가 저장되지 않음
1. exe를 관리자 권한으로 실행
2. 또는 사용자 폴더로 이동:
   ```python
   # config/settings.py에서
   DATA_DIR = Path.home() / "AppData" / "Local" / "TradingBot" / "data"
   ```

## 아이콘 추가 (선택)

1. `.ico` 파일 준비
2. spec 파일 수정:
   ```python
   icon='icon.ico',
   ```

## 코드 서명 (선택)

Windows Defender 경고 방지:
1. 코드 서명 인증서 구입
2. `signtool`로 서명:
   ```bash
   signtool sign /f certificate.pfx /p password OKX_Trading_Bot.exe
   ```

