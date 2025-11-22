import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบติดตามเป้าหมายการขาย & Workflow", layout="wide")

# --- ข้อมูลเริ่มต้นของสินค้า (Default Product Data) ---
# เป้าขายรวม: 250 + 150 + 100 + 109 = 609
# ขายได้แล้วรวม: 100 + 50 + 20 + 50 = 220
DEFAULT_PRODUCTS_DATA = pd.DataFrame([
    {"สินค้า": "ปูน", "เป้าขาย": 250, "สต็อกปัจจุบัน": 300, "ขายได้แล้ว": 100},
    {"สินค้า": "สี", "เป้าขาย": 150, "สต็อกปัจจุบัน": 50, "ขายได้แล้ว": 50},
    {"สินค้า": "เคมีภัณฑ์", "เป้าขาย": 100, "สต็อกปัจจุบัน": 250, "ขายได้แล้ว": 20},
    {"สินค้า": "ไม่สังเคราะห์", "เป้าขาย": 109, "สต็อกปัจจุบัน": 100, "ขายได้แล้ว": 50},
])

# --- ข้อมูลเริ่มต้นของงาน (Default Task Data) ---
DEFAULT_TASKS_DATA = pd.DataFrame([
    {"งาน": "กำหนดเป้าขาย & SKU", "แผนก": "Sales", "ผู้รับผิดชอบ": "คุณ A", "สถานะ": "เรียบร้อย", "กำหนดส่ง": "2025-12-01"},
    {"งาน": "ประชุม Kick-off", "แผนก": "All", "ผู้รับผิดชอบ": "คุณ A", "สถานะ": "เรียบร้อย", "กำหนดส่ง": "2025-12-03"},
    {"งาน": "อนุมัติงบประมาณ", "แผนก": "Accounting", "ผู้รับผิดชอบ": "คุณ B", "สถานะ": "กำลังดำเนินการ", "กำหนดส่ง": "2025-12-05"},
    {"งาน": "สั่งสินค้าเข้าสต็อก", "แผนก": "Purchasing", "ผู้รับผิดชอบ": "คุณ C", "สถานะ": "ยังไม่เริ่ม", "กำหนดส่ง": "2025-12-10"},
    {"งาน": "เตรียมพื้นที่คลัง", "แผนก": "Warehouse", "ผู้รับผิดชอบ": "คุณ D", "สถานะ": "รอของเข้า", "กำหนดส่ง": "2025-12-10"},
    {"งาน": "เตรียมรายชื่อลูกค้าเก่า", "แผนก": "CRM", "ผู้รับผิดชอบ": "คุณ E", "สถานะ": "กำลังดำเนินการ", "กำหนดส่ง": "2025-12-12"},
    {"งาน": "ผลิต Content รูป/คลิป", "แผนก": "Content", "ผู้รับผิดชอบ": "คุณ F", "สถานะ": "ล่าช้า", "กำหนดส่ง": "2025-12-15"},
    {"งาน": "ยิงโฆษณา (Ads Setup)", "แผนก": "Content", "ผู้รับผิดชอบ": "คุณ F", "สถานะ": "ยังไม่เริ่ม", "กำหนดส่ง": "2025-12-20"},
])

# --- 1. ส่วนจัดการข้อมูล (จำลอง Database) ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = DEFAULT_TASKS_DATA.copy()

if 'products' not in st.session_state:
    st.session_state.products = DEFAULT_PRODUCTS_DATA.copy()

# --- 2. ส่วนแสดงผล (Sidebar Menu) ---
st.sidebar.title("🏢 เมนูหลัก")
menu = st.sidebar.radio("เลือกหน้าจอ", ["📊 Dashboard ภาพรวม", "✅ ติดตามงาน (Workflow)", "📦 สต็อก & ยอดขาย", "🗺️ Map Sales"]) 

# --- 3. หน้าจอ Dashboard ---
if menu == "📊 Dashboard ภาพรวม":
    st.title("📊 Dashboard ภาพรวมความคืบหน้า")
    
    # คำนวณตัวเลขรวม
    df_prod = st.session_state.products
    total_target = df_prod['เป้าขาย'].sum()
    total_sold = df_prod['ขายได้แล้ว'].sum()
    # ป้องกันการหารด้วยศูนย์
    progress = (total_sold / total_target) * 100 if total_target > 0 else 0

    # แสดง Metrics
    col1, col2, col3 = st.columns(3)
    # แสดงผล: 609m และ 220m
    col1.metric("เป้าหมายรวม (ล้านบาท)", f"฿{total_target:,}m")
    col2.metric("ขายได้แล้ว (ล้านบาท)", f"฿{total_sold:,}m")
    col3.metric("ความสำเร็จ (%)", f"{progress:.2f}%")
    
    st.progress(progress / 100)
    
    st.markdown("---")
    
    # กราฟแท่งเปรียบเทียบ
    st.subheader("📈 เปรียบเทียบ เป้าหมาย vs ยอดขายจริง")
    fig = px.bar(df_prod, x="สินค้า", y=["เป้าขาย", "ขายได้แล้ว"], barmode='group', title="แยกตามสินค้า")
    st.plotly_chart(fig, use_container_width=True)

# --- 4. หน้าจอติดตามงาน (Workflow) ---
elif menu == "✅ ติดตามงาน (Workflow)":
    st.title("✅ รายการสิ่งที่ต้องทำ (To-Do List)")
    st.info("💡 สามารถแก้ไขข้อมูลในตารางได้โดยตรง (ดับเบิ้ลคลิก)")
    
    # --- ส่วนที่ 4.1: แบบฟอร์มเพิ่มงาน ---
    st.markdown("---")
    st.subheader("➕ เพิ่มงานใหม่ (Add Task)")
    
    with st.form("add_task_form", clear_on_submit=True):
        dept_options = list(st.session_state.tasks['แผนก'].unique())
        
        col_task, col_dept, col_owner, col_date = st.columns(4)
        
        with col_task:
            task_name = st.text_input("ชื่องาน (Task Name)", max_chars=100)
        with col_dept:
            department = st.selectbox("แผนกรับผิดชอบ", options=dept_options)
        with col_owner:
            owner = st.text_input("ผู้รับผิดชอบ (Owner)", max_chars=50)
        with col_date:
            due_date = st.date_input("กำหนดส่ง (Due Date)")
        
        submitted = st.form_submit_button("บันทึกงานใหม่ 💾")
        
        if submitted:
            if task_name and owner:
                new_task = pd.DataFrame([{
                    "งาน": task_name,
                    "แผนก": department,
                    "ผู้รับผิดชอบ": owner,
                    "สถานะ": "ยังไม่เริ่ม",
                    "กำหนดส่ง": due_date.strftime('%Y-%m-%d')
                }])
                
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_task], ignore_index=True)
                st.success(f"บันทึกงาน '{task_name}' เรียบร้อยแล้ว!")
                st.rerun() 
            else:
                st.error("กรุณากรอกชื่องานและผู้รับผิดชอบ")
    
    # --- ส่วนที่ 4.2: ตารางงานที่แก้ไขได้ ---
    st.markdown("---")
    dept_filter = st.selectbox("กรองตามแผนก", ["All Departments"] + list(st.session_state.tasks['แผนก'].unique()))
    
    if dept_filter != "All Departments":
        df_display = st.session_state.tasks[st.session_state.tasks['แผนก'] == dept_filter]
    else:
        df_display = st.session_state.tasks

    edited_df = st.data_editor(
        df_display,
        column_config={
            "สถานะ": st.column_config.SelectboxColumn(
                "สถานะงาน",
                options=["ยังไม่เริ่ม", "กำลังดำเนินการ", "เรียบร้อย", "ล่าช้า", "รอของเข้า"],
                required=True,
            )
        },
        num_rows="dynamic",
        use_container_width=True,
        key="task_editor"
    )
    st.session_state.tasks = edited_df

    # --- ส่วนที่ 4.3: ปฏิทินงานรวม ---
    st.markdown("---")
    st.subheader("🗓 ปฏิทินงานรวมตามกำหนดส่ง")
    
    df_calendar = st.session_state.tasks.copy()
    df_calendar['กำหนดส่ง'] = pd.to_datetime(df_calendar['กำหนดส่ง']) 
    df_calendar = df_calendar.sort_values(by='กำหนดส่ง')
    df_calendar['วันที่'] = df_calendar['กำหนดส่ง'].dt.strftime('%Y-%m-%d')

    for date, group in df_calendar.groupby('วันที่'):
        st.markdown(f"#### 📅 {date}")
        st.dataframe(
            group[['งาน', 'แผนก', 'ผู้รับผิดชอบ', 'สถานะ']],
            hide_index=True,
            use_container_width=True
        )

# --- 5. หน้าจอสต็อกและยอดขาย ---
elif menu == "📦 สต็อก & ยอดขาย":
    st.title("📦 ระบบติดตามสต็อกและยอดขาย")
    
    # --- ปุ่มรีเซ็ตข้อมูล ---
    if st.button("🔄 รีเซ็ตข้อมูลสต็อก/ยอดขาย"):
        st.session_state.products = DEFAULT_PRODUCTS_DATA.copy()
        st.success("ข้อมูลสินค้าถูกรีเซ็ตเรียบร้อยแล้ว!")
        st.rerun()
    st.markdown("---")
    # -----------------------

    st.warning("⚠️ แจ้งเตือน: สินค้าที่มีสต็อกต่ำกว่า 20% ของเป้าหมาย จะแสดงสีแดง")
    
    # คำนวณของพร้อมขาย
    df_inventory = st.session_state.products.copy()
    df_inventory['คงเหลือจริง'] = df_inventory['สต็อกปัจจุบัน'] - df_inventory['ขายได้แล้ว']
    
    # ตารางแก้ไขยอดขายและสต็อก
    edited_inv = st.data_editor(
        df_inventory,
        column_config={
            "เป้าขาย": st.column_config.NumberColumn("เป้าหมาย (ล้านบาท)"),
            "สต็อกปัจจุบัน": st.column_config.NumberColumn("รับของเข้า (ชิ้น)"),
            "ขายได้แล้ว": st.column_config.NumberColumn("ขายออก (ชิ้น)"),
            "คงเหลือจริง": st.column_config.NumberColumn("พร้อมขาย (ชิ้น)", disabled=True),
        },
        use_container_width=True,
        key="inv_editor"
    )
    
    # อัปเดต Session State
    st.session_state.products = edited_inv

# --- 6. หน้าจอ Map Sales (New Page) ---
elif menu == "🗺️ Map Sales":
    st.title("🗺️ แผนที่การขาย (Sales Map)")
    
    st.warning("⚠️ แผนที่นี้แสดงผลผ่านการฝังลิงก์ (iframe) อาจต้องมีการตั้งค่าลิงก์ Google Maps ให้ถูกต้องเพื่อให้แสดงผลได้สมบูรณ์")

    # ฝังโค้ด iframe ด้วย st.components.v1.html
    components.html(
        """
        <iframe 
            src="https://www.google.com/maps/d/u/0/embed?mid=11RSu1pauVQVgTyJ0SbQ-8i23wPliLhk&ehbc=2E312F" 
            width="100%" 
            height="600"
            frameborder="0" 
            style="border:0" 
            allowfullscreen="" 
            aria-hidden="false" 
            tabindex="0"
        ></iframe>
        """,
        height=620 # กำหนดความสูงของ Container
    )
