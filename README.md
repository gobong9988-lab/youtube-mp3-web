# 🎵 유튜브 최고음질 MP3 변환기 (YouTube to MP3 Web App)

스마트폰(아이폰, 갤럭시) 및 PC 브라우저에서 유튜브 링크를 입력하면 **최고음질(320kbps) MP3**로 변환하여 기기에 직접 다운로드할 수 있는 **Streamlit 웹 애플리케이션**입니다.

---

## ✨ 주요 기능
- **📱 모든 기기 완벽 지원**: PC (Windows/Mac/Linux), 모바일 (iOS Safari, Android Chrome/삼성인터넷) 브라우저에서 모두 다운로드 가능
- **🎧 최고음질 320kbps 지원**: 320kbps, 256kbps, 192kbps, 128kbps 선택 가능
- **🔊 브라우저 즉시 미리듣기**: 다운로드 전 오디오 플레이어로 바로 청취 가능
- **⚡ 간편한 웹 다운로드**: 별도 프로그램 설치 없이 웹 주소(URL)만으로 접속하여 사용
- **☁️ 무료 배포 지원**: GitHub + Streamlit Community Cloud를 통해 누구나 접속 가능한 무료 웹사이트 구축

---

## 📁 프로젝트 구조
```text
├── app.py             # Streamlit 메인 웹 애플리케이션 코드
├── requirements.txt   # 파이썬 필수 패키지 목록 (streamlit, yt-dlp)
├── packages.txt       # Streamlit Cloud 리눅스 시스템 패키지 (ffmpeg)
├── .gitignore         # Git 제외 파일 설정
└── README.md          # 프로젝트 안내 문서
```

---

## 💻 로컬(내 컴퓨터)에서 실행하기
1. **FFmpeg 설치 확인**: 컴퓨터에 FFmpeg가 설치되어 있어야 합니다.
2. **필수 라이브러리 설치**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Streamlit 웹 앱 실행**:
   ```bash
   streamlit run app.py
   ```
4. 브라우저에서 `http://localhost:8501`로 접속합니다.

---

## 🚀 Streamlit Cloud 배포 안내
1. 이 저장소(Repository)를 본인의 GitHub 계정에 업로드(Push)합니다.
2. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
3. **`Create app`** 클릭 후 생성한 저장소와 `app.py`를 선택하고 **`Deploy`**를 누르면 끝!
4. 생성된 고유 웹 주소(`https://xxxx.streamlit.app`)를 공유하면 누구나 사용할 수 있습니다.

---

## ⚠️ 유의 사항
- 본 프로그램은 개인 소장 및 연구/학습 목적에 한해 사용하시기 바라며, 저작권법을 준수해 주세요.
