# -*- coding: utf-8 -*-
"""
유튜브 최고음질 MP3 변환기 (Streamlit Web Application)
- PC, 안드로이드, 아이폰/아이패드 모든 환경 지원
- 320kbps 초고음질 MP3 변환 및 브라우저 직접 다운로드
- 다크 모드 / 라이트 모드 완벽 호환
- 유튜브 403 Forbidden 방지 및 자동 대체 추출 로직 적용
"""

import os
import re
import shutil
import tempfile
import streamlit as st
import yt_dlp

# 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 최고음질 MP3 변환기",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 모바일 및 다크/라이트 테마 친화적 커스텀 CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        text-align: center;
        color: #ff4b4b;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        text-align: center;
        opacity: 0.8;
        margin-bottom: 1.8rem;
    }
    .stDownloadButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        width: 100% !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1b5e20 !important;
        transform: translateY(-2px);
    }
    .footer-note {
        text-align: center;
        opacity: 0.6;
        font-size: 0.85rem;
        margin-top: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)


def sanitize_filename(filename: str) -> str:
    """파일명에서 특수문자를 제거하여 안전한 파일명을 만듭니다."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    cleaned = cleaned.strip()
    return cleaned if cleaned else "youtube_audio"


def format_duration(seconds: int) -> str:
    """초 단위를 분:초 형식으로 변환합니다."""
    if not seconds:
        return "시간 정보 없음"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}시간 {m}분 {s}초"
    return f"{m}분 {s}초"


def process_youtube_to_mp3(url: str, quality_bitrate: str):
    """
    유튜브 URL에서 오디오를 추출하여 MP3 파일 바이트와 메타데이터를 반환합니다.
    유튜브의 403 Forbidden 차단을 방지하기 위해 다단계 추출 전략을 사용합니다.
    """
    # 1. 시도할 다운로드 전략 목록 (403 오류 시 자동 순차 시도)
    download_configs = [
        # 전략 1: 기본 최고음질 오디오 추출 (가장 안정적, 포맷 251 Opus/140 m4a)
        {
            'name': '기본 고음질 스트림',
            'extractor_args': {},
        },
        # 전략 2: web_embedded 및 tv 클라이언트 우회
        {
            'name': '웹 임베디드 우회 스트림',
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_embedded', 'tv']
                }
            },
        },
        # 전략 3: mweb 모바일 웹 클라이언트
        {
            'name': '모바일 웹 우회 스트림',
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb']
                }
            },
        }
    ]

    last_error = None

    for config in download_configs:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'windowsfilenames': True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_bitrate,
                }],
                'quiet': True,
                'no_warnings': True,
            }

            # 전략별 extractor_args 추가
            if config.get('extractor_args'):
                ydl_opts['extractor_args'] = config['extractor_args']

            # Node.js 런타임이 설치되어 있다면 서명 암호 해독 활성화
            if shutil.which('node'):
                ydl_opts['js_runtimes'] = {'node': {}}

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', '유튜브 음원')
                    uploader = info.get('uploader', '알 수 없음')
                    duration = info.get('duration', 0)
                    thumbnail = info.get('thumbnail', None)

                # 생성된 .mp3 파일 찾기
                mp3_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.mp3')]
                if not mp3_files:
                    raise FileNotFoundError("MP3 변환 파일을 찾을 수 없습니다.")

                mp3_path = os.path.join(temp_dir, mp3_files[0])
                with open(mp3_path, 'rb') as f:
                    mp3_bytes = f.read()

                file_size_mb = len(mp3_bytes) / (1024 * 1024)

                return {
                    'title': title,
                    'uploader': uploader,
                    'duration_str': format_duration(duration),
                    'thumbnail': thumbnail,
                    'mp3_bytes': mp3_bytes,
                    'file_size_mb': f"{file_size_mb:.2f} MB",
                    'file_name': f"{sanitize_filename(title)}.mp3"
                }

            except Exception as e:
                last_error = e
                # 403 Forbidden 오류가 발생하면 다음 전략으로 자동 전환
                if "403" in str(e):
                    continue
                else:
                    raise e

    # 모든 전략 실패 시 최종 오류 전달
    raise last_error


# --- UI 레이아웃 구성 ---

st.markdown('<div class="main-title">🎵 유튜브 최고음질 MP3 변환기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">스마트폰(아이폰·갤럭시)과 PC 어디서나 유튜브를 초고음질 MP3로 다운로드하세요</div>', unsafe_allow_html=True)

# 1. URL 입력란
url_input = st.text_input(
    "유튜브 영상 링크 입력",
    placeholder="https://www.youtube.com/watch?v=... 또는 https://youtu.be/...",
    help="유튜브 앱이나 브라우저에서 '공유' → '링크 복사' 후 붙여넣으세요."
)

col1, col2 = st.columns([2, 1])
with col1:
    quality_option = st.selectbox(
        "음질 선택",
        options=["320", "256", "192", "128"],
        index=0,
        format_func=lambda x: f"{x} kbps (최고음질)" if x == "320" else f"{x} kbps"
    )
with col2:
    st.write("") # 간격 맞춤
    st.write("")
    convert_btn = st.button("🚀 MP3 변환 시작", type="primary", use_container_width=True)

# 세션 상태 초기화
if "conversion_result" not in st.session_state:
    st.session_state.conversion_result = None

# 변환 버튼 클릭 시 처리
if convert_btn:
    url = url_input.strip()
    if not url:
        st.warning("⚠️ 유튜브 영상 링크를 입력해 주세요.")
    elif not ("youtube.com" in url or "youtu.be" in url):
        st.error("❌ 올바른 유튜브 링크 형식이 아닙니다.")
    else:
        with st.spinner("🎧 유튜브 오디오 추출 및 MP3 인코딩 중입니다... (영상 길이에 따라 수 초~수십 초 소요)"):
            try:
                result = process_youtube_to_mp3(url, quality_option)
                st.session_state.conversion_result = result
                st.success("✅ MP3 변환이 성공적으로 완료되었습니다!")
            except Exception as e:
                st.session_state.conversion_result = None
                error_msg = str(e)
                if "Sign in to confirm you're not a bot" in error_msg or "403" in error_msg:
                    st.error("❌ 유튜브 봇 방지 정책(403 Forbidden)으로 인해 다운로드가 일시 차단되었습니다. 다른 영상으로 시도하거나 잠시 후 다시 시도해 주세요.")
                elif "Video unavailable" in error_msg:
                    st.error("❌ 영상을 찾을 수 없거나 비공개/삭제된 영상입니다.")
                else:
                    st.error(f"❌ 변환 도중 오류가 발생했습니다: {error_msg}")

# 변환 결과 출력
if st.session_state.conversion_result:
    res = st.session_state.conversion_result

    st.markdown("---")
    st.markdown("### 🎶 변환 완료된 음원 정보")

    col_thumb, col_info = st.columns([1, 2])
    with col_thumb:
        if res.get('thumbnail'):
            st.image(res['thumbnail'], use_container_width=True)
    with col_info:
        st.markdown(f"**제목:** {res['title']}")
        st.markdown(f"**채널명:** {res['uploader']}")
        st.markdown(f"**재생시간:** {res['duration_str']}")
        st.markdown(f"**파일 크기:** {res['file_size_mb']} ({quality_option}kbps)")

    # 바로 듣기 플레이어
    st.markdown("##### 🔊 미리듣기")
    st.audio(res['mp3_bytes'], format="audio/mp3")

    # 다운로드 버튼
    st.download_button(
        label=f"📥 MP3 다운로드 ({res['file_size_mb']})",
        data=res['mp3_bytes'],
        file_name=res['file_name'],
        mime="audio/mpeg",
        use_container_width=True
    )

    if st.button("🔄 다른 영상 변환하기", use_container_width=True):
        st.session_state.conversion_result = None
        st.rerun()

# 이용 안내 가이드 (다크모드/라이트모드 자동 대응 st.info)
st.markdown("---")
st.info("""
**💡 기기별 다운로드 안내**
* **아이폰 / 아이패드 (iOS)**: Safari 브라우저에서 'MP3 다운로드' 버튼 클릭 후 상단 주소창 다운로드 아이콘(↓) 또는 **'파일' 앱 → '다운로드'** 폴더에서 확인 가능합니다.
* **갤럭시 / 안드로이드**: Chrome 또는 삼성 인터넷에서 다운로드 버튼을 누르면 기기의 **'내 파일' → '다운로드'** 폴더에 즉시 저장됩니다.
* **PC (Windows / Mac)**: 클릭 즉시 컴퓨터의 기본 **'다운로드'** 폴더로 저장됩니다.
""")

st.markdown('<div class="footer-note">개인 소장 및 연구/학습 목적에 한해 사용하시기 바라며, 저작권법을 준수해 주세요.</div>', unsafe_allow_html=True)
