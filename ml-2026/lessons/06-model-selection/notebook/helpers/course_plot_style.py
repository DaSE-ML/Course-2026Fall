"""第6讲中文绘图字体：按真实字体族选择，局部生效，缺字时不静默回退。"""
from functools import wraps

import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font


def course_font_settings():
    """返回已安装且覆盖常用中文/数学符号的字体配置。"""
    installed = {entry.name for entry in font_manager.fontManager.ttflist}
    for family in ["PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC",
                   "Heiti SC", "Arial Unicode MS"]:
        if family not in installed:
            continue
        path = font_manager.findfont(font_manager.FontProperties(family=family),
                                     fallback_to_default=False)
        font = ft2font.FT2Font(path)
        if all(font.get_char_index(ord(char)) for char in "训练验证概率误差样本α²−"):
            return {"font.family": [family], "font.style": "normal", "font.weight": "normal",
                    "axes.titleweight": "normal", "axes.labelweight": "normal",
                    "font.size": 17, "axes.unicode_minus": False,
                    "mathtext.fontset": "stix", "text.usetex": False,
                    "svg.fonttype": "path", "savefig.dpi": 300}
    raise RuntimeError("缺少可用的中文绘图字体，请安装 Noto Sans CJK SC 后重新运行。")


def chinese_plot(function):
    """隔离绘图设置，避免导入helper时污染后续图表。"""
    @wraps(function)
    def wrapped(*args, **kwargs):
        with plt.rc_context(course_font_settings()):
            return function(*args, **kwargs)
    return wrapped
