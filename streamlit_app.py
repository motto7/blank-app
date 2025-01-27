import streamlit as st
import pandas as pd

# ======= 데이터 준비 =======
# 1. 주차별 스크립트 데이터
script_data = [
    {"Korean": "공식적으로 2024년 첫 수업이야!", "English": "It is officially THE first class of 2024."},
    {"Korean": "이건 진짜 꼭 말해야 할 게, 여러분들이 내 수업에 가져준 신뢰가 진짜 거의 비현실적이었어. 완전 혼 나감..", 
     "English": "I just have to let this one out: your trust in my class? Unreal/Surreal. Blown away!"},
    {"Korean": "아직도 그렇게 쉽게 $170 을 무슨 짤짤이 마냥 결제해준 게 정말 아직도 믿겨지지가 않아.", 
     "English": "I still can't get over how so many of you were willing to shell out that $170 CASUALLY. like it was pocket change."},
    {"Korean": "아무튼 우리의 앞으로 12개월간 우리의 계획은 이거야.", 
     "English": "So here's the game plan for the next whole 12 months:"},
]

# 2. Key phrases 데이터
key_phrases_data = [
    {"ID": 1, "Key Phrase": "THE", "Usage": "명사를 강조시키기 위해서 씀", 
     "Examples": [
         {"English": "It is THE best restaurant in town!", "Korean": "이것은 그 도시 최고의 식당이다!"},
         {"English": "He’s THE sexiest man alive!", "Korean": "그는 살아있는 가장 섹시한 남자다!"},
         {"English": "We’re honored to have THE Dr. Andrew Huberman speak at our event.", "Korean": "우리 행사에서 Andrew Huberman 박사님을 모시게 되어 영광입니다!"}
     ]},
    {"ID": 2, "Key Phrase": "have to let this one out", "Usage": "이건 말해야겠어 진짜", 
     "Examples": [
         {"English": "I just gotta let this one out, you were DROP DEAD GORGEOUS that night!!", "Korean": "정말 이건 말해야겠어, 너는 그날 정말 환상적으로 아름다웠어!!"}
     ]},
]


# ======= Streamlit App =======
def main():
    st.title("📘 Re-Naldae with ddulbi")
    st.sidebar.title("Menu")
    menu = st.sidebar.selectbox("Choose an option", ["📖 주차별 스크립트", "🔑 Key Phrases 학습", "✍️ 작문 연습", "🎯 퀴즈"])

    if menu == "📖 주차별 스크립트":
        show_weekly_script()
    elif menu == "🔑 Key Phrases 학습":
        show_key_phrases()
    elif menu == "✍️ 작문 연습":
        show_writing_practice()
    elif menu == "🎯 퀴즈":
        show_quiz()

# 주차별 스크립트
def show_weekly_script():
    st.header("📖 주차별 스크립트 학습")
    week = st.selectbox("회차를 선택하세요", options=[f"1-{i+1}" for i in range(len(script_data))])
    selected_script = script_data[int(week.split("-")[1]) - 1]
    st.subheader("📝 스크립트")
    st.write(f"**Korean**: {selected_script['Korean']}")
    st.write(f"**English**: {selected_script['English']}")

# Key Phrases 학습
def show_key_phrases():
    st.header("🔑 Key Phrases 학습")
    if "key_phrase_index" not in st.session_state:
        st.session_state["key_phrase_index"] = 0
    if "example_index" not in st.session_state:
        st.session_state["example_index"] = 0
    if "show_translation" not in st.session_state:
        st.session_state["show_translation"] = False

    current_index = st.session_state["key_phrase_index"]
    example_index = st.session_state["example_index"]
    current_phrase = key_phrases_data[current_index]

    st.subheader(f"Key Phrase: {current_phrase['Key Phrase']}")
    st.write(f"**Usage**: {current_phrase['Usage']}")

    current_example = current_phrase['Examples'][example_index]
    st.write(f"**Example**: {current_example['English']}")

    if st.button("번역 보기"):
        st.session_state["show_translation"] = True

    if st.session_state["show_translation"]:
        st.write(f"**Korean Translation**: {current_example['Korean']}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("다른 예시 보기"):
            st.session_state["example_index"] = (example_index + 1) % len(current_phrase['Examples'])
            st.session_state["show_translation"] = False  # 번역 초기화
    with col2:
        if st.button("다음 Key Phrase"):
            st.session_state["key_phrase_index"] = (current_index + 1) % len(key_phrases_data)
            st.session_state["example_index"] = 0
            st.session_state["show_translation"] = False  # 번역 초기화

# 작문 연습

def show_writing_practice():
    st.header("✍️ Key Phrases로 작문 연습")
    if "writing_index" not in st.session_state:
        st.session_state["writing_index"] = 0

    current_index = st.session_state["writing_index"]
    current_phrase = key_phrases_data[current_index]

    st.subheader(f"Key Phrase: {current_phrase['Key Phrase']}")
    st.write(f"**Usage**: {current_phrase['Usage']}")
    user_input = st.text_area(f"'{current_phrase['Key Phrase']}'를 사용하여 문장을 작성해 보세요:")

    if st.button("저장"):
        st.success(f"작성된 문장: {user_input}")
        st.info("작문이 저장되었습니다!")

    if st.button("다음", key="writing_next"):
        st.session_state["writing_index"] = (current_index + 1) % len(key_phrases_data)

# 퀴즈
def show_quiz():
    st.header("🎯 퀴즈: 한국어 -> 영어 변환")

    # 세션 상태 초기화
    if "quiz_index" not in st.session_state:
        st.session_state["quiz_index"] = 0
    if "score" not in st.session_state:
        st.session_state["score"] = 0
    if "answer_submitted" not in st.session_state:
        st.session_state["answer_submitted"] = False

    # 현재 퀴즈 문제 가져오기
    current_index = st.session_state["quiz_index"]
    current_quiz = script_data[current_index]

    # 문제 표시
    st.subheader(f"문제 {current_index + 1}:")
    st.write(f"**한국어**: {current_quiz['Korean']}")

    # 정답 입력
    user_answer = st.text_input("번역을 입력하세요:")

    # 정답 확인 버튼
    if st.button("정답 확인") and not st.session_state["answer_submitted"]:
        if user_answer.lower() == current_quiz["English"].lower():
            st.success("정답입니다! 🎉")
            st.session_state["score"] += 1
        else:
            st.error(f"오답입니다. 정답: {current_quiz['English']}")
        st.session_state["answer_submitted"] = True

    # 다음 문제로 넘어가는 버튼
    if st.session_state["answer_submitted"]:
        if st.button("다음"):
            if current_index + 1 < len(script_data):  # 다음 문제가 있으면 진행
                st.session_state["quiz_index"] += 1
                st.session_state["answer_submitted"] = False
            else:
                st.write("모든 문제를 완료했습니다! 🎉")
                st.write(f"최종 점수: {st.session_state['score']} / {len(script_data)}")
                if st.button("다시 시작"):
                    st.session_state["quiz_index"] = 0
                    st.session_state["score"] = 0
                    st.session_state["answer_submitted"] = False


if __name__ == "__main__":
    main()
