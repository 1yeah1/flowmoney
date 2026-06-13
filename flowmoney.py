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

# 添加自定义样式 - 视觉层次与交互体验优化
st.markdown("""
    <style>
    /* ===== 视觉层次 ===== */
    /* 卡片样式 */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
        border-color: rgba(79, 70, 229, 0.2);
    }
    
    /* 收入卡片 - 绿色主题 */
    .metric-card.income {
        background: linear-gradient(145deg, #ecfdf5, #d1fae5);
        border-color: rgba(16, 185, 129, 0.2);
    }
    .metric-card.income:hover {
        box-shadow: 0 12px 30px rgba(16, 185, 129, 0.15);
        border-color: rgba(16, 185, 129, 0.4);
    }
    
    /* 支出卡片 - 红色主题 */
    .metric-card.expense {
        background: linear-gradient(145deg, #fef2f2, #fee2e2);
        border-color: rgba(239, 68, 68, 0.2);
    }
    .metric-card.expense:hover {
        box-shadow: 0 12px 30px rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.4);
    }
    
    /* 正常状态卡片 - 蓝色主题 */
    .metric-card.normal {
        background: linear-gradient(145deg, #eff6ff, #dbeafe);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
    /* 警告状态卡片 - 橙色主题 */
    .metric-card.warning {
        background: linear-gradient(145deg, #fffbeb, #fef3c7);
        border-color: rgba(251, 191, 36, 0.3);
    }
    
    /* 危险状态卡片 - 红色主题 */
    .metric-card.danger {
        background: linear-gradient(145deg, #fef2f2, #fee2e2);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
    /* ===== 交互效果 ===== */
    /* 按钮悬停效果：上移2px + 阴影 */
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* 卡片悬停效果：上移4px + 阴影增强 */
    .stMetric {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 16px;
    }
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
    }
    
    /* 进度条圆角样式 */
    .stProgress > div > div {
        border-radius: 12px;
        height: 8px;
    }
    
    /* 页面平滑滚动 */
    * {
        scroll-behavior: smooth;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        padding: 8px;
        background: rgba(79, 70, 229, 0.05);
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(79, 70, 229, 0.1);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

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

# 响应式顶部导航栏设计
st.markdown("""
    <style>
    .main-nav {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    .nav-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nav-title {
        font-size: 24px;
        font-weight: 700;
        color: white;
    }
    .nav-info {
        color: rgba(255,255,255,0.9);
        font-size: 14px;
        display: flex;
        gap: 20px;
    }
    .nav-buttons-container {
        display: flex;
        gap: 8px;
        margin-top: 16px;
        flex-wrap: wrap;
    }
    
    /* 中等屏幕适配 (平板) */
    @media (max-width: 900px) {
        .main-nav {
            padding: 16px 16px;
        }
        .nav-title {
            font-size: 20px;
        }
        .nav-info {
            font-size: 12px;
            gap: 12px;
        }
        .nav-buttons-container {
            gap: 6px;
        }
    }
    
    /* 小屏幕适配 (手机) */
    @media (max-width: 600px) {
        .main-nav {
            padding: 12px 12px;
            border-radius: 12px;
        }
        .nav-row {
            flex-direction: column;
            gap: 10px;
            text-align: center;
        }
        .nav-title {
            font-size: 18px;
        }
        .nav-info {
            font-size: 11px;
            gap: 8px;
        }
        .nav-buttons-container {
            justify-content: center;
            gap: 4px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 导航菜单项
menu_items = [
    {"name": "首页仪表盘", "label": "概览"},
    {"name": "记账流水", "label": "流水"},
    {"name": "添加记账", "label": "记账"},
    {"name": "数据分析", "label": "分析"},
    {"name": "回收站", "label": "回收"},
    {"name": "系统设置", "label": "设置"}
]

# 获取当前选中的菜单
selected_menu = st.session_state.get("selected_menu", "首页仪表盘")

# 渲染导航栏头部
st.markdown(f"""
<div class="main-nav">
    <div class="nav-row">
        <div class="nav-title">💰 FlowMoney</div>
        <div class="nav-info">
            <span>📅 {datetime.now().strftime('%Y年%m月%d日')}</span>
            <span>📝 总记录: {len(data['records'])}条</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 创建导航按钮（使用 Streamlit 原生按钮）
cols = st.columns([1,1,1,1,1,1])  # 6个等宽列

for i, item in enumerate(menu_items):
    with cols[i]:
        is_selected = (selected_menu == item["name"])
        
        if is_selected:
            # 选中状态：白色背景 + 紫色文字
            st.markdown("""
                <style>
                div[data-testid="stButton"] > button {
                    background-color: white !important;
                    color: #4F46E5 !important;
                    border-radius: 10px;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 14px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                }
                div[data-testid="stButton"] > button:hover {
                    transform: translateY(-2px);
                }
                </style>
            """, unsafe_allow_html=True)
        else:
            # 未选中状态：深紫色背景 + 白色文字
            st.markdown("""
                <style>
                div[data-testid="stButton"] > button {
                    background-color: #3730A3 !important;
                    color: white !important;
                    border-radius: 10px;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 14px;
                    border: none !important;
                    transition: all 0.3s ease;
                }
                div[data-testid="stButton"] > button:hover {
                    background-color: #4338CA !important;
                    transform: translateY(-2px);
                }
                </style>
            """, unsafe_allow_html=True)
        
        if st.button(item["label"], key=f"nav_{item['name']}", use_container_width=True):
            st.session_state["selected_menu"] = item["name"]
            st.rerun()

menu = st.session_state.get("selected_menu", "首页仪表盘")

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

    # 预算状态判断
    if left_budget < 0:
        budget_status = "danger"
        status_text = "❌ 超支"
    elif left_budget < budget * 0.2:
        budget_status = "warning"
        status_text = "⚠️ 紧张"
    else:
        budget_status = "normal"
        status_text = "✅ 正常"

    # 预算警告提示
    if left_budget < 0:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fee2e2, #fecaca); border-radius: 12px; padding: 16px; margin-bottom: 20px; border-left: 4px solid #ef4444;">
                <strong style="color: #dc2626;">⚠️ 本月已超支 ¥{abs(left_budget):.2f}！</strong><br>
                <span style="color: #991b1b; font-size: 14px;">当前预算 ¥{budget:.2f}，已支出 ¥{month_expense:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    elif left_budget < budget * 0.2:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 16px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
                <strong style="color: #d97706;">⚡ 预算剩余不足 20%</strong><br>
                <span style="color: #b45309; font-size: 14px;">仅剩 ¥{left_budget:.2f}，请注意控制支出</span>
            </div>
        """, unsafe_allow_html=True)

    # 第一行卡片：主要财务数据（紫色主题配色）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, #ede9fe, #ddd6fe); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.25); transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: #7c3aed; margin-bottom: 8px;">💰 本月总收入</div>
                <div style="font-size: 28px; font-weight: 700; color: #5b21b6;">¥{month_income:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, #fce7f3, #fbcfe8); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.15); border: 1px solid rgba(236, 72, 153, 0.25); transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: #db2777; margin-bottom: 8px;">💸 本月总支出</div>
                <div style="font-size: 28px; font-weight: 700; color: #be185d;">¥{month_expense:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, #fde68a, #fcd34d); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(251, 191, 36, 0.2); border: 1px solid rgba(251, 191, 36, 0.3); transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: #ca8a04; margin-bottom: 8px;">📅 今日花费</div>
                <div style="font-size: 28px; font-weight: 700; color: #a16207;">¥{today_cost:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # 剩余预算根据状态使用不同紫色调
        if left_budget < 0:
            bg_color, border_color, text_color, value_color = "#fce7f3", "rgba(236, 72, 153, 0.3)", "#db2777", "#be185d"
        elif left_budget < budget * 0.2:
            bg_color, border_color, text_color, value_color = "#fef3c7", "rgba(251, 191, 36, 0.3)", "#ca8a04", "#a16207"
        else:
            bg_color, border_color, text_color, value_color = "#e0e7ff", "rgba(99, 102, 241, 0.25)", "#6366f1", "#4f46e5"
        
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, {bg_color}, #ffffff); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid {border_color}; transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: {text_color}; margin-bottom: 8px;">📊 剩余预算</div>
                <div style="font-size: 28px; font-weight: 700; color: {value_color};">¥{left_budget:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    # 第二行卡片：辅助信息（紫色主题配色）
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, #e0e7ff, #c7d2fe); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.25); transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: #6366f1; margin-bottom: 8px;">📆 本月剩余天数</div>
                <div style="font-size: 28px; font-weight: 700; color: #4f46e5;">{remaining_days} 天</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col6:
        if left_budget < 0:
            bg_color, border_color, text_color, value_color = "#fce7f3", "rgba(236, 72, 153, 0.3)", "#db2777", "#be185d"
            daily_text = "⚠️ 已超支"
        else:
            bg_color, border_color, text_color, value_color = "#ede9fe", "rgba(139, 92, 246, 0.25)", "#7c3aed", "#5b21b6"
            daily_text = f"¥{daily_budget:.2f}"
        
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, {bg_color}, #ffffff); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid {border_color}; transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: {text_color}; margin-bottom: 8px;">🎯 今日可用</div>
                <div style="font-size: 28px; font-weight: 700; color: {value_color};">{daily_text}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col7:
        if left_budget < 0:
            bg_color, border_color, text_color = "#fce7f3", "rgba(236, 72, 153, 0.3)", "#db2777"
        elif left_budget < budget * 0.2:
            bg_color, border_color, text_color = "#fef3c7", "rgba(251, 191, 36, 0.3)", "#ca8a04"
        else:
            bg_color, border_color, text_color = "#d1fae5", "rgba(16, 185, 129, 0.25)", "#059669"
        
        st.markdown(f"""
            <div style="background: linear-gradient(145deg, {bg_color}, #ffffff); border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid {border_color}; transition: all 0.3s ease;" class="hover-card">
                <div style="font-size: 13px; color: {text_color}; margin-bottom: 8px;">📈 状态</div>
                <div style="font-size: 24px; font-weight: 700; color: {text_color};">{status_text}</div>
            </div>
        """, unsafe_allow_html=True)

    # 添加卡片悬停动画效果
    st.markdown("""
        <style>
        .hover-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15) !important;
        }
        </style>
    """, unsafe_allow_html=True)

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
            # ===== 顶部统计卡片 =====
            total_income = sum(r["amount"] for r in ana_records if r["type"] == "收入")
            total_expense = abs(sum(r["amount"] for r in ana_records if r["type"] == "支出"))
            net_savings = total_income - total_expense
            days_count = (ana_end - ana_start).days + 1
            avg_daily_expense = total_expense / days_count if days_count > 0 else 0
            transaction_count = len(ana_records)

            st.markdown("### 📊 财务概览")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("💰 总收入", f"¥{total_income:.2f}", help="所选时间段内的总收入")
            with col_s2:
                st.metric("💸 总支出", f"¥{total_expense:.2f}", help="所选时间段内的总支出")
            with col_s3:
                savings_delta = "结余" if net_savings >= 0 else "超支"
                st.metric("💵 净结余", f"¥{net_savings:.2f}", delta=savings_delta,
                         delta_color="normal" if net_savings >= 0 else "inverse")
            with col_s4:
                st.metric("📅 日均支出", f"¥{avg_daily_expense:.2f}", 
                         help=f"基于 {days_count} 天计算")

            col_s5, col_s6, col_s7, col_s8 = st.columns(4)
            with col_s5:
                max_expense_cat = max(group_by_category(ana_records, "支出").items(), 
                                     key=lambda x: x[1], default=("暂无", 0))
                st.metric("� 最高支出分类", max_expense_cat[0], 
                         delta=f"¥{max_expense_cat[1]:.2f}" if max_expense_cat[1] > 0 else None)
            with col_s6:
                max_income_cat = max(group_by_category(ana_records, "收入").items(), 
                                    key=lambda x: x[1], default=("暂无", 0))
                st.metric("� 最高收入分类", max_income_cat[0],
                         delta=f"¥{max_income_cat[1]:.2f}" if max_income_cat[1] > 0 else None)
            with col_s7:
                budget_used = (total_expense / data["month_budget"] * 100) if data["month_budget"] > 0 else 0
                st.metric("📊 预算使用率", f"{budget_used:.1f}%",
                         delta="⚠️ 超预算" if budget_used > 100 else "✅ 正常",
                         delta_color="inverse" if budget_used > 100 else "normal")
            st.divider()
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