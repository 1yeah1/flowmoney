<<<<<<< HEAD
=======
"""
FlowMoney 个人记账应用
一个简洁、高效的个人财务管理工具

功能模块：
- 首页仪表盘：财务概览、快捷记账、预算管理
- 记账流水：查看和管理所有收支记录
- 添加记账：快速添加收入和支出记录
- 数据分析：图表展示收支趋势和分类统计
- 回收站：查看和恢复已删除的记录
- 系统设置：管理分类、账户等配置
"""

# ============================================================================
# 1. 导入库和配置
# ============================================================================

# 标准库导入
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
import json
import os
from datetime import datetime, date, timedelta
from collections import defaultdict

<<<<<<< HEAD
=======
# 第三方库导入
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Streamlit页面配置
st.set_page_config(
    page_title="FlowMoney 个人记账",
    page_icon="💰",
    layout="wide"
)

# ============================================================================
# 1.1 常量定义
# ============================================================================

# 数据文件路径
DATA_FILE = "account_data.json"

<<<<<<< HEAD
=======
# 导航菜单配置
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
MENU_ITEMS = [
    {"name": "首页仪表盘", "label": "概览"},
    {"name": "记账流水", "label": "流水"},
    {"name": "添加记账", "label": "记账"},
    {"name": "数据分析", "label": "分析"},
    {"name": "回收站", "label": "回收"},
    {"name": "系统设置", "label": "设置"}
]

<<<<<<< HEAD
=======
# 默认配置
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
DEFAULT_BUDGET = 3000
DEFAULT_EXPENSE_CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "学习", "住宿", "医疗", "其他"]
DEFAULT_INCOME_CATEGORIES = ["工资", "兼职", "奖学金", "其他"]
DEFAULT_ACCOUNTS = ["现金", "微信", "支付宝", "银行卡"]

<<<<<<< HEAD
def render_global_styles():
    st.markdown("""
    <style>
=======
# ============================================================================
# 2. CSS样式定义
# ============================================================================

def render_global_styles():
    """
    渲染全局CSS样式
    
    功能:
    - 定义卡片基础样式和悬停效果
    - 设置不同状态卡片的颜色主题（收入/支出/正常/警告/危险）
    - 自定义按钮、标签页、输入框等组件样式
    """
    st.markdown("""
    <style>
    /* 卡片基础样式 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
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
    }
    
<<<<<<< HEAD
=======
    /* 收入卡片 - 绿色主题 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .metric-card.income {
        background: linear-gradient(145deg, #ecfdf5, #d1fae5);
        border-color: rgba(16, 185, 129, 0.2);
    }
    
<<<<<<< HEAD
=======
    /* 支出卡片 - 红色主题 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .metric-card.expense {
        background: linear-gradient(145deg, #fef2f2, #fee2e2);
        border-color: rgba(239, 68, 68, 0.2);
    }
    
<<<<<<< HEAD
=======
    /* 正常状态卡片 - 蓝色主题 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .metric-card.normal {
        background: linear-gradient(145deg, #eff6ff, #dbeafe);
        border-color: rgba(59, 130, 246, 0.2);
    }
    
<<<<<<< HEAD
=======
    /* 警告状态卡片 - 橙色主题 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .metric-card.warning {
        background: linear-gradient(145deg, #fffbeb, #fef3c7);
        border-color: rgba(251, 191, 36, 0.3);
    }
    
<<<<<<< HEAD
=======
    /* 危险状态卡片 - 红色主题 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .metric-card.danger {
        background: linear-gradient(145deg, #fef2f2, #fee2e2);
        border-color: rgba(239, 68, 68, 0.3);
    }
    
<<<<<<< HEAD
=======
    /* 按钮悬停效果 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
<<<<<<< HEAD
=======
    /* 标签页样式 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
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
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
    }
    
<<<<<<< HEAD
=======
    /* 输入框样式 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
<<<<<<< HEAD
=======
    /* 选择框样式 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid rgba(0, 0, 0, 0.1);
    }
    
<<<<<<< HEAD
=======
    /* 页面平滑滚动 */
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    * { scroll-behavior: smooth; }
    </style>
    """, unsafe_allow_html=True)

def render_navigation_styles():
<<<<<<< HEAD
=======
    """
    渲染导航栏样式
    
    功能：
    - 设置导航栏的渐变背景和圆角
    - 定义标题和信息区域的布局和样式
    - 添加响应式设计，适配移动端显示
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
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
    @media (max-width: 600px) {
        .nav-row { flex-direction: column; gap: 10px; text-align: center; }
        .nav-title { font-size: 18px; }
        .nav-info { font-size: 11px; gap: 8px; }
    }
    </style>
    """, unsafe_allow_html=True)

<<<<<<< HEAD
=======
# ============================================================================
# 3. 数据管理函数
# ============================================================================

>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
def init_data():
    """
    初始化数据文件
    
    功能：
    - 检查数据文件是否存在
    - 如果不存在，创建默认数据结构
    - 默认数据包括：空记录列表、预算、分类、账户等配置
    """
    if not os.path.exists(DATA_FILE):
        default_data = {
<<<<<<< HEAD
            "records": [],
            "deleted_records": [],
            "month_budget": DEFAULT_BUDGET,
            "dark_mode": False,
            "expense_categories": DEFAULT_EXPENSE_CATEGORIES,
            "income_categories": DEFAULT_INCOME_CATEGORIES,
            "accounts": DEFAULT_ACCOUNTS
=======
            "records": [],                    # 正常记录列表
            "deleted_records": [],            # 已删除记录列表（用于回收站）
            "month_budget": DEFAULT_BUDGET,   # 月预算
            "dark_mode": False,               # 深色模式开关
            "expense_categories": DEFAULT_EXPENSE_CATEGORIES,  # 支出分类
            "income_categories": DEFAULT_INCOME_CATEGORIES,    # 收入分类
            "accounts": DEFAULT_ACCOUNTS      # 账户列表
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)

def load_data():
    """
    加载数据文件
    
    功能：
    - 从JSON文件读取所有数据
    - 返回完整的数据字典
    
    返回：
        dict: 包含所有应用数据的字典
    """
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """
    保存数据到文件
    
    功能：
    - 将数据字典写入JSON文件
    - 使用UTF-8编码和缩进格式，便于阅读
    
    参数：
        data (dict): 要保存的数据字典
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cleanup_deleted_records(data, max_days=30):
<<<<<<< HEAD
=======
    """
    清理过期的删除记录
    
    功能：
    - 删除超过指定天数的已删除记录
    - 避免回收站占用过多存储空间
    
    参数：
        data (dict): 数据字典
        max_days (int): 保留天数，默认30天
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    if not data.get("deleted_records"):
        return
    cutoff = str(date.today() - timedelta(days=max_days))
    original_len = len(data["deleted_records"])
    data["deleted_records"] = [r for r in data["deleted_records"] if r.get("date", "") > cutoff]
    if len(data["deleted_records"]) < original_len:
        save_data(data)

def ensure_data_compatibility(data):
<<<<<<< HEAD
=======
    """
    确保数据结构兼容性
    
    功能：
    - 检查数据结构是否完整
    - 为旧版本数据添加缺失的字段
    - 确保应用升级后数据仍然可用
    
    参数：
        data (dict): 数据字典
        
    返回：
        dict: 更新后的数据字典
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    if "expense_categories" not in data:
        data["expense_categories"] = DEFAULT_EXPENSE_CATEGORIES
    if "income_categories" not in data:
        data["income_categories"] = DEFAULT_INCOME_CATEGORIES
    if "deleted_records" not in data:
        data["deleted_records"] = []
    return data
<<<<<<< HEAD

def filter_records_by_date_account(records, start_date, end_date, target_account=None):
=======

# ============================================================================
# 4. 工具函数
# ============================================================================

def filter_records_by_date_account(records, start_date, end_date, target_account=None):
    """
    根据日期和账户筛选记录
    
    功能：
    - 筛选指定日期范围内的记录
    - 可选按账户进一步筛选
    
    参数：
        records (list): 记录列表
        start_date (date): 开始日期
        end_date (date): 结束日期
        target_account (str, optional): 目标账户名称
        
    返回：
        list: 筛选后的记录列表
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    result = []
    for record in records:
        rec_date = date.fromisoformat(record["date"])
        if not (start_date <= rec_date <= end_date):
            continue
        if target_account and record.get("account", "") != target_account:
            continue
        result.append(record)
    return result

def filter_records_by_condition(records, start_date, end_date, account=None, record_type=None, category=None, keyword=None):
<<<<<<< HEAD
=======
    """
    根据多个条件筛选记录
    
    功能：
    - 支持按日期范围、账户、类型、分类、关键词等多条件筛选
    - 所有条件都是可选的，满足所有条件的记录才会被返回
    
    参数：
        records (list): 记录列表
        start_date (date): 开始日期
        end_date (date): 结束日期
        account (str, optional): 账户名称
        record_type (str, optional): 记录类型（收入/支出）
        category (str, optional): 分类名称
        keyword (str, optional): 搜索关键词（匹配备注）
        
    返回：
        list: 筛选后的记录列表
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    result = []
    for record in records:
        rec_date = date.fromisoformat(record["date"])
        if not (start_date <= rec_date <= end_date):
            continue
        if account and account != "全部账户" and record.get("account") != account:
            continue
        if record_type and record_type != "全部" and record.get("type") != record_type:
            continue
        if category and category != "全部分类" and record.get("category") != category:
            continue
        if keyword and keyword.lower() not in record.get("remark", "").lower():
            continue
        result.append(record)
    return result

def group_by_month(records):
    """
    按月分组统计收支
    
    功能：
    - 将记录按月份分组
    - 统计每个月的收入和支出总额
    
    参数：
        records (list): 记录列表
        
    返回：
        dict: 按月分组的统计结果，格式为 {"YYYY-MM": {"income": 0, "expense": 0}}
    """
    month_dict = {}
    for record in records:
        month = record["date"][:7]
        if month not in month_dict:
            month_dict[month] = {"income": 0, "expense": 0}
        if record["type"] == "收入":
            month_dict[month]["income"] += record["amount"]
        else:
            month_dict[month]["expense"] += abs(record["amount"])
    return month_dict

def group_by_category(records, bill_type):
<<<<<<< HEAD
=======
    """
    按分类统计收支
    
    功能：
    - 统计指定类型（收入/支出）的各分类金额
    - 用于生成分类饼图或柱状图
    
    参数：
        records (list): 记录列表
        bill_type (str): 账单类型（"收入" 或 "支出"）
        
    返回：
        dict: 各分类的金额统计，格式为 {"分类名": 金额}
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    category_dict = {}
    for record in records:
        if record["type"] == bill_type:
            category = record["category"]
            value = record["amount"] if bill_type == "收入" else abs(record["amount"])
            category_dict[category] = category_dict.get(category, 0) + value
    return category_dict

def group_by_date(records):
<<<<<<< HEAD
=======
    """
    按日期分组记录
    
    功能：
    - 将记录按日期分组
    - 便于按日期展示或统计
    
    参数：
        records (list): 记录列表
        
    返回：
        dict: 按日期分组的记录，格式为 {"YYYY-MM-DD": [记录列表]}
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    grouped = {}
    for record in records:
        date_key = record["date"]
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(record)
    return grouped

def get_month_stat(records):
    """
    获取当月收支统计
    
    功能：
    - 计算当前月份的总收入和总支出
    
    参数：
        records (list): 记录列表
        
    返回：
        tuple: (收入总额, 支出总额)
    """
    now = datetime.now()
    current_month = f"{now.year}-{now.month:02d}"
    month_records = [r for r in records if r["date"].startswith(current_month)]
    income = sum(r["amount"] for r in month_records if r["type"] == "收入")
    expense = abs(sum(r["amount"] for r in month_records if r["type"] == "支出"))
    return income, expense

def get_today_cost(records):
    """
    获取今日支出
    
    功能：
    - 计算今天的总支出金额
    
    参数：
        records (list): 记录列表
        
    返回：
        float: 今日支出总额
    """
    today = str(date.today())
    today_records = [r for r in records if r["date"] == today and r["type"] == "支出"]
    return abs(sum(r["amount"] for r in today_records))

def get_budget_status(budget, expense):
<<<<<<< HEAD
=======
    """
    获取预算状态
    
    功能：
    - 根据预算和支出计算预算使用状态
    - 返回状态类型和对应的提示文本
    
    参数：
        budget (float): 预算金额
        expense (float): 已支出金额
        
    返回：
        tuple: (状态类型, 提示文本)
               状态类型: "danger"（超支）、"warning"（紧张）、"normal"（正常）
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    left_budget = budget - expense
    if left_budget < 0:
        return "danger", "❌ 超支"
    elif left_budget < budget * 0.2:
        return "warning", "⚠️ 紧张"
    else:
        return "normal", "✅ 正常"

def get_month_remaining_days():
<<<<<<< HEAD
=======
    """
    获取本月剩余天数
    
    功能：
    - 计算从今天到月底还有多少天
    
    返回：
        int: 本月剩余天数
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    today = date.today()
    last_day = (date(today.year, today.month + 1, 1) - timedelta(days=1)).day
    return last_day - today.day

def format_date_label(date_str):
<<<<<<< HEAD
=======
    """
    格式化日期显示标签
    
    功能：
    - 将日期转换为更友好的显示格式
    - 今天、昨天、前天显示为特殊标签
    
    参数：
        date_str (str): 日期字符串，格式为 "YYYY-MM-DD"
        
    返回：
        str: 格式化后的日期标签
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    today = date.today()
    date_obj = date.fromisoformat(date_str)
    days_diff = (today - date_obj).days
    if days_diff == 0:
        return "📅 今天"
    elif days_diff == 1:
        return "📅 昨天"
    elif days_diff == 2:
        return "📅 前天"
    else:
        return f"📅 {date_str}"

def get_expire_days_left(record_date_str):
<<<<<<< HEAD
=======
    """
    获取记录剩余过期天数
    
    功能：
    - 计算回收站中的记录还有多少天会被永久删除
    - 回收站记录保留期为30天
    
    参数：
        record_date_str (str): 记录删除日期
        
    返回：
        int: 剩余天数
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    today = date.today()
    record_date = date.fromisoformat(record_date_str)
    return 30 - (today - record_date).days

def generate_record_id():
<<<<<<< HEAD
    return datetime.now().strftime("%Y%m%d%H%M%S")

def render_navigation_bar(data):
    selected_menu = st.session_state.get("selected_menu", "首页仪表盘")
    
=======
    """
    生成唯一记录ID
    
    功能：
    - 基于当前时间戳生成唯一ID
    - 用于标识每条记录
    
    返回：
        str: 唯一ID，格式为 "YYYYMMDDHHMMSS"
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")

# ============================================================================
# 5. UI组件函数
# ============================================================================

def render_navigation_bar(data):
    """
    渲染导航栏
    
    功能：
    - 显示应用标题和当前日期
    - 显示总记录数统计
    - 渲染导航按钮，支持页面切换
    
    参数：
        data (dict): 数据字典
        
    返回：
        str: 当前选中的菜单名称
    """
    selected_menu = st.session_state.get("selected_menu", "首页仪表盘")
    
    # 导航栏头部
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
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
    
<<<<<<< HEAD
=======
    # 导航按钮
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    cols = st.columns([1, 1, 1, 1, 1, 1])
    for i, item in enumerate(MENU_ITEMS):
        with cols[i]:
            is_selected = (selected_menu == item["name"])
            
            if is_selected:
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
                    }
                    </style>
                """, unsafe_allow_html=True)
            else:
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
                    }
                    div[data-testid="stButton"] > button:hover {
                        background-color: #4338CA !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
            
            if st.button(item["label"], key=f"nav_{item['name']}", use_container_width=True):
                st.session_state["selected_menu"] = item["name"]
                st.rerun()
    
    return st.session_state.get("selected_menu", "首页仪表盘")

def render_metric_card(title, value, status="normal"):
<<<<<<< HEAD
=======
    """
    渲染统计卡片
    
    功能：
    - 显示带有渐变背景的统计卡片
    - 根据状态类型使用不同的颜色主题
    - 支持收入、支出、正常、警告、危险等状态
    
    参数：
        title (str): 卡片标题
        value (str): 显示的数值
        status (str): 状态类型，可选值："income"、"expense"、"normal"、"warning"、"danger"
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    bg_colors = {
        "income": "linear-gradient(145deg, #ecfdf5, #d1fae5)",
        "expense": "linear-gradient(145deg, #fef2f2, #fee2e2)",
        "normal": "linear-gradient(145deg, #eff6ff, #dbeafe)",
        "warning": "linear-gradient(145deg, #fffbeb, #fef3c7)",
        "danger": "linear-gradient(145deg, #fef2f2, #fee2e2)"
    }
    
    border_colors = {
        "income": "rgba(16, 185, 129, 0.2)",
        "expense": "rgba(239, 68, 68, 0.2)",
        "normal": "rgba(59, 130, 246, 0.2)",
        "warning": "rgba(251, 191, 36, 0.3)",
        "danger": "rgba(239, 68, 68, 0.3)"
    }
    
    text_colors = {
        "income": "#059669",
        "expense": "#dc2626",
        "normal": "#2563eb",
        "warning": "#d97706",
        "danger": "#dc2626"
    }
    
    bg = bg_colors.get(status, bg_colors["normal"])
    border = border_colors.get(status, border_colors["normal"])
    text = text_colors.get(status, text_colors["normal"])
    
    st.markdown(f"""
        <div style="background: {bg}; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid {border};">
            <div style="font-size: 13px; color: {text}; margin-bottom: 8px;">{title}</div>
            <div style="font-size: 28px; font-weight: 700; color: {text};">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def render_budget_warning(left_budget, budget, expense):
<<<<<<< HEAD
=======
    """
    渲染预算警告
    
    功能：
    - 当预算超支或剩余不足20%时显示警告提示
    - 使用不同的颜色区分警告级别
    
    参数：
        left_budget (float): 剩余预算
        budget (float): 总预算
        expense (float): 已支出金额
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    if left_budget < 0:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fee2e2, #fecaca); border-radius: 12px; padding: 16px; margin-bottom: 20px; border-left: 4px solid #ef4444;">
                <strong style="color: #dc2626;">⚠️ 本月已超支 ¥{abs(left_budget):.2f}！</strong><br>
                <span style="color: #991b1b; font-size: 14px;">当前预算 ¥{budget:.2f}，已支出 ¥{expense:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    elif left_budget < budget * 0.2:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 16px; margin-bottom: 20px; border-left: 4px solid #f59e0b;">
                <strong style="color: #d97706;">⚡ 预算剩余不足 20%</strong><br>
                <span style="color: #b45309; font-size: 14px;">仅剩 ¥{left_budget:.2f}，请注意控制支出</span>
            </div>
        """, unsafe_allow_html=True)

<<<<<<< HEAD
def render_home_page(data):
=======
# ============================================================================
# 6. 页面渲染函数
# ============================================================================

def render_home_page(data):
    """
    渲染首页仪表盘
    
    功能：
    - 显示新用户引导（首次使用时）
    - 提供快捷记账入口
    - 显示预算设置面板
    - 展示财务概览统计卡片
    - 支持按账户筛选数据
    
    参数：
        data (dict): 数据字典
    """
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.subheader("📊 本月财务概览")
    records = data["records"]
    budget = data["month_budget"]
    
<<<<<<< HEAD
=======
    # 新用户引导
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    if len(records) == 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dbeafe, #bfdbfe); border-radius: 16px; padding: 24px; margin-bottom: 20px; border-left: 5px solid #3b82f6;">
            <h3 style="color: #1e40af; margin-top: 0;">👋 欢迎使用 FlowMoney！</h3>
            <p style="color: #1e3a8a; font-size: 15px; line-height: 1.8;">
                看起来你是第一次使用，让我们开始吧！<br>
                💡 <strong>快速上手：</strong>点击下方【快捷记账】按钮，一键添加你的第一笔支出<br>
                💰 建议先设置本月预算，帮助你更好地管理开支
            </p>
        </div>
        """, unsafe_allow_html=True)
    
<<<<<<< HEAD
=======
    # 快捷记账
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.markdown("""
    <style>
    .quick-add-section {
        background: linear-gradient(135deg, #f5f3ff, #ede9fe);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    .quick-add-title {
        font-size: 16px;
        font-weight: 600;
        color: #7c3aed;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="quick-add-section">', unsafe_allow_html=True)
    st.markdown('<div class="quick-add-title">⚡ 快捷记账 - 一键记常用消费</div>', unsafe_allow_html=True)
    
<<<<<<< HEAD
=======
    # 快捷支出按钮
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    quick_expense = ["🍜 餐饮", "🚌 交通", "🛒 购物", "🎬 娱乐", "📚 学习", "🏠 住宿"]
    quick_cols = st.columns(6)
    for i, item in enumerate(quick_expense):
        with quick_cols[i]:
            if st.button(item, key=f"quick_exp_{i}", use_container_width=True):
                st.session_state["selected_menu"] = "添加记账"
                st.session_state["quick_add"] = {"type": "支出", "category": item[2:]}
                st.rerun()
    
<<<<<<< HEAD
=======
    # 快捷收入按钮
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    quick_income = ["💼 工资", "💻 兼职", "🎓 奖学金"]
    quick_inc_cols = st.columns(3)
    for i, item in enumerate(quick_income):
        with quick_inc_cols[i]:
            if st.button(item, key=f"quick_inc_{i}", use_container_width=True):
                st.session_state["selected_menu"] = "添加记账"
                st.session_state["quick_add"] = {"type": "收入", "category": item[2:]}
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
<<<<<<< HEAD
=======
    # 预算设置
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    with st.expander("⚙️ 设置本月预算"):
        col_budget, col_btn = st.columns([3, 1])
        with col_budget:
            new_budget = st.number_input("💵 月预算金额（元）", min_value=0, max_value=1000000, value=int(budget), step=100)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 保存", use_container_width=True):
                data["month_budget"] = float(new_budget)
                save_data(data)
                st.success(f"✅ 月预算已更新为 ¥{new_budget:.2f}")
                st.rerun()
    
<<<<<<< HEAD
=======
    # 账户筛选
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    account_list = data["accounts"]
    select_acc = st.selectbox("选择查看账户", ["全部账户"] + account_list)
    filter_records = [r for r in records if r.get("account", "") == select_acc] if select_acc != "全部账户" else records
    
<<<<<<< HEAD
=======
    # 统计计算
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    all_month_income, all_month_expense = get_month_stat(records)
    left_budget = budget - all_month_expense
    month_income, month_expense = get_month_stat(filter_records)
    today_cost = get_today_cost(filter_records)
    remaining_days = get_month_remaining_days()
    daily_budget = left_budget / remaining_days if remaining_days > 0 else 0
    budget_status, status_text = get_budget_status(budget, all_month_expense)
    
<<<<<<< HEAD
    render_budget_warning(left_budget, budget, all_month_expense)
    
=======
    # 预算警告
    render_budget_warning(left_budget, budget, all_month_expense)
    
    # 统计卡片
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("💰 本月总收入", f"¥{month_income:.2f}", "income")
    with col2:
        render_metric_card("💸 本月总支出", f"¥{month_expense:.2f}", "expense")
    with col3:
        render_metric_card("📅 今日花费", f"¥{today_cost:.2f}", "warning")
    with col4:
        render_metric_card("📊 剩余预算", f"¥{left_budget:.2f}", budget_status)
    
    col5, col6, col7 = st.columns(3)
    with col5:
        render_metric_card("📆 本月剩余天数", f"{remaining_days} 天")
    with col6:
        daily_text = "⚠️ 已超支" if left_budget < 0 else f"¥{daily_budget:.2f}"
        render_metric_card("🎯 今日可用", daily_text, budget_status)
    with col7:
        render_metric_card("📈 状态", status_text, budget_status)

def render_add_record_page(data):
<<<<<<< HEAD
=======
    """渲染添加记账页面"""
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.subheader("✍️ 新增收支记录")
    
    expense_categories = data["expense_categories"]
    income_categories = data["income_categories"]
    account_list = data["accounts"]
    
<<<<<<< HEAD
=======
    # 处理快捷记账
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    quick_add_info = st.session_state.get("quick_add", None)
    default_type = quick_add_info.get("type", "支出") if quick_add_info else "支出"
    default_category = quick_add_info.get("category", "") if quick_add_info else ""
    if quick_add_info:
        st.session_state.pop("quick_add", None)
    
<<<<<<< HEAD
=======
    # 记账表单
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    col_type, col_acc = st.columns(2)
    with col_type:
        bill_type = st.selectbox("收支类型", ["支出", "收入"], index=0 if default_type == "支出" else 1)
    with col_acc:
        select_account = st.selectbox("记账账户", account_list)
    
    current_categories = income_categories if bill_type == "收入" else expense_categories
    default_cate_index = current_categories.index(default_category) if default_category and default_category in current_categories else 0
    
    col_amount, col_date = st.columns(2)
    with col_amount:
        amount = st.number_input("金额", min_value=0.01, step=0.01)
    with col_date:
        bill_date = st.date_input("选择日期", date.today())
    
    with st.form("add_form", clear_on_submit=True):
        select_cate = st.selectbox("选择分类", current_categories, index=default_cate_index)
        remark = st.text_input("备注信息（选填）")
        
        if default_category:
            st.success(f"⚡ 快捷记账已自动填充：{default_category}")
        
        submit_btn = st.form_submit_button("💾 提交记账")
        
        if submit_btn:
            cost_amount = amount if bill_type == "收入" else -amount
            new_record = {
                "id": generate_record_id(),
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

def render_record_list_page(data):
<<<<<<< HEAD
=======
    """渲染记账流水页面"""
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.subheader("📜 记账流水")
    records = data["records"]
    expense_categories = data["expense_categories"]
    income_categories = data["income_categories"]
    account_list = data["accounts"]
    
<<<<<<< HEAD
=======
    # 筛选条件
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    col_search, col_acc, col_type = st.columns([3, 2, 2])
    with col_search:
        search_keyword = st.text_input("🔍 搜索备注")
    with col_acc:
        select_acc = st.selectbox("🏦 账户筛选", ["全部账户"] + account_list)
    with col_type:
        select_type = st.selectbox("💹 收支类型", ["全部", "支出", "收入"])
    
    col_cate, col_date_range = st.columns([2, 3])
    with col_cate:
        all_categories = expense_categories + income_categories
        select_cate = st.selectbox("🏷️ 分类筛选", ["全部分类"] + all_categories)
    with col_date_range:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("开始日期", date.today() - timedelta(days=30))
        with col_d2:
            end_date = st.date_input("结束日期", date.today())
    
    if start_date <= end_date:
        filter_records = filter_records_by_condition(records, start_date, end_date, select_acc, select_type, select_cate, search_keyword)
        filter_records.sort(key=lambda x: x["date"], reverse=True)
        
        if filter_records:
            st.caption(f"共 {len(filter_records)} 条记录（总计 {len(records)} 条）")
            
<<<<<<< HEAD
=======
            # 导出功能
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            file_name = f"FlowMoney_记账数据_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            st.download_button("📥 导出 JSON", data=json_str, file_name=file_name, mime="application/json")
            
<<<<<<< HEAD
=======
            # 按日期分组显示
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
            grouped_records = group_by_date(filter_records)
            
            for date_key, date_records in grouped_records.items():
                date_label = format_date_label(date_key)
                day_income = sum(r["amount"] for r in date_records if r["type"] == "收入")
                day_expense = abs(sum(r["amount"] for r in date_records if r["type"] == "支出"))
                
                st.markdown(f"### {date_label}")
                st.markdown(f"📝 {len(date_records)} 条记录 | 💸 支出 ¥{day_expense:.2f} | 💰 收入 ¥{day_income:.2f}")
                st.divider()
                
                for idx, rec in enumerate(date_records, 1):
                    type_icon = "💸" if rec['type'] == "支出" else "💰"
                    amount_color = "red" if rec['type'] == "支出" else "green"
                    
                    col_info, col_action = st.columns([5, 2])
                    with col_info:
                        st.write(f"**{idx}.** 账户：{rec['account']} | {type_icon} {rec['type']} | 分类：{rec['category']}")
                        st.write(f"金额：:{amount_color}[¥{abs(rec['amount']):.2f}] | 备注：{rec['remark']}", unsafe_allow_html=True)
                    with col_action:
                        if st.button("🗑️", key=f"del_{rec['id']}", help="删除"):
                            st.session_state[f"confirm_del_{rec['id']}"] = True
                        if st.session_state.get(f"confirm_del_{rec['id']}"):
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

def render_analysis_page(data):
<<<<<<< HEAD
=======
    """渲染数据分析页面"""
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.subheader("📈 数据分析")
    records = data["records"]
    account_list = data["accounts"]
    
<<<<<<< HEAD
=======
    # 筛选条件
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        select_acc = st.selectbox("分析账户", ["全部账户"] + account_list)
    with col_filter2:
        time_range = st.selectbox("时间范围", ["最近7天", "最近30天", "最近90天", "自定义日期"])
    
    today = date.today()
    if time_range == "自定义日期":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            ana_start = st.date_input("开始日期", date(today.year, today.month, 1))
        with col_d2:
            ana_end = st.date_input("结束日期", today)
    elif time_range == "最近7天":
        ana_start, ana_end = today - timedelta(days=6), today
    elif time_range == "最近30天":
        ana_start, ana_end = today - timedelta(days=29), today
    else:
        ana_start, ana_end = today - timedelta(days=89), today
    
    if ana_start <= ana_end:
        if select_acc != "全部账户":
            ana_records = filter_records_by_date_account(records, ana_start, ana_end, select_acc)
        else:
            ana_records = filter_records_by_date_account(records, ana_start, ana_end)
        
        if ana_records:
<<<<<<< HEAD
=======
            # 统计概览
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
            total_income = sum(r["amount"] for r in ana_records if r["type"] == "收入")
            total_expense = abs(sum(r["amount"] for r in ana_records if r["type"] == "支出"))
            net_savings = total_income - total_expense
            days_count = (ana_end - ana_start).days + 1
            avg_daily_expense = total_expense / days_count if days_count > 0 else 0
            
            st.markdown("### 📊 财务概览")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("💰 总收入", f"¥{total_income:.2f}")
            with col_s2:
                st.metric("💸 总支出", f"¥{total_expense:.2f}")
            with col_s3:
                savings_delta = "结余" if net_savings >= 0 else "超支"
                st.metric("💵 净结余", f"¥{net_savings:.2f}", delta=savings_delta, delta_color="normal" if net_savings >= 0 else "inverse")
            with col_s4:
                st.metric("📅 日均支出", f"¥{avg_daily_expense:.2f}")
            
            st.divider()
            tab1, tab2, tab3, tab4 = st.tabs(["🍽️ 支出分类", "💰 收入分类", "📅 月度对比", "📈 每日趋势"])
            
            with tab1:
                expense_cate = group_by_category(ana_records, "支出")
                if expense_cate:
                    fig = px.pie(names=list(expense_cate.keys()), values=list(expense_cate.values()), title="支出分类分布")
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                income_cate = group_by_category(ana_records, "收入")
                if income_cate:
                    fig = px.pie(names=list(income_cate.keys()), values=list(income_cate.values()), title="收入分类分布")
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                month_data = group_by_month(ana_records)
                if month_data:
                    months = list(month_data.keys())
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=months, y=[month_data[m]["income"] for m in months], name="收入"))
                    fig.add_trace(go.Bar(x=months, y=[month_data[m]["expense"] for m in months], name="支出"))
                    fig.update_layout(title="月度收支对比", xaxis_title="月份", yaxis_title="金额(¥)")
                    st.plotly_chart(fig, use_container_width=True)
            
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
                fig.update_layout(title="每日收支趋势", xaxis_title="日期", yaxis_title="金额 (¥)")
                st.plotly_chart(fig, use_container_width=True)

def render_trash_page(data):
<<<<<<< HEAD
=======
    """渲染回收站页面"""
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    st.subheader("🗑️ 回收站")
    st.caption("⚠️ 记录保留 30 天，超过将自动清除")
    
    deleted = data.get("deleted_records", [])
    expense_categories = data["expense_categories"]
    income_categories = data["income_categories"]
    account_list = data["accounts"]
    
    if deleted:
<<<<<<< HEAD
=======
        # 筛选条件
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
        col_search, col_acc, col_type = st.columns([3, 2, 2])
        with col_search:
            search_keyword = st.text_input("🔍 搜索备注")
        with col_acc:
            filter_acc = st.selectbox("🏦 账户筛选", ["全部账户"] + account_list)
        with col_type:
            filter_type = st.selectbox("💹 类型筛选", ["全部", "支出", "收入"])
        
        col_cate, col_date_range = st.columns([2, 3])
        with col_cate:
            all_categories = expense_categories + income_categories
            filter_cate = st.selectbox("🏷️ 分类筛选", ["全部分类"] + all_categories)
        with col_date_range:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("开始日期", date.today() - timedelta(days=30))
            with col_d2:
                end_date = st.date_input("结束日期", date.today())
        
        if start_date <= end_date:
            filtered_records = filter_records_by_condition(deleted, start_date, end_date, filter_acc, filter_type, filter_cate, search_keyword)
            filtered_records.sort(key=lambda x: x["date"], reverse=True)
            
            if filtered_records:
                st.caption(f"共 {len(filtered_records)} 条记录（总计 {len(deleted)} 条）")
                
<<<<<<< HEAD
=======
                # 按日期分组显示
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
                grouped_records = group_by_date(filtered_records)
                
                for date_key, date_records in grouped_records.items():
                    date_label = format_date_label(date_key)
                    day_income = sum(r["amount"] for r in date_records if r["type"] == "收入")
                    day_expense = abs(sum(r["amount"] for r in date_records if r["type"] == "支出"))
                    
                    st.markdown(f"### {date_label}")
                    st.markdown(f"📝 {len(date_records)} 条记录 | 💸 支出 ¥{day_expense:.2f} | 💰 收入 ¥{day_income:.2f}")
                    st.divider()
                    
                    for idx, rec in enumerate(date_records, 1):
                        days_left = get_expire_days_left(rec["date"])
                        expire_style = f":red[⚠️ 仅剩 {days_left} 天]" if days_left <= 3 else f"剩余 {days_left} 天"
                        
                        type_icon = "💸" if rec['type'] == "支出" else "💰"
                        amount_color = "red" if rec['type'] == "支出" else "green"
                        
                        col_info, col_action = st.columns([5, 2])
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

def render_settings_page(data):
<<<<<<< HEAD
    st.subheader("⚙️ 系统设置")
    
=======
    """渲染系统设置页面"""
    st.subheader("⚙️ 系统设置")
    
    # 预算设置
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
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

<<<<<<< HEAD
def main():
    render_global_styles()
    render_navigation_styles()
    
    init_data()
    
=======
# ============================================================================
# 7. 主程序入口
# ============================================================================

def main():
    """
    主应用入口
    
    执行流程：
    1. 渲染全局CSS样式和导航栏样式
    2. 初始化数据文件（如果不存在）
    3. 加载并确保数据兼容性
    4. 清理过期的删除记录
    5. 渲染导航栏
    6. 根据用户选择渲染对应页面
    """
    # 1. 渲染样式
    render_global_styles()
    render_navigation_styles()
    
    # 2. 初始化数据
    init_data()
    
    # 3. 加载数据并确保兼容性
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    data = load_data()
    data = ensure_data_compatibility(data)
    save_data(data)
    
<<<<<<< HEAD
    cleanup_deleted_records(data)
    if "selected_menu" not in st.session_state:
        st.session_state["selected_menu"] = "首页仪表盘"
    if "quick_add" not in st.session_state:
        st.session_state["quick_add"] = None

    selected_menu = render_navigation_bar(data)
    
=======
    # 4. 清理过期记录
    cleanup_deleted_records(data)
    
    # 5. 渲染导航栏
    selected_menu = render_navigation_bar(data)
    
    # 6. 根据选中的菜单渲染对应页面
>>>>>>> bedf59fe88f29a58ad90b9b229eb3dad7edeb049
    if selected_menu == "首页仪表盘":
        render_home_page(data)
    elif selected_menu == "添加记账":
        render_add_record_page(data)
    elif selected_menu == "记账流水":
        render_record_list_page(data)
    elif selected_menu == "数据分析":
        render_analysis_page(data)
    elif selected_menu == "回收站":
        render_trash_page(data)
    elif selected_menu == "系统设置":
        render_settings_page(data)

if __name__ == "__main__":
    main()