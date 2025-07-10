import streamlit as st
import pandas as pd
import numpy as np

# 页面设置
st.set_page_config(
    page_title="区县集客业务管理工具",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("区县集客业务管理工具")

# 创建Tab标签页（新增第3个标签）
tab1, tab2, tab3 = st.tabs([
    "投诉及重复故障管理",
    "集客业务交付管理",
    "专线退服管控"
])

# --------------------------
# Tab1: 投诉及重复故障管理
# --------------------------
with tab1:
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
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="resolve_rate_base",
            value=85.00
        )
    with col2:
        resolve_rate_challenge = st.number_input(
            "解决率挑战值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="resolve_rate_challenge",
            value=100.00
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
                resolve_rate = st.number_input(
                    f"{district}重复故障解决率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_resolve_rate",
                    value=85.00
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
                resolve_rate = st.number_input(
                    f"{district}重复故障解决率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_resolve_rate_2",
                    value=85.00
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
            "解决率(%)": lambda x: f"{x:.2f}%",  # 显示两位小数
            "投诉得分": lambda x: f"{x}",
            "解决率得分": lambda x: f"{x}",
            "总分": lambda x: f"{x}"
        }))

        # 全市数据明细说明
        st.markdown(f"""
        #### 全市得分计算说明
        - 投诉次数：{total_complaints}次（各区县之和）
        - 重复投诉状态：{"有" if has_city_repeated else "无"}
        - 解决率平均值：{avg_resolve_rate:.2f}%
        - 投诉压降得分：{city_complaint_score}/1.5分（挑战值:{district_params["全市"]["挑战值"]}, 基准值:{district_params["全市"]["基准值"]}）
        - 解决率得分：{city_resolve_score}/1.5分（基准值:{resolve_rate_base:.2f}%, 挑战值:{resolve_rate_challenge:.2f}%）
        - 全市总分：{city_total_score}/3分
        """)

# --------------------------
# Tab2: 集客业务交付管理
# --------------------------
with tab2:
    st.write("设置集客业务交付的考核标准，输入各区县及时率和成功率数据计算得分")

    # 1. 交付考核参数设置（可修改，带默认值）
    st.subheader("1. 交付考核参数设置")
    st.info("设置交付及时率和成功率的基准值与挑战值（支持小数点后两位）", icon="📋")

    col1, col2 = st.columns(2)
    with col1:
        st.write("#### 交付及时率考核参数")
        ontime_base = st.number_input(
            "及时率基准值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,  # 精确到小数点后两位
            key="ontime_base",
            value=94.00
        )
        ontime_challenge = st.number_input(
            "及时率挑战值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="ontime_challenge",
            value=96.00
        )

    with col2:
        st.write("#### 交付成功率考核参数")
        success_base = st.number_input(
            "成功率基准值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="success_base",
            value=90.00
        )
        success_challenge = st.number_input(
            "成功率挑战值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="success_challenge",
            value=95.00
        )

    # 2. 数据输入模块（数字输入框，支持小数点后两位）
    with st.form("delivery_data_form"):
        st.subheader("2. 各区县交付数据输入")

        districts = ["东区", "高新", "西区", "仁和", "米易", "盐边"]
        delivery_data = {}
        col1, col2 = st.columns(2)

        with col1:
            for district in districts[:3]:
                st.write(f"### {district}")
                ontime_rate = st.number_input(
                    f"{district}交付及时率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_ontime_rate",
                    value=95.00  # 默认值
                )
                success_rate = st.number_input(
                    f"{district}交付成功率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_success_rate",
                    value=93.00  # 默认值
                )
                delivery_data[district] = {
                    "及时率(%)": ontime_rate,
                    "成功率(%)": success_rate
                }

        with col2:
            for district in districts[3:]:
                st.write(f"### {district}")
                ontime_rate = st.number_input(
                    f"{district}交付及时率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_ontime_rate_2",
                    value=95.00
                )
                success_rate = st.number_input(
                    f"{district}交付成功率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_success_rate_2",
                    value=93.00
                )
                delivery_data[district] = {
                    "及时率(%)": ontime_rate,
                    "成功率(%)": success_rate
                }

        # 提交按钮
        submit_delivery = st.form_submit_button("计算交付得分", type="primary")


    # 计算及时率得分函数（满分2分）
    def calculate_ontime_score(rate):
        if rate >= ontime_challenge:
            return 2.0  # 达到挑战值得满分
        elif rate >= ontime_base:
            # 基准值得60%（1.2分），挑战值与基准值间线性得分
            score_range = 2.0 - 1.2  # 0.8分区间
            rate_range = ontime_challenge - ontime_base
            if rate_range == 0:
                return 2.0
            score_per_unit = score_range / rate_range
            return round(1.2 + score_per_unit * (rate - ontime_base), 2)
        else:
            return 0.0  # 低于基准值不得分


    # 计算成功率得分函数（满分2分）
    def calculate_success_score(rate):
        if rate >= success_challenge:
            return 2.0  # 达到挑战值得满分
        elif rate >= success_base:
            # 基准值得60%（1.2分），挑战值与基准值间线性得分
            score_range = 2.0 - 1.2  # 0.8分区间
            rate_range = success_challenge - success_base
            if rate_range == 0:
                return 2.0
            score_per_unit = score_range / rate_range
            return round(1.2 + score_per_unit * (rate - success_base), 2)
        else:
            return 0.0  # 低于基准值不得分


    # 显示计算结果
    if submit_delivery:
        st.subheader("各区县交付得分计算结果")

        # 准备结果数据
        results = []
        total_ontime_rate = 0.0
        total_success_rate = 0.0

        for district, data in delivery_data.items():
            ontime_score = calculate_ontime_score(data["及时率(%)"])
            success_score = calculate_success_score(data["成功率(%)"])
            total_score = round(ontime_score + success_score, 2)

            results.append({
                "区县": district,
                "及时率(%)": data["及时率(%)"],
                "及时率得分": ontime_score,
                "成功率(%)": data["成功率(%)"],
                "成功率得分": success_score,
                "总分": total_score
            })

            # 累加计算全市平均值
            total_ontime_rate += data["及时率(%)"]
            total_success_rate += data["成功率(%)"]

        # 计算全市平均值
        avg_ontime_rate = round(total_ontime_rate / len(districts), 2)
        avg_success_rate = round(total_success_rate / len(districts), 2)
        city_ontime_score = calculate_ontime_score(avg_ontime_rate)
        city_success_score = calculate_success_score(avg_success_rate)
        city_total_score = round(city_ontime_score + city_success_score, 2)

        # 添加全市数据到结果
        results.append({
            "区县": "全市",
            "及时率(%)": avg_ontime_rate,
            "及时率得分": city_ontime_score,
            "成功率(%)": avg_success_rate,
            "成功率得分": city_success_score,
            "总分": city_total_score
        })

        # 显示表格（数据居中显示）
        result_df = pd.DataFrame(results)
        st.table(result_df.style.set_table_styles([
            {"selector": "td", "props": [("text-align", "center")]},
            {"selector": "th", "props": [("text-align", "center")]}
        ]).format({
            "及时率(%)": lambda x: f"{x:.2f}%",  # 显示两位小数
            "及时率得分": lambda x: f"{x}",
            "成功率(%)": lambda x: f"{x:.2f}%",
            "成功率得分": lambda x: f"{x}",
            "总分": lambda x: f"{x}"
        }))

        # 全市数据明细说明
        st.markdown(f"""
        #### 全市得分计算说明
        - 及时率平均值：{avg_ontime_rate:.2f}%
        - 及时率得分：{city_ontime_score}/2分（基准值:{ontime_base:.2f}%, 挑战值:{ontime_challenge:.2f}%）
        - 成功率平均值：{avg_success_rate:.2f}%
        - 成功率得分：{city_success_score}/2分（基准值:{success_base:.2f}%, 挑战值:{success_challenge:.2f}%）
        - 全市总分：{city_total_score}/4分
        """)

# --------------------------
# Tab3: 专线退服管控（新增）
# --------------------------
with tab3:
    st.write("设置专线退服率考核标准和AAA专线故障系数，输入各区县数据计算得分")

    # 1. 退服率考核参数设置
    st.subheader("1. 退服率考核参数设置")
    st.info("设置专线退服率的基准值和挑战值（支持小数点后两位）", icon="📋")

    col1, col2 = st.columns(2)
    with col1:
        downrate_base = st.number_input(
            "退服率基准值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="downrate_base",
            value=4.00  # 默认基准值4%
        )
    with col2:
        downrate_challenge = st.number_input(
            "退服率挑战值(%)",
            min_value=0.00,
            max_value=100.00,
            step=0.01,
            key="downrate_challenge",
            value=3.50  # 默认挑战值3.5%
        )

    # 2. AAA专线故障系数设置
    st.subheader("2. AAA专线故障系数设置")
    st.info("设置不同AAA中断次数对应的故障系数", icon="📋")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        factor_0 = st.number_input(
            "中断0次系数",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="factor_0",
            value=1.0
        )
    with col2:
        factor_1 = st.number_input(
            "中断1次系数",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="factor_1",
            value=0.8
        )
    with col3:
        factor_2 = st.number_input(
            "中断2次系数",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="factor_2",
            value=0.6
        )
    with col4:
        factor_3plus = st.number_input(
            "中断3次及以上系数",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            key="factor_3plus",
            value=0.0
        )

    # 创建中断次数到系数的映射
    aaa_factors = {
        0: factor_0,
        1: factor_1,
        2: factor_2,
        3: factor_3plus  # 3次及以上使用相同系数
    }

    # 3. 数据输入模块
    with st.form("downservice_data_form"):
        st.subheader("3. 各区县专线退服数据输入")

        districts = ["东区", "高新", "西区", "仁和", "米易", "盐边"]
        downservice_data = {}
        col1, col2 = st.columns(2)

        with col1:
            for district in districts[:3]:
                st.write(f"### {district}")
                down_rate = st.number_input(
                    f"{district}专线退服率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_down_rate",
                    value=3.00  # 默认值
                )
                aaa_interruptions = st.number_input(
                    f"{district}AAA专线中断次数",
                    min_value=0,
                    max_value=10,
                    step=1,
                    key=f"{district}_aaa_interruptions",
                    value=0,
                    format="%d"
                )
                downservice_data[district] = {
                    "退服率(%)": down_rate,
                    "AAA中断次数": aaa_interruptions
                }

        with col2:
            for district in districts[3:]:
                st.write(f"### {district}")
                down_rate = st.number_input(
                    f"{district}专线退服率(%)",
                    min_value=0.00,
                    max_value=100.00,
                    step=0.01,
                    key=f"{district}_down_rate_2",
                    value=3.00
                )
                aaa_interruptions = st.number_input(
                    f"{district}AAA专线中断次数",
                    min_value=0,
                    max_value=10,
                    step=1,
                    key=f"{district}_aaa_interruptions_2",
                    value=0,
                    format="%d"
                )
                downservice_data[district] = {
                    "退服率(%)": down_rate,
                    "AAA中断次数": aaa_interruptions
                }

        # 提交按钮
        submit_downservice = st.form_submit_button("计算退服管控得分", type="primary")


    # 计算退服率得分函数（满分4分）
    def calculate_downrate_score(rate):
        if rate <= downrate_challenge:
            return 4.0  # 达到挑战值得满分
        elif rate <= downrate_base:
            # 基准值得60%（2.4分），挑战值与基准值间线性得分
            score_range = 4.0 - 2.4  # 1.6分区间
            rate_range = downrate_base - downrate_challenge
            if rate_range == 0:
                return 4.0
            score_per_unit = score_range / rate_range
            return round(2.4 + score_per_unit * (downrate_base - rate), 2)
        else:
            return 0.0  # 超过基准值不得分


    # 计算AAA中断系数
    def get_aaa_factor(interruptions):
        return aaa_factors[min(interruptions, 3)]  # 3次及以上使用factor_3plus


    # 显示计算结果
    if submit_downservice:
        st.subheader("各区县专线退服管控得分计算结果")

        # 准备结果数据
        results = []
        total_down_rate = 0.0
        total_aaa_interruptions = 0

        for district, data in downservice_data.items():
            # 计算退服率得分
            downrate_score = calculate_downrate_score(data["退服率(%)"])

            # 获取AAA中断系数
            aaa_factor = get_aaa_factor(data["AAA中断次数"])

            # 计算总得分
            total_score = round(downrate_score * aaa_factor, 2)

            results.append({
                "区县": district,
                "退服率(%)": data["退服率(%)"],
                "退服率得分": downrate_score,
                "AAA中断次数": data["AAA中断次数"],
                "AAA系数": aaa_factor,
                "总分": total_score
            })

            # 累加计算全市平均值
            total_down_rate += data["退服率(%)"]
            total_aaa_interruptions += data["AAA中断次数"]

        # 计算全市平均值
        avg_down_rate = round(total_down_rate / len(districts), 2)
        avg_aaa_interruptions = round(total_aaa_interruptions / len(districts))
        city_downrate_score = calculate_downrate_score(avg_down_rate)
        city_aaa_factor = get_aaa_factor(avg_aaa_interruptions)
        city_total_score = round(city_downrate_score * city_aaa_factor, 2)

        # 添加全市数据到结果
        results.append({
            "区县": "全市",
            "退服率(%)": avg_down_rate,
            "退服率得分": city_downrate_score,
            "AAA中断次数": avg_aaa_interruptions,
            "AAA系数": city_aaa_factor,
            "总分": city_total_score
        })

        # 显示表格（数据居中显示）
        result_df = pd.DataFrame(results)
        st.table(result_df.style.set_table_styles([
            {"selector": "td", "props": [("text-align", "center")]},
            {"selector": "th", "props": [("text-align", "center")]}
        ]).format({
            "退服率(%)": lambda x: f"{x:.2f}%",
            "退服率得分": lambda x: f"{x}",
            "AAA中断次数": lambda x: f"{x}次",
            "AAA系数": lambda x: f"{x}",
            "总分": lambda x: f"{x}"
        }))

        # 全市数据明细说明
        st.markdown(f"""
        #### 全市得分计算说明
        - 退服率平均值：{avg_down_rate:.2f}%
        - 退服率得分：{city_downrate_score}/4分（基准值:{downrate_base:.2f}%, 挑战值:{downrate_challenge:.2f}%）
        - AAA中断次数平均值：{avg_aaa_interruptions}次
        - AAA系数：{city_aaa_factor}
        - 全市总分：{city_total_score}/4分
        """)
