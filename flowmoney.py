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
            "income_categories": ["工资", "兼职", "奖学金",  "其他"],
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

    # 始终基于所有账户计算总支出和剩余预算
    all_month_income, all_month_expense = get_month_stat(records)
    left_budget = budget - all_month_expense
    
    # 只在选择特定账户时显示该账户的支出
    month_income, month_expense = get_month_stat(filter_records)
    today_cost = get_today_cost(filter_records)

    today = date.today()
    last_day = (date(today.year, today.month + 1, 1) - timedelta(days=1)).day
    remaining_days = last_day - today.day
    
    if remaining_days > 0:
        daily_budget = left_budget / remaining_days
    else:
        daily_budget = 0

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

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("本月剩余天数", f"{remaining_days} 天")
    with col6:
        if left_budget < 0:
            st.metric("今日可用", f"⚠️ 已超支", delta_color="inverse")
        else:
            st.metric("今日可用", f"¥{daily_budget:.2f}")
    with col7:
        if left_budget < 0:
            st.metric("状态", "❌ 超支", delta_color="inverse")
        elif left_budget < budget * 0.2:
            st.metric("状态", "⚠️ 紧张", delta_color="off")
        else:
            st.metric("状态", "✅ 正常", delta_color="normal")

    with st.expander("📋 今日可用计算规则"):
        st.markdown("""
        **计算公式：**  
        `今日可用 = 剩余预算 ÷ 本月剩余天数`
        
        **举例说明：**  
        - 预算 ¥3000 - 已支出 ¥1200 = 剩余 ¥1800  
        - 剩余 15 天 → 每日可用 ¥120  
        
        **状态标记：**  
        - ✅ 正常：预算剩余 ≥ 20%  
        - ⚠️ 紧张：预算剩余 < 20%  
        - ❌ 超支：已超出预算  
        """)

elif menu == "添加记账":
    st.subheader("✍️ 新增收支记录")

    with st.expander("🔧 管理记账分类（可新增/删除）"):
        tab_exp, tab_inc = st.tabs(["💸 支出分类", "💰 收入分类"])

        with tab_exp:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**💸 支出分类推荐：**")
                exp_recommend = ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "医疗", "健身", "通讯", "日用品"]
                exp_filtered = [t for t in exp_recommend if t not in expense_categories]
                if exp_filtered:
                    cols = st.columns(4)
                    for i, tag in enumerate(exp_filtered):
                        with cols[i % 4]:
                            if st.button(tag, key=f"exp_tag_{i}", use_container_width=True):
                                st.session_state["new_exp_cate"] = tag
                                st.rerun()
                else:
                    st.caption("✅ 支出分类已包含所有推荐项")
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
                st.markdown("**💰 收入分类推荐：**")
                inc_recommend = ["工资", "兼职", "奖学金", "理财", "投资", "红包"]
                inc_filtered = [t for t in inc_recommend if t not in income_categories]
                if inc_filtered:
                    cols = st.columns(4)
                    for i, tag in enumerate(inc_filtered):
                        with cols[i % 4]:
                            if st.button(tag, key=f"inc_tag_{i}", use_container_width=True):
                                st.session_state["new_inc_cate"] = tag
                                st.rerun()
                else:
                    st.caption("✅ 收入分类已包含所有推荐项")
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

    col_amount, col_date = st.columns(2)
    with col_amount:
        amount = st.number_input("金额", min_value=0.01, step=0.01, key="add_amount")
    with col_date:
        bill_date = st.date_input("选择日期", date.today(), key="add_date")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            select_cate = st.selectbox("选择分类", current_categories, key="add_cate")
        with col2:
            st.write("")
            st.write("")

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

    col_search, col_acc, col_type = st.columns([3, 2, 2])
    with col_search:
        search_keyword = st.text_input("🔍 搜索备注", key="流水_search")
    with col_acc:
        select_acc = st.selectbox("🏦 账户筛选", ["全部账户"] + account_list, key="流水_acc")
    with col_type:
        select_type = st.selectbox("💹 收支类型", ["全部", "支出", "收入"], key="流水_type")

    col_cate, col_date_range = st.columns([2, 3])
    with col_cate:
        all_categories = expense_categories + income_categories
        select_cate = st.selectbox("🏷️ 分类筛选", ["全部分类"] + all_categories, key="流水_cate")
    with col_date_range:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("开始日期", date.today() - timedelta(days=30), key="流水_start")
        with col_d2:
            end_date = st.date_input("结束日期", date.today(), key="流水_end")

    if start_date > end_date:
        st.error("开始日期不能晚于结束日期")
    else:
        filter_records = []
        for r in records:
            rec_date = date.fromisoformat(r["date"])
            
            if search_keyword and search_keyword.lower() not in r.get("remark", "").lower():
                continue
            if select_acc != "全部账户" and r.get("account") != select_acc:
                continue
            if select_type != "全部" and r.get("type") != select_type:
                continue
            if select_cate != "全部分类" and r.get("category") != select_cate:
                continue
            if not (start_date <= rec_date <= end_date):
                continue
            
            filter_records.append(r)

        filter_records.sort(key=lambda x: x["date"], reverse=True)

        if not filter_records:
            st.info("暂无符合条件的记录")
        else:
            st.caption(f"共 {len(filter_records)} 条记录（总计 {len(records)} 条）")

            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            file_name = f"FlowMoney_记账数据_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            st.download_button("📥 导出 JSON", data=json_str, file_name=file_name, mime="application/json")

            grouped_records = {}
            for rec in filter_records:
                date_key = rec["date"]
                if date_key not in grouped_records:
                    grouped_records[date_key] = []
                grouped_records[date_key].append(rec)

            today = date.today()
            for date_key, date_records in grouped_records.items():
                date_obj = date.fromisoformat(date_key)
                days_diff = (today - date_obj).days
                
                if days_diff == 0:
                    date_label = "📅 今天"
                elif days_diff == 1:
                    date_label = "📅 昨天"
                elif days_diff == 2:
                    date_label = "📅 前天"
                else:
                    date_label = f"📅 {date_key}"

                day_income = sum(r["amount"] for r in date_records if r["type"] == "收入")
                day_expense = abs(sum(r["amount"] for r in date_records if r["type"] == "支出"))

                st.markdown(f"### {date_label}")
                st.markdown(f"� {len(date_records)} 条记录 | 💸 支出 ¥{day_expense:.2f} | 💰 收入 ¥{day_income:.2f}")
                st.divider()

                for idx, rec in enumerate(date_records, 1):
                    type_icon = "💸" if rec['type'] == "支出" else "💰"
                    amount_color = "red" if rec['type'] == "支出" else "green"

                    col_info, col_action = st.columns([5, 2])
                    with col_info:
                        st.write(f"**{idx}.** 账户：{rec['account']} | {type_icon} {rec['type']} | 分类：{rec['category']}")
                        st.write(f"金额：:{amount_color}[¥{abs(rec['amount']):.2f}] | 备注：{rec['remark']}", unsafe_allow_html=True)
                    with col_action:
                        col_del, col_confirm = st.columns(2)
                        with col_del:
                            if st.button("🗑️", key=f"del_流水_{rec['id']}", help="删除"):
                                st.session_state[f"confirm_del_{rec['id']}"] = True
                        if st.session_state.get(f"confirm_del_{rec['id']}"):
                            with col_confirm:
                                st.warning("确定删除？")
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("是", key=f"yes_del_{rec['id']}"):
                                        data["deleted_records"].insert(0, rec)
                                        data["records"].remove(rec)
                                        save_data(data)
                                        st.session_state[f"confirm_del_{rec['id']}"] = False
                                        st.rerun()
                                with col_no:
                                    if st.button("否", key=f"no_del_{rec['id']}"):
                                        st.session_state[f"confirm_del_{rec['id']}"] = False
                                        st.rerun()
                st.markdown("---")

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
        col_search, col_acc, col_type = st.columns([3, 2, 2])
        with col_search:
            search_keyword = st.text_input("🔍 搜索备注", key="trash_search")
        with col_acc:
            filter_acc = st.selectbox("🏦 账户筛选", ["全部账户"] + account_list, key="trash_acc")
        with col_type:
            filter_type = st.selectbox("💹 类型筛选", ["全部", "支出", "收入"], key="trash_type")

        col_cate, col_date_range, col_expire = st.columns([2, 3, 2])
        with col_cate:
            all_categories = expense_categories + income_categories
            filter_cate = st.selectbox("🏷️ 分类筛选", ["全部分类"] + all_categories, key="trash_cate")
        with col_date_range:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("开始日期", date.today() - timedelta(days=30), key="trash_start")
            with col_d2:
                end_date = st.date_input("结束日期", date.today(), key="trash_end")
        with col_expire:
            expire_options = ["全部", "即将过期（3天内）", "一周内过期", "两周内过期", "本月内过期", "自定义天数"]
            expire_filter = st.selectbox("⏳ 剩余时间", expire_options, key="trash_expire")
            custom_days = 0
            if expire_filter == "自定义天数":
                custom_days = st.number_input("输入天数", min_value=1, max_value=30, value=7, key="trash_custom_days")

        today = date.today()
        filtered_records = []
        for rec in deleted:
            rec_date = date.fromisoformat(rec["date"])
            days_left = 30 - (today - rec_date).days
            
            if search_keyword and search_keyword.lower() not in rec.get("remark", "").lower():
                continue
            if filter_acc != "全部账户" and rec.get("account") != filter_acc:
                continue
            if filter_type != "全部" and rec.get("type") != filter_type:
                continue
            if filter_cate != "全部分类" and rec.get("category") != filter_cate:
                continue
            if not (start_date <= rec_date <= end_date):
                continue
            
            if expire_filter == "即将过期（3天内）" and days_left > 3:
                continue
            elif expire_filter == "一周内过期" and days_left > 7:
                continue
            elif expire_filter == "两周内过期" and days_left > 14:
                continue
            elif expire_filter == "本月内过期" and days_left > 30:
                continue
            elif expire_filter == "自定义天数" and days_left > custom_days:
                continue
            
            filtered_records.append(rec)

        filtered_records.sort(key=lambda x: x["date"], reverse=True)

        if not filtered_records:
            st.info("暂无符合条件的记录")
        else:
            st.caption(f"共 {len(filtered_records)} 条记录（总计 {len(deleted)} 条）")

            if "selected_ids" not in st.session_state:
                st.session_state.selected_ids = set()

            col_select_all, col_deselect, col_count, col_action1, col_action2 = st.columns([2, 2, 2, 2, 2])
            with col_select_all:
                if st.button("☑️ 全选"):
                    st.session_state.selected_ids = set(rec["id"] for rec in filtered_records)
                    for rec in filtered_records:
                        st.session_state[f"cb_trash_{rec['id']}"] = True
                    st.rerun()
            with col_deselect:
                if st.button("☐ 取消全选"):
                    st.session_state.selected_ids.clear()
                    for rec in filtered_records:
                        st.session_state[f"cb_trash_{rec['id']}"] = False
                    st.rerun()
            with col_count:
                st.info(f"已选中 {len(st.session_state.selected_ids)} 条")
            with col_action1:
                if st.button("♻️ 批量还原"):
                    selected_recs = [r for r in filtered_records if r["id"] in st.session_state.selected_ids]
                    for rec in selected_recs:
                        data["records"].insert(0, rec)
                        data["deleted_records"].remove(rec)
                    save_data(data)
                    st.session_state.selected_ids.clear()
                    st.rerun()
            with col_action2:
                if st.button("🗑️ 批量删除"):
                    selected_recs = [r for r in filtered_records if r["id"] in st.session_state.selected_ids]
                    if len(selected_recs) > 0:
                        st.session_state["confirm_batch_delete"] = True
            
            if st.session_state.get("confirm_batch_delete"):
                st.warning(f"⚠️ 确定要彻底删除 {len([r for r in filtered_records if r['id'] in st.session_state.selected_ids])} 条记录吗？此操作不可撤销！")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("确认删除", type="primary"):
                        selected_recs = [r for r in filtered_records if r["id"] in st.session_state.selected_ids]
                        for rec in selected_recs:
                            data["deleted_records"].remove(rec)
                        save_data(data)
                        st.session_state.selected_ids.clear()
                        st.session_state["confirm_batch_delete"] = False
                        st.rerun()
                with col_no:
                    if st.button("取消"):
                        st.session_state["confirm_batch_delete"] = False
                        st.rerun()

            grouped_records = {}
            for rec in filtered_records:
                rec_date = date.fromisoformat(rec["date"])
                date_key = rec["date"]
                if date_key not in grouped_records:
                    grouped_records[date_key] = []
                grouped_records[date_key].append(rec)

            global_idx = 0
            for date_key, date_records in grouped_records.items():
                date_obj = date.fromisoformat(date_key)
                days_diff = (today - date_obj).days
                
                if days_diff == 0:
                    date_label = "📅 今天"
                elif days_diff == 1:
                    date_label = "📅 昨天"
                elif days_diff == 2:
                    date_label = "📅 前天"
                else:
                    date_label = f"📅 {date_key}"

                day_income = sum(r["amount"] for r in date_records if r["type"] == "收入")
                day_expense = abs(sum(r["amount"] for r in date_records if r["type"] == "支出"))

                st.markdown(f"### {date_label}")
                st.markdown(f"📝 {len(date_records)} 条记录 | 💸 支出 ¥{day_expense:.2f} | 💰 收入 ¥{day_income:.2f}")
                st.divider()

                for idx, rec in enumerate(date_records, 1):
                    cb_key = f"cb_trash_{rec['id']}"
                    rec_date = date.fromisoformat(rec["date"])
                    days_left = 30 - (today - rec_date).days
                    
                    if days_left <= 3:
                        expire_style = ":red[⚠️ 仅剩 {} 天]".format(days_left)
                    elif days_left <= 7:
                        expire_style = ":orange[⚡ 仅剩 {} 天]".format(days_left)
                    else:
                        expire_style = f"剩余 {days_left} 天"

                    type_icon = "💸" if rec['type'] == "支出" else "💰"
                    amount_color = "red" if rec['type'] == "支出" else "green"

                    col_check, col_info, col_action = st.columns([0.5, 5, 2])
                    with col_check:
                        if cb_key not in st.session_state:
                            st.session_state[cb_key] = rec["id"] in st.session_state.selected_ids
                        checked = st.checkbox("", key=cb_key)
                        if checked:
                            st.session_state.selected_ids.add(rec["id"])
                        else:
                            st.session_state.selected_ids.discard(rec["id"])
                    with col_info:
                        st.write(f"**{idx}.** 账户：{rec['account']} | {type_icon} {rec['type']} | 分类：{rec['category']}")
                        st.write(f"金额：:{amount_color}[¥{abs(rec['amount']):.2f}] | 备注：{rec['remark']} | {expire_style}", unsafe_allow_html=True)
                    with col_action:
                        col_restore, col_delete = st.columns(2)
                        with col_restore:
                            if st.button("♻️", key=f"restore_{rec['id']}", help="还原"):
                                data["records"].insert(0, rec)
                                data["deleted_records"].remove(rec)
                                save_data(data)
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️", key=f"delete_perm_{rec['id']}", help="彻底删除"):
                                st.session_state[f"confirm_perm_del_{rec['id']}"] = True
                        if st.session_state.get(f"confirm_perm_del_{rec['id']}"):
                            st.warning("⚠️ 确定彻底删除？此操作不可撤销！")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("确认删除", key=f"yes_perm_del_{rec['id']}", type="primary"):
                                    data["deleted_records"].remove(rec)
                                    save_data(data)
                                    st.session_state[f"confirm_perm_del_{rec['id']}"] = False
                                    st.rerun()
                            with col_no:
                                if st.button("取消", key=f"no_perm_del_{rec['id']}"):
                                    st.session_state[f"confirm_perm_del_{rec['id']}"] = False
                                    st.rerun()
                st.markdown("---")

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