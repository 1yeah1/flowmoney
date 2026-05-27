import streamlit as st
import json
import os
from datetime import datetime, date

# ========== 【固定放在最前面】页面配置 ==========
st.set_page_config(
    page_title="FlowMoney 个人记账",
    page_icon="💰",
    layout="wide"
)

# ===================== 初始化本地存储 =====================
DATA_FILE = "account_data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        init_dict = {
            "records": [],
            "month_budget": 3000,
            "dark_mode": False
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(init_dict, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

init_data()
data = load_data()

# 预设基础分类（仅固定分类，移除自定义分类相关逻辑）
base_category = ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "工资", "其他"]

st.title("💰 FlowMoney 年轻人极简记账")
st.caption("大学生个人财务管理作品集项目")

# 侧边导航（移除数据分析选项）
menu = st.sidebar.radio("功能导航", ["首页仪表盘", "添加记账", "系统设置"])

# ===================== 工具函数 =====================
def get_month_stat(records):
    now = datetime.now()
    current_month = f"{now.year}-{now.month:02d}"
    month_rec = [r for r in records if r["date"].startswith(current_month)]
    income = sum(r["amount"] for r in month_rec if r["type"]=="收入")
    expense = abs(sum(r["amount"] for r in month_rec if r["type"]=="支出"))
    return income, expense

def get_today_cost(records):
    today = str(date.today())
    today_rec = [r for r in records if r["date"]==today and r["type"]=="支出"]
    return abs(sum(r["amount"] for r in today_rec))

# ===================== 1. 首页仪表盘 =====================
if menu == "首页仪表盘":
    st.subheader("📊 本月财务概览")
    records = data["records"]
    budget = data["month_budget"]

    month_income, month_expense = get_month_stat(records)
    today_cost = get_today_cost(records)
    left_budget = budget - month_expense

    # 卡片数据展示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("本月总收入", f"¥{month_income:.2f}", delta_color="normal")
    with col2:
        st.metric("本月总支出", f"¥{month_expense:.2f}", delta_color="inverse")
    with col3:
        st.metric("今日花费", f"¥{today_cost:.2f}")
    with col4:
        st.metric("剩余预算", f"¥{left_budget:.2f}")

elif menu == "添加记账":
    st.subheader("✍️ 新增收支记录")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            bill_type = st.selectbox("收支类型", ["支出", "收入"])
            # 仅保留固定下拉分类，删除自定义输入框
            select_cate = st.selectbox("选择分类", base_category)
        with col2:
            amount = st.number_input("金额", min_value=0.01, step=0.01)
            bill_date = st.date_input("选择日期", date.today())
        submit_btn = st.form_submit_button("提交记账")

        if submit_btn:
            cost_amount = amount if bill_type=="收入" else -amount
            new_record = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "type": bill_type,
                "category": select_cate,
                "amount": cost_amount,
                "date": str(bill_date)
            }
            data["records"].insert(0, new_record)
            save_data(data)
            st.success(f"✅ 记账成功！当前分类：{select_cate}")

elif menu == "系统设置":
    st.subheader("⚙️ 系统设置")
    budget = st.number_input("设置每月预算", min_value=0, value=int(data["month_budget"]))
    if st.button("保存预算"):
        data["month_budget"] = budget
        save_data(data)
        st.success("预算修改成功")

    st.divider()
    if st.button("清空所有记账数据", type="primary"):
        data["records"] = []
        save_data(data)
        st.warning("所有数据已清空！")