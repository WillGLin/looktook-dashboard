"""
郎园Station LookTook 营收成本测算看板
运行: streamlit run looktook_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================== 页面配置 ====================
st.set_page_config(page_title="LookTook 营收测算", page_icon="📊", layout="wide")

# ==================== 侧边栏参数配置 ====================
st.sidebar.divider()
st.sidebar.header("📐 全局参数配置")
st.sidebar.caption("💡 刷新页面可重置所有参数为默认值")

# --- 客流参数 ---
st.sidebar.subheader("客流参数")
base_traffic_weekday = st.sidebar.number_input("工作日基础客流", value=3000, step=100, key="traffic_weekday")
base_traffic_weekend = st.sidebar.number_input("周末基础客流", value=12000, step=100, key="traffic_weekend")
base_traffic_peak = st.sidebar.number_input("峰值客流", value=23000, step=100, key="traffic_peak")

# --- 季节权重 ---
st.sidebar.subheader("季节权重")
season_weights = {
    "冬季": st.sidebar.slider("冬季 (12-2月)", 0.0, 2.0, 0.30, 0.05, key="s_winter"),
    "春季": st.sidebar.slider("春季 (3-5月)", 0.0, 2.0, 1.10, 0.05, key="s_spring"),
    "夏季": st.sidebar.slider("夏季 (6-8月)", 0.0, 2.0, 1.60, 0.05, key="s_summer"),
    "秋季": st.sidebar.slider("秋季 (9-11月)", 0.0, 2.0, 1.00, 0.05, key="s_autumn"),
}

# --- 进店率 ---
st.sidebar.subheader("进店率")
entry_rate_weekday = st.sidebar.slider("工作日进店率", 0.01, 0.20, 0.10, 0.01, key="er_weekday")
entry_rate_weekend = st.sidebar.slider("周末进店率", 0.01, 0.20, 0.07, 0.01, key="er_weekend")
entry_rate_peak = st.sidebar.slider("峰值日进店率", 0.01, 0.20, 0.04, 0.01, key="er_peak")
entry_rates = {"工作日": entry_rate_weekday, "周末": entry_rate_weekend, "峰值日": entry_rate_peak}

# --- 成交率 ---
st.sidebar.subheader("成交率")
retail_conv_weekday = st.sidebar.slider("零售-工作日成交率", 0.05, 0.40, 0.1963, 0.01, key="rc_weekday")
retail_conv_weekend = st.sidebar.slider("零售-周末成交率", 0.05, 0.40, 0.1668, 0.01, key="rc_weekend")
retail_conv_peak = st.sidebar.slider("零售-峰值成交率", 0.05, 0.40, 0.1297, 0.01, key="rc_peak")
coffee_conv = st.sidebar.slider("咖啡成交率", 0.05, 0.40, 0.19, 0.01, key="cc")
retail_conv_rates = {"工作日": retail_conv_weekday, "周末": retail_conv_weekend, "峰值日": retail_conv_peak}

# --- 客单价 ---
st.sidebar.subheader("客单价")
retail_price_weekday = st.sidebar.number_input("零售-工作日客单", value=112, step=1, key="rp_weekday")
retail_price_weekend = st.sidebar.number_input("零售-周末客单", value=96, step=1, key="rp_weekend")
retail_price_peak = st.sidebar.number_input("零售-峰值客单", value=79, step=1, key="rp_peak")
coffee_price = st.sidebar.number_input("咖啡客单", value=35, step=1, key="cp")
retail_prices = {"工作日": retail_price_weekday, "周末": retail_price_weekend, "峰值日": retail_price_peak}

# --- 佣金比例 ---
st.sidebar.subheader("佣金比例")
retail_commission = st.sidebar.slider("零售佣金比例 (A+B+C)", 0.10, 0.50, 0.35, 0.01, key="comm_retail")
coffee_commission = st.sidebar.slider("咖啡佣金比例 (F)", 0.10, 0.30, 0.20, 0.01, key="comm_coffee")
workshop_commission = st.sidebar.slider("Workshop分成比例 (D)", 0.10, 0.50, 0.35, 0.01, key="comm_workshop")

# --- Workshop ---
st.sidebar.subheader("Workshop")
workshop_ticket_price = st.sidebar.number_input("门票价格", value=55, step=1, key="ws_price")
workshop_tickets_per_session = st.sidebar.number_input("每场销售票数", value=65, step=1, key="ws_tickets")
workshop_attendance_rate = st.sidebar.slider("Workshop上座率", 0.50, 1.00, 0.75, 0.05, key="ws_attendance")
workshop_actual_tickets = workshop_tickets_per_session * workshop_attendance_rate
workshop_sessions = {
    "冬季": st.sidebar.slider("Workshop场次-冬", 0.0, 5.0, 1.0, 0.5, key="ws_winter"),
    "春季": st.sidebar.slider("Workshop场次-春", 0.0, 5.0, 1.5, 0.5, key="ws_spring"),
    "夏季": st.sidebar.slider("Workshop场次-夏", 0.0, 5.0, 2.0, 0.5, key="ws_summer"),
    "秋季": st.sidebar.slider("Workshop场次-秋", 0.0, 5.0, 1.5, 0.5, key="ws_autumn"),
}
workshop_per_session = workshop_ticket_price * workshop_actual_tickets * workshop_commission

# --- C快闪岛 ---
st.sidebar.subheader("C快闪岛")
island_daily_sales = st.sidebar.number_input("展位日销售额", value=1250, step=10, key="island_sales")
island_count = st.sidebar.number_input("展位数", value=4, step=1, key="island_count")
island_bonus_people = st.sidebar.number_input("快闪岛加成人数/天", value=30, step=1, key="island_bonus")
island_commission_rate = st.sidebar.slider("快闪岛佣金比例", 0.10, 0.50, 0.35, 0.01, key="comm_island")
island_daily_commission = island_daily_sales * island_count * island_commission_rate

# --- 活动引流 ---
st.sidebar.subheader("活动引流")
event_influx = {
    "工作日": st.sidebar.number_input("活动日-工作日引流", value=50, step=5, key="ei_weekday"),
    "周末": st.sidebar.number_input("活动日-周末引流", value=100, step=5, key="ei_weekend"),
    "峰值日": st.sidebar.number_input("活动日-峰值引流", value=200, step=5, key="ei_peak"),
}
daily_influx = {
    "工作日": st.sidebar.number_input("日常-工作日引流", value=20, step=5, key="di_weekday"),
    "周末": st.sidebar.number_input("日常-周末引流", value=40, step=5, key="di_weekend"),
    "峰值日": st.sidebar.number_input("日常-峰值引流", value=70, step=5, key="di_peak"),
}

# --- 成本参数 ---
st.sidebar.subheader("固定成本")
daily_rent = st.sidebar.number_input("日租金 (¥)", value=333, step=10, key="rent")
electricity_rate = st.sidebar.number_input("电费单价 (¥/㎡/天)", value=0.2, step=0.01, key="elec_rate")
area = st.sidebar.number_input("商业面积 (㎡)", value=840, step=10, key="area")
daily_electricity = electricity_rate * area
daily_insurance = st.sidebar.number_input("商业保险 (¥/天)", value=92, step=10, key="insurance")

st.sidebar.subheader("人工成本")
staff_weekday = st.sidebar.number_input("工作日人数", value=2, step=1, key="staff_weekday")
staff_weekend = st.sidebar.number_input("周末人数", value=3, step=1, key="staff_weekend")
staff_salary = st.sidebar.number_input("人均月工资 (¥)", value=10000, step=500, key="salary")
staff_count = {"工作日": staff_weekday, "周末": staff_weekend, "峰值日": staff_weekend}

st.sidebar.subheader("营销成本")
monthly_marketing = st.sidebar.number_input("月营销基础 (¥)", value=5500, step=100, key="mkt_base")
event_extra_cost = st.sidebar.number_input("活动日额外成本 (¥)", value=5000, step=100, key="mkt_event")

st.sidebar.subheader("运营附加成本")
payment_fee_rate = st.sidebar.slider("收款手续费率 (%)", 0.0, 2.0, 1.2, 0.1, key="payment_fee") / 100
monthly_ops_cost = st.sidebar.number_input("运维耗材 (¥/月)", value=4500, step=100, key="ops_cost")

# --- 郎园分成 ---
st.sidebar.subheader("郎园分成")
langyuan_share_rate = st.sidebar.slider("郎园分成比例", 0.05, 0.20, 0.10, 0.01, key="ly_share")
langyuan_guarantee = st.sidebar.number_input("郎园保底额 (¥/月)", value=10000, step=1000, key="ly_guarantee")
langyuan_extra_per_customer = st.sidebar.number_input("郎园额外收益客单价 (¥)", value=190, step=10, key="ly_extra_customer")
langyuan_extra_rate = st.sidebar.slider("郎园引流抽成比例 (%)", 1.0, 20.0, 10.0, 0.5, key="ly_extra_rate") / 100

# --- 一次性支出 ---
st.sidebar.subheader("一次性支出")
opening_cost = st.sidebar.number_input("开业宣传 (¥)", value=30000, step=1000, key="open_cost")
hard_fitout_unit = st.sidebar.number_input("硬装单价 (¥/㎡)", value=2274, step=100, key="hard_fit")
soft_fitout_unit = st.sidebar.number_input("软装单价 (¥/㎡)", value=1236.66, step=0.01, key="soft_fit")
langyuan_coverage = st.sidebar.number_input("郎园装修覆盖 (¥)", value=1500000, step=10000, key="ly_cover")

# 郎园覆盖金额抵减LookTook投入（郎园覆盖减少LookTook实际出资）
total_investment = opening_cost + (hard_fitout_unit + soft_fitout_unit) * area - langyuan_coverage
hard_fitout_total = hard_fitout_unit * area
soft_fitout_total = soft_fitout_unit * area

# ==================== 主标题 ====================
st.title("📊 LookTook 营收成本测算看板")

# ==================== 时间维度选择 ====================
view_tabs = st.tabs([
    "📊 年度数据", "🍂 季度数据", "📆 月度数据",
    "📅 日均数据", "🔍 全场景分析", "💸 一次性支出"
])

# ==================== 计算函数 ====================

def get_base_traffic(date_type):
    if date_type == "工作日":
        return base_traffic_weekday
    elif date_type == "周末":
        return base_traffic_weekend
    else:
        return base_traffic_peak

def calculate_daily(date_type, season, is_event):
    base = get_base_traffic(date_type)
    traffic = base * season_weights[season]
    entry = traffic * entry_rates[date_type]
    c_bonus = island_bonus_people if date_type == "周末" else 0
    influx = event_influx[date_type] if is_event else daily_influx[date_type]
    total_entry = entry + c_bonus + influx

    retail_conv = total_entry * retail_conv_rates[date_type]
    retail_sales = retail_conv * retail_prices[date_type]
    retail_comm = retail_sales * retail_commission

    coffee_conv_count = total_entry * coffee_conv
    coffee_sales = coffee_conv_count * coffee_price
    coffee_comm = coffee_sales * coffee_commission

    island_comm = island_daily_commission if date_type == "周末" else 0
    workshop_daily = workshop_per_session * workshop_sessions[season] / 30

    gross_profit = retail_comm + coffee_comm + island_comm + workshop_daily
    langyuan_share = 0
    langyuan_share_estimate = gross_profit * langyuan_share_rate

    total_sales_for_fee = retail_sales + coffee_sales + island_comm
    payment_fee = total_sales_for_fee * payment_fee_rate

    daily_mkt = monthly_marketing / 30
    daily_ops = monthly_ops_cost / 30
    daily_labor = staff_count[date_type] * staff_salary / 30
    extra_event = event_extra_cost if is_event else 0
    total_cost = daily_rent + daily_electricity + daily_insurance + daily_labor + daily_mkt + daily_ops + payment_fee + extra_event

    net_profit = gross_profit - total_cost - langyuan_share

    return {
        "郎园日客流": traffic,
        "自然进店": entry,
        "快闪岛加成": c_bonus,
        "活动引流": influx,
        "总进店人数": total_entry,
        "零售成交人数": retail_conv,
        "零售销售额": retail_sales,
        "零售佣金": retail_comm,
        "咖啡成交人数": coffee_conv_count,
        "咖啡销售额": coffee_sales,
        "咖啡佣金": coffee_comm,
        "快闪岛佣金": island_comm,
        "Workshop日均": workshop_daily,
        "日毛利": gross_profit,
        "郎园分成": langyuan_share,
        "郎园分成估算": langyuan_share_estimate,
        "日租金": daily_rent,
        "日电费": daily_electricity,
        "日保险": daily_insurance,
        "日人工": daily_labor,
        "日营销基础": daily_mkt,
        "日运维耗材": daily_ops,
        "日收款手续费": payment_fee,
        "活动日额外": extra_event,
        "日总成本": total_cost,
        "日净利润": net_profit,
    }

def calculate_monthly(season, has_event_weekday=False, has_event_weekend=False):
    weekday_days = 22
    weekend_days = 8
    peak_weekend_days = 2

    m_weekday = calculate_daily("工作日", season, has_event_weekday)
    m_weekend = calculate_daily("周末", season, has_event_weekend)
    m_peak = calculate_daily("峰值日", season, True)

    result = {
        "天数": weekday_days + weekend_days + peak_weekend_days,
        "工作日天数": weekday_days,
        "周末天数": weekend_days,
        "峰值天数": peak_weekend_days,
    }

    for key in ["总进店人数", "零售佣金", "咖啡佣金", "快闪岛佣金", "Workshop日均",
                "日毛利", "日总成本", "日净利润"]:
        result[f"月{key.replace('日', '')}"] = (
            m_weekday[key] * weekday_days +
            m_weekend[key] * weekend_days +
            m_peak[key] * peak_weekend_days
        )

    monthly_gross = m_weekday["日毛利"] * weekday_days + m_weekend["日毛利"] * weekend_days + m_peak["日毛利"] * peak_weekend_days
    monthly_commission = monthly_gross * langyuan_share_rate
    result["月郎园分成或保底"] = max(monthly_commission, langyuan_guarantee)

    result["月活动额外成本"] = event_extra_cost * peak_weekend_days
    result["月净利润"] -= result["月活动额外成本"]

    extra_rev_wd = (event_influx["工作日"] if has_event_weekday else daily_influx["工作日"]) * langyuan_extra_per_customer * langyuan_extra_rate
    extra_rev_we = (event_influx["周末"] if has_event_weekend else daily_influx["周末"]) * langyuan_extra_per_customer * langyuan_extra_rate
    extra_rev_peak = event_influx["峰值日"] * langyuan_extra_per_customer * langyuan_extra_rate
    result["月郎园额外收益"] = extra_rev_wd * weekday_days + extra_rev_we * weekend_days + extra_rev_peak * peak_weekend_days

    return result, m_weekday, m_weekend, m_peak

season_config = {
    "冬季": {"wd": 66, "we": 24, "peak": 0, "event_peak": 0},
    "春季": {"wd": 65, "we": 25, "peak": 5, "event_peak": 3},
    "夏季": {"wd": 57, "we": 28, "peak": 5, "event_peak": 5},
    "秋季": {"wd": 65, "we": 25, "peak": 0, "event_peak": 0},
}

def compute_quarterly_data():
    month_days = 30
    qdata = {}
    for season, cfg in season_config.items():
        monthly_result, _, _, _ = calculate_monthly(season, False, False)
        season_gross = monthly_result["月毛利"] * (cfg["wd"] + cfg["we"] + cfg["peak"]) / month_days
        season_cost = monthly_result["月总成本"] * (cfg["wd"] + cfg["we"] + cfg["peak"]) / month_days
        season_cost += event_extra_cost * cfg["event_peak"]
        season_share = monthly_result["月郎园分成或保底"] * (cfg["wd"] + cfg["we"] + cfg["peak"]) / month_days
        qdata[season] = {
            "天数": cfg["wd"] + cfg["we"] + cfg["peak"],
            "季度毛利": season_gross,
            "季度成本": season_cost,
            "季度分成或保底": season_share,
            "季度净利润": season_gross - season_cost - season_share,
        }
    return qdata

quarterly_data = compute_quarterly_data()
year_days = sum(d["天数"] for d in quarterly_data.values())
year_gross = sum(d["季度毛利"] for d in quarterly_data.values())
year_cost = sum(d["季度成本"] for d in quarterly_data.values())
year_share = sum(d["季度分成或保底"] for d in quarterly_data.values())
year_net = sum(d["季度净利润"] for d in quarterly_data.values())

# ==================== 年度数据 Tab ====================
with view_tabs[0]:
    st.subheader("年度数据汇总")

    langyuan_year_share = year_share
    year_langyuan_extra = 0
    for season, cfg in season_config.items():
        monthly_result, _, _, _ = calculate_monthly(season, False, False)
        ly_extra = monthly_result.get("月郎园额外收益", 0)
        year_langyuan_extra += ly_extra * (cfg["wd"] + cfg["we"] + cfg["peak"]) / 30
    langyuan_year_total = langyuan_year_share + year_langyuan_extra

    looktook_payback = total_investment / (year_net / 12) if year_net > 0 else float('inf')
    langyuan_investment = langyuan_coverage
    langyuan_annual_income = langyuan_year_total
    langyuan_payback = langyuan_investment / (langyuan_annual_income / 12) if langyuan_annual_income > 0 else float('inf')

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### LookTook年度收益")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("年毛利", f"¥{year_gross:,.0f}")
        col2.metric("年总成本", f"¥{year_cost:,.0f}")
        col3.metric("年净利润", f"¥{year_net:,.0f}", delta=f"¥{year_net:,.0f}")
        col4.metric("回本周期", f"{looktook_payback:.1f}个月" if year_net > 0 else "亏损中")

        st.divider()
        st.markdown("**📈 LookTook回本周期分析**")
        col_inv1, col_inv2, col_inv3 = st.columns(3)
        col_inv1.metric("LookTook总投资", f"¥{total_investment:,.0f}")
        col_inv2.metric("月均净利润", f"¥{year_net/12:,.0f}")
        col_inv3.metric("回本周期", f"{looktook_payback:.1f}个月" if year_net > 0 else "亏损中")

    with col_right:
        st.markdown("### 郎园年度收益")
        col_ly1, col_ly2, col_ly3 = st.columns(3)
        col_ly1.metric("年分成/保底", f"¥{langyuan_year_share:,.0f}")
        col_ly2.metric("年额外收益", f"¥{year_langyuan_extra:,.0f}")
        col_ly3.metric("郎园年总收入", f"¥{langyuan_year_total:,.0f}")

        st.divider()
        st.markdown("**📈 郎园回本周期分析**")
        col_ly_inv1, col_ly_inv2, col_ly_inv3 = st.columns(3)
        col_ly_inv1.metric("郎园总投资", f"¥{langyuan_investment:,.0f}")
        col_ly_inv2.metric("郎园月均收入", f"¥{langyuan_annual_income/12:,.0f}")
        col_ly_inv3.metric("郎园回本周期", f"{langyuan_payback:.1f}个月" if langyuan_annual_income > 0 else "无收入")

    st.divider()

    year_summary = pd.DataFrame({
        "项目": ["LookTook年毛利", "LookTook年总成本", "LookTook年净利润", "LookTook回本周期",
                "郎园年分成/保底", "郎园年额外收益", "郎园年总收入", "郎园回本周期"],
        "金额": [f"¥{year_gross:,.0f}", f"¥{year_cost:,.0f}", f"¥{year_net:,.0f}", f"{looktook_payback:.1f}个月" if year_net > 0 else "亏损",
                f"¥{langyuan_year_share:,.0f}", f"¥{year_langyuan_extra:,.0f}",
                f"¥{langyuan_year_total:,.0f}", f"{langyuan_payback:.1f}个月" if langyuan_annual_income > 0 else "无收入"]
    })
    st.dataframe(year_summary, hide_index=True, use_container_width=True)

    st.divider()

    cumulative = [0]
    for d in quarterly_data.values():
        cumulative.append(cumulative[-1] + d["季度净利润"])

    fig_cumulative = go.Figure()
    fig_cumulative.add_trace(go.Scatter(
        x=["Q0", "冬", "春", "夏", "秋"],
        y=cumulative,
        mode="lines+markers",
        fill="tozeroy",
        name="累计利润"
    ))
    fig_cumulative.update_layout(title="累计利润趋势", template="plotly_white")
    st.plotly_chart(fig_cumulative, use_container_width=True)

# ==================== 季度数据 Tab ====================
with view_tabs[1]:
    st.subheader("季度数据")


    month_days = 30
    quarter_langyuan_extra = {}
    for season, cfg in season_config.items():
        monthly_result, _, _, _ = calculate_monthly(season, False, False)
        ly_extra = monthly_result.get("月郎园额外收益", 0)
        quarter_langyuan_extra[season] = ly_extra * (cfg["wd"] + cfg["we"] + cfg["peak"]) / month_days

    col1, col2, col3, col4 = st.columns(4)
    for i, (season, data) in enumerate(quarterly_data.items()):
        with [col1, col2, col3, col4][i]:
            st.metric(f"{season}", f"¥{data['季度净利润']:,.0f}", f"毛利¥{data['季度毛利']:,.0f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### LookTook季度收益")
        fig_quarter = px.bar(
            x=list(quarterly_data.keys()),
            y=[d["季度净利润"] for d in quarterly_data.values()],
            color=[d["季度净利润"] for d in quarterly_data.values()],
            color_continuous_scale="RdYlGn",
            labels={"x": "季节", "y": "季度净利润 (¥)"},
            title="各季度净利润对比"
        )
        fig_quarter.update_layout(template="plotly_white")
        st.plotly_chart(fig_quarter, use_container_width=True)

        st.divider()
        quarter_df = pd.DataFrame([
            {"季节": s, "天数": d["天数"], "季度毛利": f"¥{d['季度毛利']:,.0f}",
             "季度成本": f"¥{d['季度成本']:,.0f}", "郎园分成或保底": f"¥{d['季度分成或保底']:,.0f}",
             "季度净利润": f"¥{d['季度净利润']:,.0f}"}
            for s, d in quarterly_data.items()
        ])
        st.dataframe(quarter_df, hide_index=True, use_container_width=True)

    with col_right:
        st.markdown("### 郎园季度收益")
        for season, cfg in season_config.items():
            days = cfg["wd"] + cfg["we"] + cfg["peak"]
            ly_share = quarterly_data[season]["季度分成或保底"]
            ly_extra = quarter_langyuan_extra[season]
            ly_total = ly_share + ly_extra

            st.markdown(f"**{season}**")
            cols = st.columns(3)
            cols[0].metric("分成/保底", f"¥{ly_share:,.0f}")
            cols[1].metric("额外收益", f"¥{ly_extra:,.0f}")
            cols[2].metric("总收入", f"¥{ly_total:,.0f}")
            st.divider()

# ==================== 月度数据 Tab ====================
with view_tabs[2]:
    st.subheader("月度数据（按所选季节）")

    month_season = st.selectbox("选择季节", list(season_weights.keys()), key="month_season")
    has_event_wd = st.checkbox("工作日有活动", key="month_event_weekday")
    has_event_we = st.checkbox("周末有活动（含峰值日）", key="month_event_weekend")

    month_data, wd, we, peak = calculate_monthly(month_season, has_event_wd, has_event_we)

    ly_share = month_data["月郎园分成或保底"]
    ly_extra = month_data.get("月郎园额外收益", 0)
    ly_total = ly_share + ly_extra

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### LookTook月度收益")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("天数", f"{month_data['天数']}天")
        col2.metric("月毛利", f"¥{month_data['月毛利']:,.0f}")
        col3.metric("月总成本", f"¥{month_data['月总成本']:,.0f}")
        col4.metric("月净利润", f"¥{month_data['月净利润']:,.0f}", delta=f"¥{month_data['月净利润']:,.0f}")

        st.divider()

        month_summary = pd.DataFrame({
            "日期类型": ["工作日", "周末", "峰值日", "合计"],
            "天数": [month_data["工作日天数"], month_data["周末天数"], month_data["峰值天数"], month_data["天数"]],
            "月毛利": [f"¥{wd['日毛利']*month_data['工作日天数']:,.0f}",
                       f"¥{we['日毛利']*month_data['周末天数']:,.0f}",
                       f"¥{peak['日毛利']*month_data['峰值天数']:,.0f}",
                       f"¥{month_data['月毛利']:,.0f}"],
            "月成本": [f"¥{wd['日总成本']*month_data['工作日天数']:,.0f}",
                       f"¥{we['日总成本']*month_data['周末天数']:,.0f}",
                       f"¥{peak['日总成本']*month_data['峰值天数']:,.0f}",
                       f"¥{month_data['月总成本']:,.0f}"],
            "月利润": [f"¥{wd['日净利润']*month_data['工作日天数']:,.0f}",
                       f"¥{we['日净利润']*month_data['周末天数']:,.0f}",
                       f"¥{peak['日净利润']*month_data['峰值天数']:,.0f}",
                       f"¥{month_data['月净利润']:,.0f}"],
        })
        st.dataframe(month_summary, hide_index=True, use_container_width=True)

        with st.expander("查看详细计算明细", expanded=False):
            income_df = pd.DataFrame({
                "日期类型": ["工作日", "周末", "峰值日"],
                "日均毛利": [f"¥{wd['日毛利']:,.0f}", f"¥{we['日毛利']:,.0f}", f"¥{peak['日毛利']:,.0f}"],
                "日均成本": [f"¥{wd['日总成本']:,.0f}", f"¥{we['日总成本']:,.0f}", f"¥{peak['日总成本']:,.0f}"],
                "日均利润": [f"¥{wd['日净利润']:,.0f}", f"¥{we['日净利润']:,.0f}", f"¥{peak['日净利润']:,.0f}"],
                "月毛利": [f"¥{wd['日毛利']*month_data['工作日天数']:,.0f}",
                           f"¥{we['日毛利']*month_data['周末天数']:,.0f}",
                           f"¥{peak['日毛利']*month_data['峰值天数']:,.0f}"],
                "月成本": [f"¥{wd['日总成本']*month_data['工作日天数']:,.0f}",
                           f"¥{we['日总成本']*month_data['周末天数']:,.0f}",
                           f"¥{peak['日总成本']*month_data['峰值天数']:,.0f}"],
                "月利润": [f"¥{wd['日净利润']*month_data['工作日天数']:,.0f}",
                           f"¥{we['日净利润']*month_data['周末天数']:,.0f}",
                           f"¥{peak['日净利润']*month_data['峰值天数']:,.0f}"],
            })
            st.dataframe(income_df, hide_index=True, use_container_width=True)

            st.markdown("**收入构成**")
            revenue_monthly = pd.DataFrame({
                "收入项": ["零售佣金", "咖啡佣金", "快闪岛佣金", "Workshop"],
                "月金额": [
                    wd['零售佣金']*month_data['工作日天数'] + we['零售佣金']*month_data['周末天数'] + peak['零售佣金']*month_data['峰值天数'],
                    wd['咖啡佣金']*month_data['工作日天数'] + we['咖啡佣金']*month_data['周末天数'] + peak['咖啡佣金']*month_data['峰值天数'],
                    wd['快闪岛佣金']*month_data['工作日天数'] + we['快闪岛佣金']*month_data['周末天数'] + peak['快闪岛佣金']*month_data['峰值天数'],
                    wd['Workshop日均']*month_data['工作日天数'] + we['Workshop日均']*month_data['周末天数'] + peak['Workshop日均']*month_data['峰值天数'],
                ]
            })
            st.dataframe(revenue_monthly, hide_index=True, use_container_width=True)

            st.markdown("**成本构成明细**")
            wd_days = month_data["工作日天数"]
            we_days = month_data["周末天数"]
            peak_days = month_data["峰值天数"]
            daily_ops = monthly_ops_cost / 30
            cost_items = {
                "日租金": daily_rent,
                "日电费": daily_electricity,
                "日保险": daily_insurance,
                "日人工（工作日）": wd["日人工"],
                "日人工（周末/峰值）": (we["日人工"] + peak["日人工"]) / 2,
                "日营销基础": wd["日营销基础"],
                "日运维耗材": daily_ops,
                "日收款手续费": (wd["日收款手续费"] * wd_days + we["日收款手续费"] * we_days + peak["日收款手续费"] * peak_days) / month_data["天数"],
                "活动日额外": peak["活动日额外"],
            }
            cost_monthly_items = pd.DataFrame({
                "成本项": list(cost_items.keys()),
                "日均": [f"¥{v:,.2f}" for v in cost_items.values()],
                "月合计": [f"¥{v * (wd_days if "工作日" in k or k == "日租金" or k == "日电费" or k == "日保险" else (we_days if "周末" in k else peak_days)):,.0f}" if k != "日收款手续费" else f"¥{(wd["日收款手续费"]*wd_days + we["日收款手续费"]*we_days + peak["日收款手续费"]*peak_days):,.0f}" for k, v in cost_items.items()],
            })
            st.dataframe(cost_monthly_items, hide_index=True, use_container_width=True)

    with col_right:
        st.markdown("### 郎园月度收益")
        col_ly1, col_ly2, col_ly3 = st.columns(3)
        col_ly1.metric("月分成/保底", f"¥{ly_share:,.0f}")
        col_ly2.metric("月额外收益", f"¥{ly_extra:,.0f}")
        col_ly3.metric("郎园月总收入", f"¥{ly_total:,.0f}")


        st.divider()
        st.markdown("**说明文案**")
        st.caption("💡 郎园分成或保底 = max(月毛利×10%, 保底额¥10,000)，按月结算")
        st.caption("💡 郎园额外收益 = Σ(日活动引流人数 × ¥190 × 10%)，指LookTook活动引流用户在郎园园区其他店消费的流水抽成")

# ==================== 日均数据 Tab ====================
with view_tabs[3]:
    st.subheader("单日数据")

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        day_season = st.selectbox("选择季节", list(season_weights.keys()), key="day_season")
    with col_sel2:
        day_type = st.selectbox("选择日期类型", ["工作日", "周末", "峰值日"], key="day_type")

    is_event_day = st.checkbox("活动日", key="day_is_event")
    m = calculate_daily(day_type, day_season, is_event_day)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总进店人数", f"{m['总进店人数']:.0f}人")
    col2.metric("日毛利", f"¥{m['日毛利']:,.0f}")
    col3.metric("日总成本", f"¥{m['日总成本']:,.0f}")
    col4.metric("日净利润", f"¥{m['日净利润']:,.0f}", delta=f"¥{m['日净利润']:,.0f}")

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**💰 收入构成**")
        revenue_data = pd.DataFrame({
            "收入项": ["零售佣金", "咖啡佣金", "快闪岛佣金", "Workshop"],
            "金额": [m["零售佣金"], m["咖啡佣金"], m["快闪岛佣金"], m["Workshop日均"]]
        })
        fig_pie = px.pie(revenue_data, values="金额", names="收入项", hole=0.4)
        fig_pie.update_layout(template="plotly_white", margin=dict(t=30, b=30))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("**📉 成本构成**")
        cost_df = pd.DataFrame({
            "成本项": ["租金", "电费", "保险", "人工", "营销基础", "运维耗材", "收款手续费", "活动日额外"],
            "金额": [m["日租金"], m["日电费"], m["日保险"], m["日人工"], m["日营销基础"], m["日运维耗材"], m["日收款手续费"], m["活动日额外"]]
        })
        fig_cost = px.bar(cost_df, x="成本项", y="金额", color="金额", color_continuous_scale="OrRd")
        fig_cost.update_layout(template="plotly_white", margin=dict(t=30, b=30))
        st.plotly_chart(fig_cost, use_container_width=True)

    st.divider()

    with st.expander("查看详细计算明细", expanded=False):
        income_df = pd.DataFrame({
            "指标": ["郎园日客流", "自然进店人数", "快闪岛加成", "活动引流", "总进店人数",
                    "零售成交人数", "零售销售额", "零售佣金", "咖啡成交人数", "咖啡销售额", "咖啡佣金",
                    "快闪岛佣金", "Workshop日均", "日毛利合计"],
            "数值": [f"{m[k]:,.1f}" for k in ["郎园日客流", "自然进店", "快闪岛加成", "活动引流",
                                              "总进店人数", "零售成交人数", "零售销售额", "零售佣金",
                                              "咖啡成交人数", "咖啡销售额", "咖啡佣金", "快闪岛佣金",
                                              "Workshop日均", "日毛利"]]
        })
        cost_df_full = pd.DataFrame({
            "指标": ["日租金", "日电费", "日保险", "日人工", "日营销基础", "日运维耗材", "日收款手续费", "活动日额外", "日总成本", "日净利润"],
            "数值": [f"¥{m[k]:,.2f}" for k in ["日租金", "日电费", "日保险", "日人工",
                                                "日营销基础", "日运维耗材", "日收款手续费", "活动日额外", "日总成本", "日净利润"]]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(income_df, hide_index=True, use_container_width=True)
        with col2:
            st.dataframe(cost_df_full, hide_index=True, use_container_width=True)


# ==================== 全场景敏感性分析 Tab ====================
with view_tabs[4]:
    st.subheader("12种场景敏感性分析")

    all_scenarios = []
    for season in season_weights.keys():
        for dtype in ["工作日", "周末", "峰值日"]:
            for is_event in [False, True]:
                label = f"{season}-{dtype}-{'活动日' if is_event else '日常'}"
                d = calculate_daily(dtype, season, is_event)
                all_scenarios.append({
                    "场景": label,
                    "季节": season,
                    "类型": dtype,
                    "活动": "活动日" if is_event else "日常",
                    "日客流": d["郎园日客流"],
                    "进店人数": d["总进店人数"],
                    "日毛利": d["日毛利"],
                    "日成本": d["日总成本"],
                    "郎园分成": d["郎园分成"],
                    "日净利润": d["日净利润"],
                })

    scenario_df = pd.DataFrame(all_scenarios)
    scenario_df = scenario_df.sort_values("日净利润", ascending=False)

    def color_profit(val):
        if val > 0:
            return "background-color: #90EE90"
        return "background-color: #FFB6C1"

    st.dataframe(
        scenario_df.style.map(color_profit, subset=["日净利润"]),
        hide_index=True, use_container_width=True, height=500
    )

    st.divider()
    st.markdown("**🔥 净利润热力图**")


    pivot_data = scenario_df.pivot_table(
        values="日净利润", index="季节", columns=["类型", "活动"], aggfunc="sum"
    )

    fig_heatmap = px.imshow(
        pivot_data.values,
        x=[f"{c[0]}-{c[1]}" for c in pivot_data.columns],
        y=pivot_data.index,
        color_continuous_scale="RdYlGn",
        labels=dict(x="日期类型-活动", y="季节", color="日净利润"),
        text_auto=True
    )
    fig_heatmap.update_layout(template="plotly_white")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.caption("绿色表示盈利，红色表示亏损（单位：元）")

# ==================== 一次性支出 Tab ====================
with view_tabs[5]:
    st.subheader("一次性支出明细")

    col1, col2, col3 = st.columns(3)
    col1.metric("硬装总额", f"¥{hard_fitout_total:,.0f}", f"¥{hard_fitout_unit:,.0f}/㎡")
    col2.metric("软装总额", f"¥{soft_fitout_total:,.0f}", f"¥{soft_fitout_unit:,.0f}/㎡")
    col3.metric("开业宣传", f"¥{opening_cost:,.0f}", "一次性")

    st.divider()

    langyuan_year_share = year_share
    year_langyuan_extra = 0
    for season, cfg in season_config.items():
        monthly_result, _, _, _ = calculate_monthly(season, False, False)
        ly_extra = monthly_result.get("月郎园额外收益", 0)
        year_langyuan_extra += ly_extra * (cfg["wd"] + cfg["we"] + cfg["peak"]) / 30
    langyuan_year_total = langyuan_year_share + year_langyuan_extra

    langyuan_investment = langyuan_coverage
    langyuan_annual_income = langyuan_year_total
    langyuan_payback = langyuan_investment / (langyuan_annual_income / 12) if langyuan_annual_income > 0 else float('inf')
    looktook_payback = total_investment / (year_net / 12) if year_net > 0 else float('inf')

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### LookTook投入")
        st.metric("LookTook总投入", f"¥{total_investment:,.0f}")
        if year_net > 0:
            st.metric("LookTook回本周期", f"{looktook_payback:.1f}个月")
        else:
            st.metric("LookTook回本周期", "亏损中")
        st.caption(f"= 硬装¥{hard_fitout_total:,.0f} + 软装¥{soft_fitout_total:,.0f} + 开业¥{opening_cost:,.0f} - 郎园覆盖¥{langyuan_coverage:,.0f}")
        st.caption(f"月均净利润¥{year_net/12:,.0f}（扣除郎园分成或保底后）")

        st.divider()
        st.markdown("**📊 LookTook支出构成**")
        investment_data = pd.DataFrame({
            "支出项": ["硬装", "软装", "开业宣传"],
            "金额": [hard_fitout_total, soft_fitout_total, opening_cost],
        })
        investment_data["占比"] = (investment_data["金额"] / total_investment * 100)
        investment_data["标签"] = investment_data.apply(
            lambda r: f"¥{r['金额']:,.0f} ({r['占比']:.1f}%)", axis=1
        )
        fig_inv = px.pie(
            investment_data,
            values="金额", names="支出项",
            title="LookTook一次性支出构成"
        )
        fig_inv.update_layout(template="plotly_white")
        st.plotly_chart(fig_inv, use_container_width=True)

    with col_right:
        st.markdown("### 郎园投入")
        st.metric("郎园投入", f"¥{langyuan_coverage:,.0f}")
        st.caption("郎园装修覆盖金额（郎园承担）")
        if langyuan_annual_income > 0:
            st.metric("郎园回本周期", f"{langyuan_payback:.1f}个月")
        else:
            st.metric("郎园回本周期", "无收入")
        st.caption(f"月均收入¥{langyuan_annual_income/12:,.0f}")

    st.divider()

    invest_detail = pd.DataFrame({
        "项目": ["商业面积", "硬装单价", "硬装合计", "软装单价", "软装合计", "开业宣传", "郎园装修覆盖（郎园出资）", "LookTook总投入"],
        "数值/金额": [f"{area} ㎡", f"¥{hard_fitout_unit:,}/㎡", f"¥{hard_fitout_total:,}",
                     f"¥{soft_fitout_unit:,}/㎡", f"¥{soft_fitout_total:,}",
                     f"¥{opening_cost:,}", f"¥{langyuan_coverage:,}", f"¥{total_investment:,}"],
    })
    st.dataframe(invest_detail, hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("**💡 说明**")
    st.info("""
    - **硬装**：硬件搭建、装修、材料、通水电、简单内装（¥4,500/㎡参考价）
    - **软装**：可调节/可移动的设施配置（目前待确认）
    - **郎园装修覆盖**：郎园可能承担的装修费用，从LookTook总投入中抵扣
    - LookTook回本周期 = LookTook总投入 / 月均净利润（扣除郎园分成后）
    - 郎园回本周期 = 郎园投入 / 月均郎园收入
    """)
