"""
수면 시간 데이터 분석과 시각화 - Streamlit 인터랙티브 대시보드
슬라이드 ④ [인터랙티브 기능 구상] 실습용

실행 방법:
1. 터미널에서: pip install streamlit pandas plotly
2. 같은 폴더에 Sleep_health_and_lifestyle_dataset.csv 파일 준비
3. 터미널에서: streamlit run sleep_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────────────────────────
# 페이지 설정
# ────────────────────────────────
st.set_page_config(page_title="수면 시간 데이터 분석", layout="wide")

st.title("😴 수면 시간과 스트레스, 정말 관계가 있을까?")
st.markdown("데이터를 직접 조작하며 수면 습관이 건강에 미치는 영향을 탐색해 보자.")

# ────────────────────────────────
# 데이터 로드
# ────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Sleep_health_and_lifestyle_dataset.csv")
    df["Sleep Disorder"] = df["Sleep Disorder"].fillna("None")
    return df

df = load_data()

# ────────────────────────────────
# 사이드바 - 인터랙티브 컨트롤
# ────────────────────────────────
st.sidebar.header("🔧 조건을 설정해 보자")

# ① 드롭다운 - 성별 선택
gender_option = st.sidebar.selectbox(
    "성별 선택",
    options=["전체"] + sorted(df["Gender"].unique().tolist())
)

# ② 드롭다운(다중선택) - 직업 선택
occupation_options = st.sidebar.multiselect(
    "직업 선택 (여러 개 선택 가능)",
    options=sorted(df["Occupation"].unique().tolist()),
    default=sorted(df["Occupation"].unique().tolist())
)

# ③ 슬라이더 - 수면 시간 범위
sleep_range = st.sidebar.slider(
    "수면 시간 범위 (시간)",
    min_value=float(df["Sleep Duration"].min()),
    max_value=float(df["Sleep Duration"].max()),
    value=(float(df["Sleep Duration"].min()), float(df["Sleep Duration"].max())),
    step=0.1
)

# ④ 버튼 - 수면장애 있는 사람만 보기
show_disorder_only = st.sidebar.checkbox("수면장애가 있는 사람만 보기")

# ────────────────────────────────
# 필터링
# ────────────────────────────────
filtered = df.copy()

if gender_option != "전체":
    filtered = filtered[filtered["Gender"] == gender_option]

if occupation_options:
    filtered = filtered[filtered["Occupation"].isin(occupation_options)]

filtered = filtered[
    (filtered["Sleep Duration"] >= sleep_range[0]) &
    (filtered["Sleep Duration"] <= sleep_range[1])
]

if show_disorder_only:
    filtered = filtered[filtered["Sleep Disorder"] != "None"]

st.sidebar.markdown(f"**현재 선택된 데이터: {len(filtered)}명**")

# ────────────────────────────────
# 메인 - 요약 지표
# ────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("평균 수면 시간", f"{filtered['Sleep Duration'].mean():.1f}시간" if len(filtered) else "-")
col2.metric("평균 스트레스 수준", f"{filtered['Stress Level'].mean():.1f}" if len(filtered) else "-")
col3.metric("평균 심박수", f"{filtered['Heart Rate'].mean():.0f}bpm" if len(filtered) else "-")

st.divider()

# ────────────────────────────────
# 메인 그래프 1 - 산점도 (수면시간 vs 스트레스)
# ────────────────────────────────
st.subheader("📊 수면 시간과 스트레스 수준의 관계")

if len(filtered) > 0:
    fig1 = px.scatter(
        filtered,
        x="Sleep Duration",
        y="Stress Level",
        color="Occupation",
        size="Heart Rate",
        hover_data=["Gender", "Age", "Sleep Disorder"],
        trendline="ols",
        title="점 위에 마우스를 올려 세부 정보를 확인해 보자"
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("조건에 맞는 데이터가 없어요. 필터를 조정해 보자.")

# ────────────────────────────────
# 메인 그래프 2 - 직업별 평균 수면시간 막대그래프
# ────────────────────────────────
st.subheader("💼 직업별 평균 수면 시간")

if len(filtered) > 0:
    occ_avg = filtered.groupby("Occupation")["Sleep Duration"].mean().sort_values()
    fig2 = px.bar(
        occ_avg,
        orientation="h",
        labels={"value": "평균 수면 시간(시간)", "Occupation": "직업"},
        title="어떤 직업이 가장 적게/많이 잘까?"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ────────────────────────────────
# 메인 그래프 3 - 수면장애 분포
# ────────────────────────────────
st.subheader("🩺 수면 장애 분포")

if len(filtered) > 0:
    disorder_count = filtered["Sleep Disorder"].value_counts().reset_index()
    disorder_count.columns = ["Sleep Disorder", "count"]
    fig3 = px.pie(
        disorder_count,
        names="Sleep Disorder",
        values="count",
        title="선택된 그룹의 수면장애 비율"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ────────────────────────────────
# 학생 활동 - 발견한 인사이트 작성란
# ────────────────────────────────
st.divider()
st.subheader("✍️ 내가 발견한 인사이트")
insight = st.text_area(
    "위 그래프를 조작해 보면서 발견한 흥미로운 점을 적어 보자.",
    placeholder="예: 수면 시간이 6시간 미만인 그룹은 스트레스 수준이 눈에 띄게 높았다..."
)
if st.button("저장하기"):
    st.success("작성한 내용을 캡처하거나 워크시트에 옮겨 적어 발표 자료로 활용해 보자!")
