# 谷神星丢失与重现时间线（第 3 讲谷神星故事页配图）
# 合成示意图：仅含历史事件标注，无实验数据
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.dates import date2num
from datetime import date

plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Hiragino Sans GB', 'Heiti TC', 'STHeiti',
                                   'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
BLUE, ORANGE, GREEN, GRAY = '#4177b7', '#a14a22', '#23756c', '#8194aa'

fig, ax = plt.subplots(figsize=(12.4, 4.6), dpi=200)

d = lambda y, m, dd: date2num(date(y, m, dd))
# 区间带
ax.axvspan(d(1801, 1, 1), d(1801, 2, 11), color=BLUE, alpha=.14)
ax.axvspan(d(1801, 2, 11), d(1801, 12, 7), color=GRAY, alpha=.12)
# 主轴线
ax.axhline(0, color='#52657a', lw=1.4, zorder=1)

events = [
    (d(1801, 1, 1),  0.62, BLUE,   '1 月 1 日\n皮亚齐发现谷神星（巴勒莫）'),
    (d(1801, 2, 11), 1.12, BLUE,   '2 月 11 日：第 24 次观测后因病中断\n（此后隐入太阳眩光）'),
    (d(1801, 12, 7), -0.78, ORANGE, '12 月 7 日：察赫首次见到候选'),
    (d(1801, 12, 31), 0.62, GREEN, '12 月 31 日\n察赫与奥伯斯在预测位置\n附近确认重现'),
]
for x, y, c, label in events:
    ax.plot([x], [0], 'o', color=c, ms=9, zorder=3)
    halign = 'right' if x == d(1801, 12, 7) else 'center'
    ax.annotate(label, (x, 0), xytext=(x - (12 if halign == 'right' else 0), y + 0.28), ha=halign, fontsize=10.5,
                color='#192b41', arrowprops=dict(arrowstyle='-', color=c, lw=1.1))

ax.annotate('', xy=(d(1801, 2, 3), -0.42), xytext=(d(1801, 1, 3), -0.42),
            arrowprops=dict(arrowstyle='<->', color=BLUE, lw=1.3))
ax.text(d(1801, 2, 5), -0.56, '24 次观测，共约 40 天', ha='center', fontsize=11, color=BLUE)
ax.annotate('', xy=(d(1801, 11, 20), -0.42), xytext=(d(1801, 3, 1), -0.42),
            arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1.3))
ax.text(d(1801, 6, 10), -0.56, '消失约 10 个月：全欧洲“天体警察”按原轨道搜索无果', ha='center', fontsize=11, color='#52657a')
ax.text(d(1801, 8, 1), 1.16, '高斯数周内算出新轨道，11 月寄出预测表', ha='center', fontsize=11, color=GREEN,
        bbox=dict(boxstyle='round,pad=0.35', fc='#f1f8f6', ec=GREEN, lw=1))

ax.set_xlim(d(1800, 12, 20), d(1802, 1, 20))
ax.set_ylim(-1.15, 1.55)
ax.set_yticks([])
ticks = [date(1801, m, 1) for m in [1, 3, 5, 7, 9, 11]] + [date(1802, 1, 1)]
ax.set_xticks([date2num(t) for t in ticks])
ax.set_xticklabels(['1801-01', '03', '05', '07', '09', '11', '1802-01'], fontsize=10.5)
for sp in ['top', 'right', 'left']:
    ax.spines[sp].set_visible(False)
ax.set_title('谷神星的丢失与重现（1801）', fontsize=14, color='#174b87', pad=12)
plt.tight_layout()
plt.savefig('ch3-ceres-timeline.png', bbox_inches='tight', facecolor='white')
print('saved ch3-ceres-timeline.png')
