"""只绘制已计算的损失切片，不执行训练或修改参数。"""
import numpy as np
import matplotlib.pyplot as plt


def plot_gradient_check(X, y, w0, grad, finite):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    loss0 = np.mean((X @ w0 - y) ** 2)
    h = 0.35  # 仅为看清两点；数值校验仍使用 notebook 中的 eps=1e-6。
    j = 1  # 只画 w[1]，w[0] 固定；数值代码仍检查两个分量。
    center = w0[j]
    grid = np.linspace(center - 0.8, center + 0.8, 200)
    candidates = np.tile(w0, (len(grid), 1))
    candidates[:, j] = grid
    losses = np.mean((X @ candidates.T - y[:, None]) ** 2, axis=0)
    points = np.tile(w0, (2, 1))
    points[:, j] = [center - h, center + h]
    heights = np.mean((X @ points.T - y[:, None]) ** 2, axis=0)
    slope = (heights[1] - heights[0]) / (2 * h)
    ax.plot(grid, losses, color="#4177b7", lw=2, label="损失曲线（另一参数固定）")
    ax.plot(grid, loss0 + grad[j] * (grid - center), "--",
            color="#23756c", label="中心点的切线：解析梯度")
    ax.plot(points[:, j], heights, "o-", color="#a14a22",
            label="左右两点的割线：中心差分")
    ax.scatter([center], [loss0], color="#23756c", zorder=4)
    ax.plot([center-h, center+h, center+h],
            [heights[0], heights[0], heights[1]], ":", color="#8194aa")
    ax.annotate("横向间隔 2h", (center, heights[0]),
                xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
    for value, height, label in zip(points[:, j], heights, ["左点", "右点"]):
        ax.annotate(label, (value, height), xytext=(7, 9),
                    textcoords="offset points", fontsize=9)
    ax.set(title="只改变一个参数，观察损失变化（固定 w[0]）",
           xlabel="参数值 w[1]", ylabel="训练 MSE")
    ax.text(0.03, 0.04,
            f"解析梯度 = {grad[j]:.6f}\n数值差分 = {finite[j]:.6f}",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(facecolor="white", edgecolor="#d5dfe9", alpha=0.95))
    ax.grid(alpha=0.15)
    ax.legend(fontsize=8, loc="upper right")
    assert np.isclose(slope, grad[j])  # 本例二次损失的中心差分在精确算术下恰好等于导数。
    fig.suptitle("中心差分：左右损失之差 ÷ 参数间隔，近似当前方向的斜率", fontsize=13)
    fig.tight_layout()
    plt.show()
