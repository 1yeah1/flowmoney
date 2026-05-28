import streamlit as st
import json
import os
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="FlowMoney 个人记账",
    page_icon="💰",
    layout="wide"
)

DATA_FILE = "account_data.json"

def init_data():
    if not os.path.exists(DATA_FILE):
        init_dict = {
            "records": [],
            "month_budget": 3000,
            "dark_mode": False,
            "custom_categories": ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "工资", "其他"],
            "accounts": ["现金", "微信", "支付宝", "银行卡"]  # 初始化默认账户
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
category_list = data["custom_categories"]
account_list = data["accounts"]

st.title("💰 FlowMoney ")
st.caption("大学生个人财务管理")

menu = st.sidebar.radio(
    "功能导航",
    ["首页仪表盘", "添加记账", "最近5条记录", "日期范围查询", "数据分析", "数据导出", "系统设置"]
)

def filter_records_by_date_account(records, start_date, end_date, target_account=None):
    res = []
    for r in records:
        rec_date = date.fromisoformat(r["date"])
        if not (start_date <= rec_date <= end_date):
            continue
        if target_account and r.get("account", "") != target_account:
            continue
        res.append(r)
    return res

def group_by_month(records):
    month_dict = {}
    for r in records:
        month = r["date"][:7]
        if month not in month_dict:
            month_dict[month] = {"income": 0, "expense": 0}
        if r["type"] == "收入":
            month_dict[month]["income"] += r["amount"]
        else:
            month_dict[month]["expense"] += abs(r["amount"])
    return month_dict

def group_by_category(records, bill_type):
    cate_dict = {}
    for r in records:
        if r["type"] == bill_type:
            cate = r["category"]
            val = r["amount"] if bill_type == "收入" else abs(r["amount"])
            cate_dict[cate] = cate_dict.get(cate, 0) + val
    return cate_dict

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

if menu == "首页仪表盘":
    st.subheader("📊 本月财务概览")
    records = data["records"]
    budget = data["month_budget"]

    select_acc = st.selectbox("选择查看账户", ["全部账户"] + account_list)
    if select_acc != "全部账户":
        filter_records = [r for r in records if r.get("account", "") == select_acc]
    else:
        filter_records = records

    month_income, month_expense = get_month_stat(filter_records)
    today_cost = get_today_cost(filter_records)
    left_budget = budget - month_expense

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

    with st.expander("🔧 管理记账分类（可新增/删除）"):
        new_cate = st.text_input("输入新分类名称")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("添加分类") and new_cate.strip() and new_cate not in category_list:
                data["custom_categories"].append(new_cate.strip())
                save_data(data)
                st.success(f"分类【{new_cate}】添加成功")
                st.rerun()
        with col_b:
            del_cate = st.selectbox("选择要删除的分类", category_list)
            if st.button("删除分类") and len(category_list) > 1:
                data["custom_categories"].remove(del_cate)
                save_data(data)
                st.success(f"分类【{del_cate}】已删除")
                st.rerun()

    with st.expander("💳 管理记账账户（可新增/删除）"):
        new_acc = st.text_input("输入新账户名称")
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("添加账户") and new_acc.strip() and new_acc not in account_list:
                data["accounts"].append(new_acc.strip())
                save_data(data)
                st.success(f"账户【{new_acc}】添加成功")
                st.rerun()
        with col_d:
            del_acc = st.selectbox("选择要删除的账户", account_list)
            if st.button("删除账户") and len(account_list) > 1:
                data["accounts"].remove(del_acc)
                save_data(data)
                st.success(f"账户【{del_acc}】已删除")
                st.rerun()

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            bill_type = st.selectbox("收支类型", ["支出", "收入"])
            select_cate = st.selectbox("选择分类", data["custom_categories"])
            select_account = st.selectbox("选择记账账户", account_list)
        with col2:
            amount = st.number_input("金额", min_value=0.01, step=0.01)
            bill_date = st.date_input("选择日期", date.today())
        
        remark = st.text_input("备注信息（选填）")
        submit_btn = st.form_submit_button("提交记账")

        if submit_btn:
            cost_amount = amount if bill_type=="收入" else -amount
            new_record = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "type": bill_type,
                "category": select_cate,
                "account": select_account,  
                "amount": cost_amount,
                "date": str(bill_date),
                "remark": remark  
            }
            data["records"].insert(0, new_record)
            save_data(data)
            st.success(f"✅ 记账成功！账户：{select_account} 分类：{select_cate}")

elif menu == "最近5条记录":
    st.subheader("📜 最近5条记账记录")
    records = data["records"]
    select_acc = st.selectbox("筛选账户", ["全部账户"] + account_list)
    
    if select_acc != "全部账户":
        filter_records = [r for r in records if r.get("account", "") == select_acc]
    else:
        filter_records = records

    if not filter_records:
        st.info("暂无任何记账记录")
    else:
        show_records = filter_records[:5]
        for idx, rec in enumerate(show_records, 1):
            st.write(f"**第{idx}条**")
            st.write(f"日期：{rec['date']} | 账户：{rec['account']} | 类型：{rec['type']} | 分类：{rec['category']}")
            st.write(f"金额：¥{abs(rec['amount']):.2f} | 备注：{rec['remark']}")
            st.divider()

elif menu == "日期范围查询":
    st.subheader("📅 按日期范围查询记账流水")
    records = data["records"]
    select_acc = st.selectbox("筛选账户", ["全部账户"] + account_list)

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("开始日期", date.today())
    with col2:
        end = st.date_input("结束日期", date.today())
    
    if start > end:
        st.error("开始日期不能晚于结束日期")
    else:
        if select_acc != "全部账户":
            filter_rec = filter_records_by_date_account(records, start, end, select_acc)
        else:
            filter_rec = filter_records_by_date_account(records, start, end)

        if not filter_rec:
            st.info("该时间段内暂无记账记录")
        else:
            st.success(f"共查询到 {len(filter_rec)} 条记录")
            for idx, rec in enumerate(filter_rec, 1):
                st.write(f"**{idx}.** 日期：{rec['date']} | 账户：{rec['account']} | {rec['type']} | 分类：{rec['category']}")
                st.write(f"金额：¥{abs(rec['amount']):.2f} | 备注：{rec['remark']}")
                st.divider()

elif menu == "数据分析":
    st.subheader("📈 收支数据分析图表")
    records = data["records"]
    select_acc = st.selectbox("分析指定账户", ["全部账户"] + account_list)

    col1, col2 = st.columns(2)
    with col1:
        ana_start = st.date_input("分析起始日期", date.today())
    with col2:
        ana_end = st.date_input("分析结束日期", date.today())

    if ana_start > ana_end:
        st.error("起始日期不能大于结束日期")
    else:
        if select_acc != "全部账户":
            ana_records = filter_records_by_date_account(records, ana_start, ana_end, select_acc)
        else:
            ana_records = filter_records_by_date_account(records, ana_start, ana_end)

        if not ana_records:
            st.warning("所选时间段/账户暂无数据，无法生成图表")
        else:

            st.markdown("### 1. 收入分类占比饼图")
            income_cate = group_by_category(ana_records, "收入")
            if income_cate:
                fig_income = px.pie(
                    names=list(income_cate.keys()),
                    values=list(income_cate.values()),
                    title="收入分类分布"
                )
                st.plotly_chart(fig_income, use_container_width=True)
            else:
                st.info("该时间段无收入数据")

            st.markdown("### 2. 支出分类占比饼图")
            expense_cate = group_by_category(ana_records, "支出")
            if expense_cate:
                fig_expense = px.pie(
                    names=list(expense_cate.keys()),
                    values=list(expense_cate.values()),
                    title="支出分类分布"
                )
                st.plotly_chart(fig_expense, use_container_width=True)
            else:
                st.info("该时间段无支出数据")

            st.markdown("### 3. 月度收支对比柱状图")
            month_data = group_by_month(ana_records)
            if month_data:
                months = list(month_data.keys())
                income_list = [month_data[m]["income"] for m in months]
                expense_list = [month_data[m]["expense"] for m in months]

                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(x=months, y=income_list, name="收入"))
                fig_bar.add_trace(go.Bar(x=months, y=expense_list, name="支出"))
                fig_bar.update_layout(title="月度收入/支出对比", xaxis_title="月份", yaxis_title="金额(¥)")
                st.plotly_chart(fig_bar, use_container_width=True)

elif menu == "数据导出":
    st.subheader("📥 导出记账数据")
    records = data["records"]
    if not records:
        st.warning("暂无数据，无法导出")
    else:
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        file_name = f"FlowMoney_记账数据_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        st.download_button(
            label="点击下载 JSON 文件",
            data=json_str,
            file_name=file_name,
            mime="application/json"
        )
        st.success("文件已准备好，点击按钮即可下载")

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