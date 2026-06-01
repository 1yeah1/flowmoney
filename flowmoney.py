import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
from collections import defaultdict
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
            "deleted_records": [],
            "month_budget": 3000,
            "dark_mode": False,
            "expense_categories": ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "医疗", "其他"],
            "income_categories": ["工资", "兼职", "奖学金", "理财", "投资分红", "礼金", "其他"],
            "accounts": ["现金", "微信", "支付宝", "银行卡"]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(init_dict, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cleanup_deleted_records(data, max_days=30):
    if not data.get("deleted_records"):
        return
    from datetime import date as date_cls
    cutoff = str(date_cls.today() - timedelta(days=max_days))
    original_len = len(data["deleted_records"])
    data["deleted_records"] = [r for r in data["deleted_records"] if r.get("date", "") > cutoff]
    removed = original_len - len(data["deleted_records"])
    if removed > 0:
        save_data(data)

init_data()
data = load_data()

if "expense_categories" not in data:
    data["expense_categories"] = ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "医疗", "其他"]
if "income_categories" not in data:
    data["income_categories"] = ["工资", "兼职", "奖学金", "理财", "投资分红", "礼金", "其他"]
if "deleted_records" not in data:
    data["deleted_records"] = []
save_data(data)

cleanup_deleted_records(data)
expense_categories = data["expense_categories"]
income_categories = data["income_categories"]
account_list = data["accounts"]

st.title("💰 FlowMoney ")
st.caption("大学生个人财务管理")

menu = st.sidebar.radio(
    "功能导航",
    ["首页仪表盘", "记账流水", "添加记账", "数据分析", "回收站", "系统设置"]
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

    if left_budget < 0:
        st.error(f"⚠️ 本月已超支 ¥{abs(left_budget):.2f}！当前预算 ¥{budget:.2f}，已支出 ¥{month_expense:.2f}")
    elif left_budget < budget * 0.2:
        st.warning(f"⚡ 预算剩余不足 20%，仅剩 ¥{left_budget:.2f}，请注意控制支出")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("本月总收入", f"¥{month_income:.2f}", delta_color="normal")
    with col2:
        st.metric("本月总支出", f"¥{month_expense:.2f}", delta_color="inverse")
    with col3:
        st.metric("今日花费", f"¥{today_cost:.2f}")
    with col4:
        st.metric("剩余预算", f"¥{left_budget:.2f}", delta="inverse" if left_budget < 0 else "normal")

elif menu == "添加记账":
    st.subheader("✍️ 新增收支记录")

    with st.expander("🔧 管理记账分类（可新增/删除）"):
        tab_exp, tab_inc = st.tabs(["💸 支出分类", "💰 收入分类"])

        with tab_exp:
            col_a, col_b = st.columns(2)
            with col_a:
                new_exp_cate = st.text_input("新增支出分类", key="new_exp_cate")
                if st.button("添加", key="add_exp_cate") and new_exp_cate.strip() and new_exp_cate.strip() not in expense_categories:
                    data["expense_categories"].append(new_exp_cate.strip())
                    save_data(data)
                    st.success(f"支出分类【{new_exp_cate}】添加成功")
                    st.rerun()
            with col_b:
                del_exp_cate = st.selectbox("删除支出分类", expense_categories, key="del_exp_cate")
                if "confirm_del_exp" not in st.session_state:
                    st.session_state.confirm_del_exp = ""
                
                if st.button("删除", key="del_exp_cate_btn") and len(expense_categories) > 1:
                    st.session_state.confirm_del_exp = del_exp_cate
                
                if st.session_state.confirm_del_exp == del_exp_cate:
                    st.warning(f"⚠️ 确定要删除「{del_exp_cate}」分类吗？关联的历史记录将被更新为「其他」")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("确认删除", key=f"confirm_del_exp_{del_exp_cate}"):
                            for r in data["records"]:
                                if r["type"] == "支出" and r["category"] == del_exp_cate:
                                    r["category"] = "其他"
                            for r in data.get("deleted_records", []):
                                if r["type"] == "支出" and r["category"] == del_exp_cate:
                                    r["category"] = "其他"
                            data["expense_categories"].remove(del_exp_cate)
                            save_data(data)
                            st.success(f"✅ 支出分类【{del_exp_cate}】已删除，历史记录同步更新为「其他」")
                            st.session_state.confirm_del_exp = ""
                            st.rerun()
                    with col_y:
                        if st.button("取消", key=f"cancel_del_exp_{del_exp_cate}"):
                            st.session_state.confirm_del_exp = ""
                            st.rerun()

        with tab_inc:
            col_a, col_b = st.columns(2)
            with col_a:
                new_inc_cate = st.text_input("新增收入分类", key="new_inc_cate")
                if st.button("添加", key="add_inc_cate") and new_inc_cate.strip() and new_inc_cate.strip() not in income_categories:
                    data["income_categories"].append(new_inc_cate.strip())
                    save_data(data)
                    st.success(f"收入分类【{new_inc_cate}】添加成功")
                    st.rerun()
            with col_b:
                del_inc_cate = st.selectbox("删除收入分类", income_categories, key="del_inc_cate")
                if "confirm_del_inc" not in st.session_state:
                    st.session_state.confirm_del_inc = ""
                
                if st.button("删除", key="del_inc_cate_btn") and len(income_categories) > 1:
                    st.session_state.confirm_del_inc = del_inc_cate
                
                if st.session_state.confirm_del_inc == del_inc_cate:
                    st.warning(f"⚠️ 确定要删除「{del_inc_cate}」分类吗？关联的历史记录将被更新为「其他」")
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("确认删除", key=f"confirm_del_inc_{del_inc_cate}"):
                            for r in data["records"]:
                                if r["type"] == "收入" and r["category"] == del_inc_cate:
                                    r["category"] = "其他"
                            for r in data.get("deleted_records", []):
                                if r["type"] == "收入" and r["category"] == del_inc_cate:
                                    r["category"] = "其他"
                            data["income_categories"].remove(del_inc_cate)
                            save_data(data)
                            st.success(f"✅ 收入分类【{del_inc_cate}】已删除，历史记录同步更新为「其他」")
                            st.session_state.confirm_del_inc = ""
                            st.rerun()
                    with col_y:
                        if st.button("取消", key=f"cancel_del_inc_{del_inc_cate}"):
                            st.session_state.confirm_del_inc = ""
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

    st.markdown("---")
    st.subheader("📝 记账")
    col_type, col_acc = st.columns(2)
    with col_type:
        bill_type = st.selectbox("收支类型", ["支出", "收入"], key="bill_type")
    with col_acc:
        select_account = st.selectbox("记账账户", account_list, key="add_acc")

    current_categories = income_categories if bill_type == "收入" else expense_categories

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            select_cate = st.selectbox("选择分类", current_categories, key="add_cate")
        with col2:
            amount = st.number_input("金额", min_value=0.01, step=0.01, key="add_amount")
            bill_date = st.date_input("选择日期", date.today(), key="add_date")

        remark = st.text_input("备注信息（选填）", key="add_remark")
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

            # 预算超支提醒
            current_month = datetime.now().strftime("%Y-%m")
            month_records = [r for r in data["records"] if r["date"].startswith(current_month)]
            month_expense = abs(sum(r["amount"] for r in month_records if r["type"] == "支出"))
            if month_expense > data["month_budget"]:
                over = month_expense - data["month_budget"]
                st.error(f"⚠️ 本月已超支 ¥{over:.2f}！预算 ¥{data['month_budget']:.2f}，已支出 ¥{month_expense:.2f}")

elif menu == "记账流水":
    st.subheader("📜 记账流水")
    records = data["records"]

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        select_acc = st.selectbox("筛选账户", ["全部账户"] + account_list, key="流水_acc")
    with col_filter2:
        time_range = st.selectbox("时间范围", ["不限", "最近7天", "最近30天", "自定义日期"], key="流水_time")

    today = date.today()
    if time_range == "自定义日期":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start = st.date_input("开始日期", date(today.year, today.month, 1), key="流水_start")
        with col_d2:
            end = st.date_input("结束日期", today, key="流水_end")
    elif time_range == "最近7天":
        start, end = today - timedelta(days=6), today
    elif time_range == "最近30天":
        start, end = today - timedelta(days=29), today
    else:
        start, end = date(2000, 1, 1), today

    if start > end:
        st.error("开始日期不能晚于结束日期")
    else:
        filter_records = [r for r in records if r.get("account", "") == select_acc or select_acc == "全部账户"]
        filter_records = [r for r in filter_records if start <= date.fromisoformat(r["date"]) <= end]

        if not filter_records:
            st.info("暂无符合条件的记录")
        else:
            st.caption(f"共 {len(filter_records)} 条记录")

            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            file_name = f"FlowMoney_记账数据_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            st.download_button("📥 导出 JSON", data=json_str, file_name=file_name, mime="application/json")

            for idx, rec in enumerate(filter_records, 1):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.write(f"**{idx}.** 日期：{rec['date']} | 账户：{rec['account']} | {rec['type']} | 分类：{rec['category']}")
                    st.write(f"金额：¥{abs(rec['amount']):.2f} | 备注：{rec['remark']}")
                with col_b:
                    if st.button("🗑️", key=f"del_流水_{rec['id']}", help="删除"):
                        data["deleted_records"].insert(0, rec)
                        data["records"].remove(rec)
                        save_data(data)
                        st.rerun()
                st.divider()

elif menu == "数据分析":
    st.subheader("📈 数据分析")
    records = data["records"]

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        select_acc = st.selectbox("分析账户", ["全部账户"] + account_list, key="分析_acc")
    with col_filter2:
        time_range = st.selectbox("时间范围", ["最近7天", "最近30天", "最近90天", "自定义日期"], key="分析_time")

    today = date.today()
    if time_range == "自定义日期":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            ana_start = st.date_input("开始日期", date(today.year, today.month, 1), key="分析_start")
        with col_d2:
            ana_end = st.date_input("结束日期", today, key="分析_end")
    elif time_range == "最近7天":
        ana_start, ana_end = today - timedelta(days=6), today
    elif time_range == "最近30天":
        ana_start, ana_end = today - timedelta(days=29), today
    else:
        ana_start, ana_end = today - timedelta(days=89), today

    if ana_start > ana_end:
        st.error("开始日期不能晚于结束日期")
    else:
        if select_acc != "全部账户":
            ana_records = filter_records_by_date_account(records, ana_start, ana_end, select_acc)
        else:
            ana_records = filter_records_by_date_account(records, ana_start, ana_end)

        if not ana_records:
            st.warning("所选时间段/账户暂无数据")
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["🍽️ 支出分类", "💰 收入分类", "📅 月度对比", "📈 每日趋势"])

            with tab1:
                expense_cate = group_by_category(ana_records, "支出")
                if expense_cate:
                    fig = px.pie(names=list(expense_cate.keys()), values=list(expense_cate.values()), title="支出分类分布")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("该时间段无支出数据")

            with tab2:
                income_cate = group_by_category(ana_records, "收入")
                if income_cate:
                    fig = px.pie(names=list(income_cate.keys()), values=list(income_cate.values()), title="收入分类分布")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("该时间段无收入数据")

            with tab3:
                month_data = group_by_month(ana_records)
                if month_data:
                    months = list(month_data.keys())
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=months, y=[month_data[m]["income"] for m in months], name="收入"))
                    fig.add_trace(go.Bar(x=months, y=[month_data[m]["expense"] for m in months], name="支出"))
                    fig.update_layout(title="月度收支对比", xaxis_title="月份", yaxis_title="金额(¥)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("该时间段无月度数据")

            with tab4:
                daily_income = defaultdict(float)
                daily_expense = defaultdict(float)
                for r in ana_records:
                    d = r["date"]
                    if r["type"] == "收入":
                        daily_income[d] += r["amount"]
                    else:
                        daily_expense[d] += abs(r["amount"])

                date_list = []
                current = ana_start
                while current <= ana_end:
                    date_list.append(str(current))
                    current += timedelta(days=1)

                income_vals = [daily_income.get(d, 0) for d in date_list]
                expense_vals = [daily_expense.get(d, 0) for d in date_list]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=date_list, y=income_vals, mode='lines+markers', name='收入', line=dict(color='green')))
                fig.add_trace(go.Scatter(x=date_list, y=expense_vals, mode='lines+markers', name='支出', line=dict(color='red')))
                num_dates = len(date_list)
                tickformat = "%m/%d" if num_dates <= 31 else "%y/%m/%d"
                fig.update_layout(
                    title="每日收支趋势",
                    xaxis_title="日期",
                    yaxis_title="金额 (¥)",
                    xaxis=dict(
                        tickformat=tickformat,
                        tickangle=-45 if num_dates > 15 else 0,
                        tickmode="auto",
                        nticks=min(num_dates, 10)
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

                col_a, col_b = st.columns(2)
                col_a.metric("总支出", f"¥{sum(expense_vals):.2f}")
                col_b.metric("总收入", f"¥{sum(income_vals):.2f}")

elif menu == "回收站":
    st.subheader("🗑️ 回收站")
    st.caption("⚠️ 记录保留 30 天，超过将自动清除")
    deleted = data.get("deleted_records", [])

    if not deleted:
        st.info("回收站为空")
    else:
        st.caption(f"共 {len(deleted)} 条已删除的记录")
        today = date.today()
        for idx, rec in enumerate(deleted, 1):
            rec_date = date.fromisoformat(rec["date"])
            days_since_delete = (today - rec_date).days
            days_left = 30 - days_since_delete
            
            if days_left <= 3:
                expire_style = ":red[⚠️ 仅剩 {} 天]".format(days_left)
            elif days_left <= 7:
                expire_style = ":orange[⚡ 仅剩 {} 天]".format(days_left)
            else:
                expire_style = f"剩余 {days_left} 天"
            
            col_a, col_b, col_c = st.columns([4, 1, 1])
            with col_a:
                st.write(f"**{idx}.** 日期：{rec['date']} | 账户：{rec['account']} | {rec['type']} | 分类：{rec['category']}")
                st.write(f"金额：¥{abs(rec['amount']):.2f} | 备注：{rec['remark']} | {expire_style}")
            with col_b:
                if st.button("♻️ 还原", key=f"restore_{rec['id']}"):
                    data["records"].insert(0, rec)
                    data["deleted_records"].remove(rec)
                    save_data(data)
                    st.rerun()
            with col_c:
                if st.button("❌ 彻底删除", key=f"delete_perm_{rec['id']}"):
                    data["deleted_records"].remove(rec)
                    save_data(data)
                    st.rerun()
            st.divider()

elif menu == "系统设置":
    st.subheader("⚙️ 系统设置")
    budget = st.number_input("设置每月预算", min_value=0, value=int(data["month_budget"]))
    if st.button("保存预算"):
        data["month_budget"] = budget
        save_data(data)
        st.success("预算修改成功")

    st.divider()
    st.subheader("🗑️ 危险操作")
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False

    if st.button("清空所有记账数据", type="primary"):
        st.session_state.confirm_clear = True

    if st.session_state.confirm_clear:
        st.error("⚠️ 确定要清空所有数据吗？此操作不可撤销！")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("确认清空", type="primary"):
                data["records"] = []
                data["deleted_records"] = []
                save_data(data)
                st.session_state.confirm_clear = False
                st.rerun()
        with col_b:
            if st.button("取消"):
                st.session_state.confirm_clear = False
                st.rerun()