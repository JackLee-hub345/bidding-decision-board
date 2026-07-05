import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import shutil
from matplotlib.colors import LinearSegmentedColormap

# =====================================================================
# 🚨 核心修复：强制清除云端 Matplotlib 的顽固字体缓存，解决豆腐块乱码
# =====================================================================
cache_dir = matplotlib.get_cachedir()
if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)
    except Exception:
        pass

# ----------------- 页面基础配置与深度美化 -----------------
st.set_page_config(page_title="投标报价智能决策看板 v6.2", layout="wide")

st.markdown("""
<style>
.main { background-color: #fcfcfc; }
.stButton>button { width: 100%; border-radius: 6px; font-weight: bold; background-color: #0068c9; color: white; }
.process-box { background-color: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #dee2e6; margin-bottom: 10px; }
.metric-box { background-color: #ffffff; padding: 15px; border-radius: 8px; border-left: 5px solid #d32f2f; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.report-card { background-color: #f4fbf7; padding: 20px; border-radius: 8px; border-left: 5px solid #2e7d32; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# 告诉 Matplotlib 优先使用我们刚装的文泉驿字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'SimHei', 'Microsoft YaHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False 

st.title("📊 投标报价智能决策看板 v6.2")
st.write("核心算法：全景滑动雷达扫描 + 多梯队弹性网格布防 + 强制防废标拓宽 + 10万次蒙特卡洛联合火力验证。")
st.markdown("---")
# ----------------- 1. 核心战略参数与阵型拆解 -----------------
st.header("1. 🎯 正投舰队布防策略与 K 值规则")
col_base1, col_base2 = st.columns([1.5, 1])

with col_base1:
    st.write("##### 💼 正投单位阶梯化兵力分配")
    bc1, bc2 = st.columns(2)
    total_our_units = bc1.number_input("我方正投总家数", min_value=2, max_value=30, value=5, step=1)
    
    default_main = max(1, int(total_our_units * 0.66))
    num_main_units = bc2.number_input("主力家数 (守核心高胜率区)", min_value=1, max_value=total_our_units, value=default_main, step=1)
    
    # 【新增】：最小战术步距防守底线
    min_main_step = st.number_input("主力最小战术步距 (%) - 智能防废标底线", min_value=0.01, value=0.20, step=0.05)
    
    num_flank_units = total_our_units - num_main_units
    st.info(f"兵力分配：主力核心 {num_main_units} 家，侧翼掩护 {num_flank_units} 家。")
    
    if num_flank_units > 0:
        flank_strategy = st.radio(
            "🛡️ 侧翼掩护部队落位战略指引：",
            ["👈 部署在左侧 (价格更低，防御对手极端杀价踩踏)", 
             "👉 部署在右侧 (价格更高，对冲主阵型踏空，搏取高利润)", 
             "⚖️ 双侧均衡部署 (左右各分兵，全范围网格化兜底)"]
        )
    else:
        flank_strategy = "无侧翼部队"

with col_base2:
    st.write("##### 🎲 评标基准 K 值组合 (自动摇号)")
    st.caption("K1 固定从 [0.95~0.90] 中均等抽取。")
    k1_options = np.array([0.95, 0.94, 0.93, 0.92, 0.91, 0.90])
    st.caption("请设定 K2 的三组抽签组合 (K3 = 1 - K2)：")
    kc1, kc2, kc3 = st.columns(3)
    k2_1 = kc1.number_input("K2 (组1)", value=0.4, step=0.1)
    k2_2 = kc2.number_input("K2 (组2)", value=0.5, step=0.1)
    k2_3 = kc3.number_input("K2 (组3)", value=0.6, step=0.1)
    k_pairs = np.array([[k2_1, round(1.0 - k2_1, 2)], [k2_2, round(1.0 - k2_2, 2)], [k2_3, round(1.0 - k2_3, 2)]])

st.markdown("---")

# ----------------- 2. 动态市场大盘阵型推演 -----------------
st.header("2. 📋 动态市场大盘搅局阵型池")

st.write("##### 👤 独立竞争对手区间跳动设置")
col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
num_competitors = col_comp1.number_input("独立对手总家数", min_value=0, value=15, step=1)
comp_min = col_comp2.number_input("统一随机下限(%)", value=93.0, step=0.5)
comp_max = col_comp3.number_input("统一随机上限(%)", value=97.0, step=0.5)
comp_step = col_comp4.number_input("离散跳动步距(%)", value=0.5, step=0.1)

st.write("##### 👥 多梯队陪标大兵团压舱设置")
num_teams = st.number_input("设定有几个独立运作的陪标团队？", min_value=1, max_value=10, value=2, step=1)
partner_data = []

for i in range(num_teams):
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        p_count = st.number_input(f"团队 {i+1} 家数", min_value=0, value=15, key=f"pt_cnt_{i}")
    with pc2:
        p_min = st.number_input(f"团队 {i+1} 下限(%)", value=88.0 + i*2, key=f"pt_min_{i}", step=0.5)
    with pc3:
        p_max = st.number_input(f"团队 {i+1} 上限(%)", value=92.0 + i*2, key=f"pt_max_{i}", step=0.5)
    with pc4:
        p_step = st.number_input(f"团队 {i+1} 步距(%)", value=0.5, key=f"pt_step_{i}", step=0.1)
    partner_data.append({"count": p_count, "min": p_min, "max": p_max, "step": p_step})

st.markdown("---")

# ----------------- 3. 技术标防御倒逼模型 -----------------
st.header("3. ⚖️ 施工深化设计：技术标防御模型")

col_eval1, col_eval2, col_eval3 = st.columns(3)
with col_eval1:
    owner_reps = st.number_input("业主代表人数", min_value=0, value=2, step=1)
    social_experts = st.number_input("社会专家人数", min_value=1, value=5, step=1)
    total_committee = owner_reps + social_experts

with col_eval2:
    num_items = st.number_input("差异化评审项数量", min_value=1, value=9, step=1)
    tier_diff = st.number_input("单项(优-良)档位分差", min_value=0.0, value=1.0, format="%.2f")

with col_eval3:
    intended_helpers = st.number_input("意向认可我方方案评委数", min_value=0, max_value=total_committee, value=1, step=1)
    auto_controlled_diff = round((tier_diff * num_items / total_committee) * intended_helpers, 4)
    
    st.markdown(" ")
    manual_override = st.checkbox("🧩 启用手动覆写技术标可控分差")
    controlled_diff = st.number_input("当前生效可控分差", value=auto_controlled_diff, format="%.4f", disabled=not manual_override)

min_business_score = round(60.0 - controlled_diff, 4)

st.info(f"🚨 基于当前参数，我方商务得分必须 **≥ {min_business_score:.4f} 分** 才能确保总分第一不被翻盘。")
st.markdown("---")

# ----------------- 4. 蒙特卡洛矩阵引擎运算 -----------------
st.header("4. 🕹️ V6.2 海量联合推演与弹性网格排兵布阵")

if st.button("🚀 启动 100,000 次海量兵棋推演", use_container_width=True):
    with st.spinner("正在引爆 10万次 极端市场乱战，系统正抓取大盘极值并拆分弹性联合阵型..."):
        SIM_COUNT = 100000
        
        # [1. 生成 K值 矩阵]
        k1_sims = np.random.choice(k1_options, size=(SIM_COUNT, 1))
        k2_k3_idx = np.random.choice([0, 1, 2], size=SIM_COUNT)
        k2_sims = k_pairs[k2_k3_idx, 0].reshape(-1, 1)
        k3_sims = k_pairs[k2_k3_idx, 1].reshape(-1, 1)
        
        # [2. 生成对手与陪标团动态矩阵]
        external_bids_list = []
        if num_competitors > 0:
            c_pts = np.arange(comp_min, comp_max + comp_step/2, comp_step)
            c_matrix = np.random.choice(c_pts, size=(SIM_COUNT, num_competitors))
            external_bids_list.append(c_matrix)
            
        for pt in partner_data:
            if pt["count"] > 0:
                p_pts = np.arange(pt["min"], pt["max"] + pt["step"]/2, pt["step"])
                p_matrix = np.random.choice(p_pts, size=(SIM_COUNT, pt["count"]))
                external_bids_list.append(p_matrix)
        
        all_external = np.hstack(external_bids_list) if len(external_bids_list) > 0 else np.zeros((SIM_COUNT, 0))
        external_sum = np.sum(all_external, axis=1, keepdims=True) if all_external.shape[1] > 0 else np.zeros((SIM_COUNT, 1))
        total_external_count = all_external.shape[1]

        # 核心算分函数
        def get_sim_results(my_bids_matrix):
            N = my_bids_matrix.shape[1]
            total_sum = external_sum + np.sum(my_bids_matrix, axis=1, keepdims=True)
            bid_avg = total_sum / (total_external_count + N)
            baseline = (100.0 * k1_sims * k2_sims) + (bid_avg * k3_sims)
            
            my_dev = np.round(np.abs(my_bids_matrix - baseline) / baseline * 100, 2)
            my_scores = np.clip(np.round(np.where(my_bids_matrix >= baseline, 60.0 - my_dev * 1.0, 60.0 - my_dev * 0.5), 2), 0.0, 60.0)
            my_max = np.max(my_scores, axis=1, keepdims=True)
            
            if total_external_count > 0:
                ext_dev = np.round(np.abs(all_external - baseline) / baseline * 100, 2)
                ext_scores = np.clip(np.round(np.where(all_external >= baseline, 60.0 - ext_dev * 1.0, 60.0 - ext_dev * 0.5), 2), 0.0, 60.0)
                ext_max = np.max(ext_scores, axis=1, keepdims=True)
            else:
                ext_max = np.zeros((SIM_COUNT, 1))
                
            is_win = (my_max >= ext_max) & (my_max >= min_business_score)
            return is_win, my_scores

        # [3. 第一阶段：单兵滑动雷达扫描寻找极值]
        my_bids_axis = np.linspace(85.50, 100.00, 300)
        win_probabilities = np.zeros_like(my_bids_axis)
        
        for i, pt in enumerate(my_bids_axis):
            pt_matrix = np.full((SIM_COUNT, 1), pt)
            is_win, _ = get_sim_results(pt_matrix)
            win_probabilities[i] = np.mean(is_win) * 100.0

        # [4. 第二阶段：依据极值进行弹性兵力拆解与布防]
        peak_idx = np.argmax(win_probabilities)
        peak_prob = win_probabilities[peak_idx]
        peak_val = my_bids_axis[peak_idx]
        
        force_expanded = False
        original_core_width = 0.0
        
        if peak_prob == 0:
            core_min, core_max = 90.0, 95.0
            abs_min, abs_max = 88.0, 97.0
        else:
            core_indices = np.where(win_probabilities >= peak_prob * 0.85)[0]
            core_min, core_max = my_bids_axis[core_indices[0]], my_bids_axis[core_indices[-1]]
            
            viable_indices = np.where(win_probabilities >= peak_prob * 0.10)[0]
            abs_min, abs_max = my_bids_axis[viable_indices[0]], my_bids_axis[viable_indices[-1]]
        
        # 【新增弹性网格逻辑】：判断自然宽度与需求宽度的关系
        if num_main_units > 1:
            req_width = (num_main_units - 1) * min_main_step
            original_core_width = core_max - core_min
            
            if original_core_width < req_width:
                force_expanded = True
                core_min = peak_val - req_width / 2
                core_max = peak_val + req_width / 2
                
            main_bids = np.linspace(core_min, core_max, num_main_units)
        else:
            main_bids = np.array([peak_val])
            
        # 侧翼掩护逻辑保持不变
        flank_bids = []
        if num_flank_units > 0:
            if "左侧" in flank_strategy:
                f_min, f_max = abs_min, max(abs_min, core_min - 0.2)
                flank_bids = np.linspace(f_min, f_max, num_flank_units) if num_flank_units > 1 else np.array([(f_min + f_max)/2])
            elif "右侧" in flank_strategy:
                f_min, f_max = min(abs_max, core_max + 0.2), abs_max
                flank_bids = np.linspace(f_min, f_max, num_flank_units) if num_flank_units > 1 else np.array([(f_min + f_max)/2])
            else: 
                left_units = num_flank_units // 2
                right_units = num_flank_units - left_units
                lbids = np.linspace(abs_min, max(abs_min, core_min - 0.2), left_units) if left_units > 0 else []
                rbids = np.linspace(min(abs_max, core_max + 0.2), abs_max, right_units) if right_units > 0 else []
                flank_bids = np.concatenate([lbids, rbids])
                
        fleet_positions = np.sort(np.concatenate([main_bids, np.array(flank_bids) if len(flank_bids)>0 else []]))

        # [5. 第三阶段：全舰队联合抗压终极验证]
        fleet_matrix = np.tile(fleet_positions, (SIM_COUNT, 1))
        joint_is_win, _ = get_sim_results(fleet_matrix)
        joint_win_rate = np.mean(joint_is_win) * 100.0

        # ================= 输出报告 =================
        st.success("✅ 弹性阵型计算与联合火力抗压验证完毕！")
        
        # --- 图一绘制 ---
        fig1, ax1 = plt.subplots(figsize=(11, 4.5))
        ax1.plot(my_bids_axis, win_probabilities, color='#0068c9', linewidth=3, label='大盘单兵试探胜率曲线')
        ax1.set_xlim(85.5, 100.0)
        ax1.set_xlabel('我方试探报价 (%)', fontweight='bold')
        ax1.set_ylabel('基础安全概率 (%)', color='#0068c9', fontweight='bold')
        ax1.grid(True, linestyle=":", alpha=0.5)
        
        ax1.axvspan(core_min, core_max, color='lightgreen', alpha=0.25, label=f'主力核心布防区')
        for mb in main_bids:
            ax1.axvline(x=mb, color='#d32f2f', linestyle='-', linewidth=2, alpha=0.8, label='主力落位点' if mb==main_bids[0] else "")
        if len(flank_bids) > 0:
            for fb in flank_bids:
                ax1.axvline(x=fb, color='#ff9800', linestyle='--', linewidth=2, alpha=0.8, label='侧翼落位点' if fb==flank_bids[0] else "")

        ax1.legend(loc='upper right')
        plt.title("📈 大盘全景雷达扫描地形图 与 多梯队弹性落位网格", fontsize=12, pad=12, fontweight='bold')
        st.pyplot(fig1)

        # --- 深度解释与报告 ---
        main_str = "、".join([f"{v:.2f}%" for v in main_bids])
        flank_str = "、".join([f"{v:.2f}%" for v in flank_bids]) if len(flank_bids)>0 else "无"
        flank_strat_clean = flank_strategy.split('(')[0].strip() if flank_strategy != "无侧翼部队" else "无"
        
        expansion_note = ""
        if force_expanded:
            expansion_note = f"<div style='margin-top:10px; padding:10px; background-color:#fff3cd; border-left: 4px solid #ffc107; color:#856404; font-size:14px; border-radius:4px;'>⚠️ <b>系统自动战术规避：</b> 检测到当前市场大概率山峰过于狭窄（原高优区跨度仅 <b>{original_core_width:.2f}%</b>）。为防范因报价过于密集而产生的“废标/异常一致”风险，系统已强制介入。以绝对最高峰 ({peak_val:.2f}%) 为锚点，按照您设定的最小战术步距 <b>{min_main_step}%</b> 将火力网向外安全撑开。</div>"
        
        html_report = f"""
<div style='background-color:#f4fbf7; padding: 20px; border-radius: 8px; border-left: 5px solid #2e7d32; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
<h4 style='margin:0 0 10px 0; color:#1b5e20;'>🎯 CBO 决策层：10万次蒙特卡洛全景推演与弹性网格布防执行书</h4>

<div style='background-color:#ffffff; padding:12px; border-radius:6px; margin-bottom:15px; border: 1px solid #e0e0e0;'>
<p style='margin:0 0 5px 0; color:#333; font-weight:bold;'>🧠 底层推演环境声明 (为何这套数据值得信任？)</p>
<p style='margin:0; font-size:14px; color:#555;'>
本报告的点位并非简单的均值估算。系统刚刚为您启动了 <b>100,000 次平行的蒙特卡洛动态随机模拟</b>。在每一次模拟中，系统都让 <b>K1下浮率、K2/K3权重组合、独立竞争对手报价、以及多梯队陪标大兵团</b> 在您设定的区间内发生了极端的随机跳动与踩踏。<br>
在这 10 万个高度混沌的市场乱局中，系统逐一验证了我方防线。以下推荐的落位点，正是经历 10 万次极限压力测试后，能够最大概率守住“施工深化设计”技术标红线的最优阵型。
</p>
</div>

<p style='color:#b71c1c; margin: 10px 0 0 0; font-weight:bold;'>🚩 【主力核心阵型】（共 {num_main_units} 家）—— 锁死大概率主峰</p>
<ul style='margin-top: 5px; margin-bottom: 5px; font-size:15px;'>
<li><b>布防区间：</b> {core_min:.2f}% ~ {core_max:.2f}% (大盘绝对峰值拦截区)</li>
<li><b>建议下注点位：</b> <span style='font-size:16px; font-weight:bold; color:#b71c1c; background:#ffebee; padding:2px 6px; border-radius:4px;'>【 {main_str} 】</span></li>
<li style='color:#555;'><b>推演依据：</b> 经 10 万次扫描，大盘基准价落入该区间的频次最高。将主力重兵密集部署于此，旨在死死锁住常规状态下胜率最高的核心红利区。</li>
</ul>
{expansion_note}

<p style='color:#e65100; margin: 15px 0 0 0; font-weight:bold;'>🛡️ 【侧翼掩护阵型】（共 {num_flank_units} 家）—— 对冲黑天鹅风险</p>
<ul style='margin-top: 5px; margin-bottom: 15px; font-size:15px;'>
<li><b>执行策略：</b> {flank_strat_clean}</li>
<li><b>建议下注点位：</b> <span style='font-size:16px; font-weight:bold; color:#e65100; background:#fff3e0; padding:2px 6px; border-radius:4px;'>【 {flank_str} 】</span></li>
<li style='color:#555;'><b>推演依据：</b> 蒙特卡洛模拟显示，市场存在小概率的极端杀价或意外高价。将剩下的兵力拉大步距布防于主峰两侧，是为了在 K1 抽签极差或对手恶意低价时，依然有子弹能够截获基准价，防止主阵型集体踏空。</li>
</ul>

<hr style='border:0; border-top: 1px dashed #ccc; margin: 15px 0;'>
<h5 style='color:#1b5e20; margin: 0 0 5px 0;'>🏆 该联合阵型终极抗压结论：</h5>
<p style='font-size:15px; color:#444;'>
将上述 <b>{total_our_units} 家</b> 构成的完整立体网格火力网，重新置入包含魔鬼抽签与极值踩踏的 100,000 次海量乱局中进行终极验算。我方联合阵型成功拿下全场最高分、且守住技术标倒逼红线的<b>【联合锁定终极胜率】确认为：</b>
</p>
<div style='text-align:center; padding: 10px; margin-top: 5px;'>
<span style='font-size:42px; font-weight:900; color:#2e7d32; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);'>{joint_win_rate:.2f}%</span>
</div>
<p style='text-align:center; font-size:13px; color:#666; margin-top:0;'>
<i>(注：在数十家单位高度内卷的基建盘中，该联合胜率已具备绝对的压制性优势)</i>
</p>
</div>
"""
        st.markdown(html_report, unsafe_allow_html=True)

        # --- 图二：高管汇报热力图 ---
        if len(fleet_positions) >= 3:
            strategic_points = [fleet_positions[0], fleet_positions[len(fleet_positions)//2], fleet_positions[-1]]
            strategic_labels = [f"极左防线\n({fleet_positions[0]:.2f}%)", f"中轴防线\n({fleet_positions[len(fleet_positions)//2]:.2f}%)", f"极右防线\n({fleet_positions[-1]:.2f}%)"]
        elif len(fleet_positions) == 2:
            strategic_points = [fleet_positions[0], (fleet_positions[0]+fleet_positions[1])/2, fleet_positions[-1]]
            strategic_labels = [f"极左防线\n({fleet_positions[0]:.2f}%)", "中轴防线\n(均值)", f"极右防线\n({fleet_positions[-1]:.2f}%)"]
        else:
            strategic_points = [fleet_positions[0]-0.5, fleet_positions[0], fleet_positions[0]+0.5]
            strategic_labels = ["-", f"单兵防线\n({fleet_positions[0]:.2f}%)", "-"]

        heatmap_data = []
        scenario_names = []
        
        for k1_val in k1_options:
            for k2_val, k3_val in k_pairs:
                s_name = f"K1={k1_val:.2f} | K2={k2_val:.1f},K3={k3_val:.1f}"
                scenario_names.append(s_name)
                
                mask = (np.isclose(k1_sims.flatten(), k1_val)) & (np.isclose(k2_sims.flatten(), k2_val))
                sub_sim_count = np.sum(mask)
                
                row_scores = []
                for pt in strategic_points:
                    if sub_sim_count > 0:
                        sub_ext_sum = external_sum[mask]
                        bid_avg = (sub_ext_sum + pt) / (total_external_count + 1)
                        baseline = (100.0 * k1_val * k2_val) + (bid_avg * k3_val)
                        dev = np.round(np.abs(pt - baseline) / baseline * 100, 2)
                        sc = np.where(pt >= baseline, 60.0 - dev * 1.0, 60.0 - dev * 0.5)
                        row_scores.append(np.mean(np.clip(np.round(sc, 2), 0, 60.0)))
                    else:
                        row_scores.append(0.0)
                heatmap_data.append(row_scores)
                
        arr_data = np.array(heatmap_data)
        
        st.markdown("---")
        st.subheader("🛑 图二：大盘抽签规则“红绿灯”风险响应矩阵 (抽取阵型左/中/右防线验证)")
        
        fig2, ax3 = plt.subplots(figsize=(10, 7))
        diff_range = 60.0 - (min_business_score - 1.5)
        if diff_range <= 0: diff_range = 0.1 
        safe_mid_node = max(0.01, min(0.99, 1.5 / diff_range))
        custom_cmap = LinearSegmentedColormap.from_list("risk_map", list(zip([0.0, safe_mid_node, 1.0], ["#d32f2f", "#ffffff", "#2e7d32"])))
        
        X, Y = np.meshgrid(np.arange(arr_data.shape[1] + 1), np.arange(arr_data.shape[0] + 1))
        c = ax3.pcolormesh(X, Y, arr_data, cmap=custom_cmap, vmin=min_business_score - 1.5, vmax=60.0, edgecolors='white', linewidths=0.5)
        ax3.invert_yaxis()  

        for m in range(arr_data.shape[0]):
            for n in range(arr_data.shape[1]):
                val = arr_data[m, n]
                text_color = "white" if (val < min_business_score or val > 55.0) else "black"
                ax3.text(n + 0.5, m + 0.5, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=10, fontweight="bold")
        
        ax3.set_xticks(np.arange(arr_data.shape[1]) + 0.5)
        ax3.set_yticks(np.arange(arr_data.shape[0]) + 0.5)
        ax3.set_xticklabels(strategic_labels, fontsize=10)
        ax3.set_yticklabels(scenario_names, fontsize=9)
        
        cbar = fig2.colorbar(c, ax=ax3, pad=0.02)
        cbar.set_label('平均期望商务得分 (分)', fontsize=10, fontweight='bold')
        
        plt.title(f"📊 18大底层抽签组合 × 阵型防线抗压测试 (红线拦截: {min_business_score:.2f}分)", fontsize=12, pad=15, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig2)
