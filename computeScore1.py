import streamlit as st
import pandas as pd
import numpy as np

# 页面设置
st.set_page_config(
    page_title="区县集客投诉管理得分计算工具",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("区县集客投诉管理得分计算工具")
st.write("先设置各区县及全市的基准值和挑战值，再输入投诉数据进行计算")

# 1. 参数设置模块
st.subheader("1. 考核参数设置")
st.info("请设置重复故障解决率的考核标准及各区县投诉考核参数", icon="📝")

# 重复故障解决率参数设置
st.write("#### 重复故障解决率考核参数")
col1, col2 = st.columns(2)
with col1:
    resolve_rate_base = st.number_input(
        "解决率基准值(%)",
        min_value=0,
        max_value=100,
        step=1,
        key="resolve_rate_base",
        value=85
    )
with col2:
    resolve_rate_challenge = st.number_input(
        "解决率挑战值(%)",
        min_value=0,
        max_value=100,
        step=1,
        key="resolve_rate_challenge",
        value=100
    )

# 区县投诉考核参数设置
st.write("#### 各区县投诉考核参数")
districts = ["东区", "高新", "西区", "仁和", "米易", "盐边", "全市"]
district_params = {}

# 定义各区县默认基准值
default_bases = {
    "东区": 3,
    "高新": 1,
    "西区": 2,
    "仁和": 2,
    "米易": 2,
    "盐边": 2,
    "全市": 12
}

col1, col2 = st.columns(2)
with col1:
    for district in districts[:3]:
        with st.container():
            st.write(f"##### {district}")
            challenge = st.number_input(
                f"{district}挑战值",
                min_value=0,
                step=1,
                key=f"{district}_challenge",
                value=0
            )
            base = st.number_input(
                f"{district}基准值",
                min_value=0,
                step=1,
                key=f"{district}_base",
                value=default_bases[district]
            )
            district_params[district] = {"挑战值": challenge, "基准值": base}

with col2:
    for district in districts[3:6]:
        with st.container():
            st.write(f"##### {district}")
            challenge = st.number_input(
                f"{district}挑战值",
                min_value=0,
                step=1,
                key=f"{district}_challenge_2",
                value=0
            )
            base = st.number_input(
                f"{district}基准值",
                min_value=0,
                step=1,
                key=f"{district}_base_2",
                value=default_bases[district]
            )
            district_params[district] = {"挑战值": challenge, "基准值": base}

    # 全市参数输入
    with st.container():
        st.write("##### 全市")
        challenge = st.number_input(
            "全市挑战值",
            min_value=0,
            step=1,
            key="city_challenge",
            value=0
        )
        base = st.number_input(
            "全市基准值",
            min_value=0,
            step=1,
            key="city_base",
            value=12
        )
        district_params["全市"] = {"挑战值": challenge, "基准值": base}

# 2. 数据输入模块
with st.form("district_data_form"):
    st.subheader("2. 各区县投诉数据输入")

    district_data = {}
    col1, col2 = st.columns(2)

    with col1:
        for district in districts[:3]:
            st.write(f"### {district}")
            complaints = st.number_input(
                f"{district}投诉次数",
                min_value=0,
                step=1,
                key=f"{district}_complaints",
                format="%d"
            )
            has_repeated = st.checkbox(
                f"{district}是否有重复投诉",
                key=f"{district}_repeated"
            )
            resolve_rate = st.slider(
                f"{district}重复故障解决率(%)",
                min_value=0,
                max_value=100,
                value=85,
                key=f"{district}_resolve_rate",
                format="%d%%"
            )
            district_data[district] = {
                "投诉次数": complaints,
                "重复投诉": has_repeated,
                "解决率": resolve_rate
            }

    with col2:
        for district in districts[3:6]:
            st.write(f"### {district}")
            complaints = st.number_input(
                f"{district}投诉次数",
                min_value=0,
                step=1,
                key=f"{district}_complaints_2",
                format="%d"
            )
            has_repeated = st.checkbox(
                f"{district}是否有重复投诉",
                key=f"{district}_repeated_2"
            )
            resolve_rate = st.slider(
                f"{district}重复故障解决率(%)",
                min_value=0,
                max_value=100,
                value=85,
                key=f"{district}_resolve_rate_2",
                format="%d%%"
            )
            district_data[district] = {
                "投诉次数": complaints,
                "重复投诉": has_repeated,
                "解决率": resolve_rate
            }

    # 提交按钮
    submitted = st.form_submit_button("计算得分", type="primary")


# 计算投诉压降得分函数
def calculate_complaint_score(complaints, district, has_repeated):
    """按线性规则计算投诉压降得分"""
    if district != "全市" and has_repeated:
        return 0.0  # 非全市且有重复投诉，得0分

    challenge = district_params[district]["挑战值"]
    base = district_params[district]["基准值"]

    if complaints <= challenge:
        return 1.5  # 达到挑战值得满分
    elif complaints <= base:
        score_range = 1.5 * 0.4
        x_range = base - challenge
        if x_range == 0:
            return 1.5
        score_per_unit = score_range / x_range
        return round(1.5 - score_per_unit * (complaints - challenge), 2)
    else:
        return 0.0  # 超过基准值不得分


# 计算重复故障解决率得分函数
def calculate_resolve_rate_score(rate):
    """按线性规则计算重复故障解决率得分"""
    if rate >= resolve_rate_challenge:
        return 1.5  # 达到挑战值得满分
    elif rate >= resolve_rate_base:
        score_range = 1.5 * 0.4
        rate_range = resolve_rate_challenge - resolve_rate_base
        if rate_range == 0:
            return 1.5
        score_per_percent = score_range / rate_range
        return round(0.9 + score_per_percent * (rate - resolve_rate_base), 2)
    else:
        return 0.0  # 低于基准值不得分


# 显示计算结果
if submitted:
    st.subheader("各区县及全市得分计算结果")

    # 准备区县数据
    results = []
    for district, data in district_data.items():
        complaint_score = calculate_complaint_score(
            data["投诉次数"], district, data["重复投诉"]
        )
        resolve_score = calculate_resolve_rate_score(data["解决率"])
        total_score = round(complaint_score + resolve_score, 2)

        results.append({
            "区县": district,
            "投诉次数": data["投诉次数"],
            "是否重复投诉": "是" if data["重复投诉"] else "否",
            "解决率(%)": data["解决率"],
            "投诉得分": complaint_score,
            "解决率得分": resolve_score,
            "总分": total_score
        })

    # 自动汇总全市数据
    total_complaints = sum([data["投诉次数"] for data in district_data.values()])
    has_city_repeated = any([data["重复投诉"] for data in district_data.values()])
    avg_resolve_rate = round(
        np.mean([data["解决率"] for data in district_data.values()]), 2
    )

    # 计算全市得分（忽略重复投诉）
    city_complaint_score = calculate_complaint_score(
        total_complaints, "全市", has_repeated=False
    )
    city_resolve_score = calculate_resolve_rate_score(avg_resolve_rate)
    city_total_score = round(city_complaint_score + city_resolve_score, 2)

    # 添加全市数据到结果
    results.append({
        "区县": "全市",
        "投诉次数": total_complaints,
        "是否重复投诉": "是" if has_city_repeated else "否",
        "解决率(%)": avg_resolve_rate,
        "投诉得分": city_complaint_score,
        "解决率得分": city_resolve_score,
        "总分": city_total_score
    })

    # 显示表格（数据居中显示）
    result_df = pd.DataFrame(results)
    st.table(result_df.style.set_table_styles([
        {"selector": "td", "props": [("text-align", "center")]},
        {"selector": "th", "props": [("text-align", "center")]}
    ]).format({
        "投诉次数": lambda x: f"{x}次",
        "解决率(%)": lambda x: f"{x}%",
        "投诉得分": lambda x: f"{x}",
        "解决率得分": lambda x: f"{x}",
        "总分": lambda x: f"{x}"
    }))

    # 全市数据明细说明
    st.markdown(f"""
    #### 全市得分计算说明
    - 投诉次数：{total_complaints}次（各区县之和）
    - 重复投诉状态：{"有" if has_city_repeated else "无"}
    - 解决率平均值：{avg_resolve_rate}%
    - 投诉压降得分：{city_complaint_score}/1.5分（挑战值:{district_params["全市"]["挑战值"]}, 基准值:{district_params["全市"]["基准值"]}）
    - 解决率得分：{city_resolve_score}/1.5分（基准值:{resolve_rate_base}%, 挑战值:{resolve_rate_challenge}%）
    - 全市总分：{city_total_score}/3分
    """)
