import streamlit as st
import pandas as pd
#import ssl
import gspread
from google.oauth2.service_account import Credentials

#ssl._create_default_https_context = ssl._create_unverified_context
# ======= Google Drive에서 데이터 로드 =======
@st.cache_data
#@retry(stop_max_attempt_number=3, wait_fixed=2000)
def connect_to_gsheets():

    #/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/certifi/cacert.pem
    creds = Credentials.from_service_account_file("/Users/jaehoon/Documents/service_account.json", scopes=[
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(creds)
    return client


def load_data():
    ssl._create_default_https_context = ssl._create_unverified_context
    """Google Drive에서 Excel 파일을 로드하여 DataFrame으로 변환"""
    sheet_id = "141c46fbsLvfVt_F4jf0Eqv5PCsUM4nikrgKpjsZpLUY"
    script_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv&gid=0"
    key_phrases_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=tsv&gid=478341413"
    #https://docs.google.com/spreadsheets/d/141c46fbsLvfVt_F4jf0Eqv5PCsUM4nikrgKpjsZpLUY/gviz/tq?tqx=out:tsv&sheet=script_data"
    # Google Sheets에서 데이터 로드
    script_df = pd.read_csv(script_url, sep="\t", names=["Korean", "English", "Week"])
    key_phrases_df = pd.read_csv(key_phrases_url, sep="\t", names=["Session", "Key Phrase", "ID", "Usage", "Example (English)", "Example (Korean)"])
    
    return script_df, key_phrases_df

# 데이터 로드
script_df, key_phrases_df = load_data()

# ======= 학습 완료 정보 저장 및 불러오기 =======
def load_completed_weeks():
    """Google Sheets에서 'completed_weeks' 시트 불러오기"""
    client = connect_to_gsheets()
    #client.open("가계부")
    sheet = client.open("naldae.tsv").worksheet("completed_weeks")
    data = sheet.get_all_records()
    return {row["Username"]: set(row["Completed Weeks"].split(", ")) for row in data}

def save_completed_week(username, selected_week):
    """Google Sheets의 'completed_weeks' 시트에 학습 완료 정보 저장"""
    client = connect_to_gsheets()
    sheet = client.open("naldae.tsv").worksheet("completed_weeks")
    
    completed_weeks = load_completed_weeks()

    if username not in completed_weeks:
        completed_weeks[username] = set()
    completed_weeks[username].add(selected_week)

    # Google Sheets 업데이트
    sheet.clear()  # 기존 데이터 삭제
    sheet.append_row(["Username", "Completed Weeks"])  # 헤더 추가

    for user, weeks in completed_weeks.items():
        sheet.append_row([user, ", ".join(weeks)])  # 사용자별 데이터 추가


# ======= 로그인 정보 설정 =======
USER_CREDENTIALS = {
    "admin": "admin123",
    "olseulbi": "user123"
}

# ======= 로그인 시스템 =======
if "username" not in st.session_state:
    st.session_state["username"] = None
if "completed_weeks" not in st.session_state:
    st.session_state["completed_weeks"] = {"admin": set(), "olseulbi": set()}

if not st.session_state["username"]:
    st.title("🔒 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["username"] = username

            if username == "olseulbi":
                st.success(f"Welcome, my love !")
            st.rerun()
        else:
            st.error("Invalid username or password.")
else:
    def main():
        st.title("📘 Re-Naldae with ddulbi")
        st.sidebar.title(f"Welcome, {st.session_state['username']}")
        menu = st.sidebar.selectbox("Choose an option", ["📖 주차별 스크립트", "🔑 Key Phrases 학습", "✍️ 작문 연습", "🎯 퀴즈", "🚪 로그아웃"])
        
        if menu == "📖 주차별 스크립트":
            show_weekly_script()
        elif menu == "🔑 Key Phrases 학습":
            show_key_phrases()
        elif menu == "✍️ 작문 연습":
            show_writing_practice()
        elif menu == "🎯 퀴즈":
            show_quiz()
        elif menu == "🚪 로그아웃":
            st.session_state["username"] = None
            st.rerun()

    # 주차별 스크립트 학습
    def show_weekly_script():
        st.header("📖 주차별 스크립트 학습")
        
        # 주차 목록 동적 생성
        week_list = script_df["Week"].unique()
        selected_week = st.selectbox("회차를 선택하세요", options=week_list)

        # 선택한 주차의 데이터 필터링
        week_data = script_df[script_df["Week"] == selected_week]

        # 출력
        for index, row in week_data.iterrows():
            st.subheader(f"📝 문장 {index + 1}")
            st.write(f"**Korean**: {row['Korean']}")
            st.write(f"**English**: {row['English']}")
        
        # 학습 완료 체크
        if st.button("이 주차 완료하기"):
            username = st.session_state["username"].lower()
        
            # Streamlit 세션 상태 업데이트
            st.session_state["completed_weeks"][username].add(selected_week)
            
            # Google Sheets에도 저장
            save_completed_week(username, selected_week)

            st.success("✅ 이 주차 완료 정보가 저장되었습니다!")

        # 완료된 주차 목록 표시
        completed_weeks = st.session_state["completed_weeks"][st.session_state["username"].lower()]
        if completed_weeks:
            st.write("✅ 완료된 주차:", ", ".join(completed_weeks))

    # Key Phrases 학습
    def show_key_phrases():
        st.header("🔑 Key Phrases 학습")
        if "key_phrase_index" not in st.session_state:
            st.session_state["key_phrase_index"] = 0

        current_index = st.session_state["key_phrase_index"]
        current_phrase = key_phrases_df.iloc[current_index]

        st.subheader(f"Key Phrase: {current_phrase['Key Phrase']}")
        st.write(f"**Usage**: {current_phrase['Usage']}")
        st.write(f"**Example (English)**: {current_phrase['Example (English)']}")

        if st.button("번역 보기"):
            st.write(f"**Example (Korean)**: {current_phrase['Example (Korean)']}")

        if st.button("다음 Key Phrase"):
            st.session_state["key_phrase_index"] = (current_index + 1) % len(key_phrases_df)

    # 실행
    if __name__ == "__main__":
        main()
