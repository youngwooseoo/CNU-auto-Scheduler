import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# CSV 불러오기 (예시)
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # 그 다음부터 df를 활용하는 기존 코드가 이어지면 돼

# 학과 리스트 추출
departments = sorted(df['운영학과'].dropna().unique())

# --- 사이드바 필터 설정 ---
st.sidebar.header("🎓 조건 설정")

# 학과 검색 선택 필터
selected_major = st.sidebar.selectbox("전공 학과를 검색해 선택하세요", departments)

# 공강 요일 선택 (다중 선택)
days = ['월', '화', '수', '목', '금']
no_lecture_days = st.sidebar.multiselect("공강 희망 요일", days)

# 수업 방식 선택 (다중)
lecture_modes = st.sidebar.multiselect("수업 방식", ['대면수업', '화상강의'])

# 평가 방식 (단일 선택)
grading = st.sidebar.radio("평가 방식", ['상대평가', '절대평가'], index=0)

# --- 필터링 ---
filtered = df.copy()
if selected_major:
    filtered = filtered[filtered['운영학과'] == selected_major]
if grading:
    filtered = filtered[filtered['평가방식'] == grading]
if lecture_modes:
    filtered = filtered[filtered['수업방식'].isin(lecture_modes)]
if no_lecture_days:
    for day in no_lecture_days:
        filtered = filtered[~filtered['수업시간'].astype(str).str.contains(day)]

st.write(f"🔍 조건에 맞는 과목 수: {len(filtered)}개")
st.dataframe(filtered[['과목명', '운영학과', '수업시간', '수업방식', '평가방식']].reset_index(drop=True))

# --- 시간표 시각화 ---
st.subheader("🗓️ 추천 시간표 시각화")
day_order = ['월', '화', '수', '목', '금']
day_to_x = {day: i for i, day in enumerate(day_order)}

fig, ax = plt.subplots(figsize=(10, 6))
for x in range(5):
    for y in range(8, 19):
        ax.add_patch(
            patches.Rectangle((x, y), 1, 1, edgecolor='lightgray', facecolor='white', lw=1)
        )

for i, row in filtered.iterrows():
    time_info = str(row['수업시간'])
    matches = [(d, t.split('~')) for d in day_order if d in time_info for t in [time_info.split(d)[-1].strip().split(',')[0]] if '~' in t]
    for day, (start, end) in matches:
        try:
            start_h = int(start.split(':')[0])
            end_h = int(end.split(':')[0])
            ax.add_patch(
                patches.Rectangle(
                    (day_to_x[day], start_h), 0.95, end_h - start_h,
                    edgecolor='black', facecolor='#AED6F1', lw=1
                )
            )
            ax.text(day_to_x[day] + 0.5, start_h + 0.5, row['과목명'], ha='center', va='center', fontsize=7)
        except:
            continue

ax.set_xlim(0, 5)
ax.set_ylim(8, 19)
ax.set_xticks(range(5))
ax.set_xticklabels(day_order)
ax.set_yticks(range(8, 20))
ax.set_ylabel("시간")
ax.set_title("시간표 타임테이블")
ax.axis("off")

st.pyplot(fig)
