from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import shutil
import zipfile
import pandas as pd

def prepare_credit_csv(cache_dir, data_dirs):
    """Reuse an existing CSV, convert XLS/ZIP, or fetch the pinned UCI source."""
    cache_dir = Path(cache_dir)
    csv_name = "default of credit card clients.csv"
    xls_name = "default of credit card clients.xls"
    data_path = next((p / csv_name for p in data_dirs if (p / csv_name).exists()), None)
    if data_path is None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        xls_path = next((p / xls_name for p in data_dirs if (p / xls_name).exists()), None)
        zip_names = ["default-credit-card-clients.zip", "default+of+credit+card+clients.zip"]
        zip_path = next((p / name for p in data_dirs for name in zip_names
                         if (p / name).exists()), None)
        if xls_path is None and zip_path is not None:
            xls_path = cache_dir / xls_name
            # 只取指定数据文件，不执行下载内容，也不解压其他路径。
            with zipfile.ZipFile(zip_path) as archive:
                with archive.open(xls_name) as source, xls_path.open("wb") as out:
                    shutil.copyfileobj(source, out)
        if xls_path is not None:
            # xlrd 仅用于旧版 .xls；独立上传 Notebook 时也自动补齐。
            import importlib.util, subprocess, sys
            if importlib.util.find_spec("xlrd") is None:
                print("转换 XLS：安装 xlrd==2.0.2 到当前内核……", flush=True)
                subprocess.run([sys.executable, "-m", "pip", "install", "xlrd==2.0.2"], check=True)
            raw = pd.read_excel(xls_path, header=None, engine="xlrd")
        else:
            # UCI 官方 API 指向这个较小的 CSV，避免下载 5.3 MB 的 XLS。
            source_path = next((p / name for p in data_dirs for name in ["uci350-source.csv", "data.csv"]
                                if (p / name).exists()), cache_dir / "uci350-source.csv")
            if not source_path.exists():
                url = "https://archive.ics.uci.edu/static/public/350/data.csv"
                partial = source_path.with_suffix(".csv.partial")
                print("首次准备：从 UCI 自动下载信用卡数据（约 2.8 MB）……", flush=True)
                try:
                    with urlopen(Request(url, headers={"User-Agent": "ML-course-notebook"}), timeout=60) as response, partial.open("wb") as out:
                        shutil.copyfileobj(response, out)
                    if hashlib.sha256(partial.read_bytes()).hexdigest() != "45bcf4df62ff2e237a74eb155cabfb4bbbc171219a0637daef44fdad07503dd0":
                        raise ValueError("UCI 文件校验不一致，请联系教师核查来源版本。")
                    partial.replace(source_path)
                except Exception as exc:
                    partial.unlink(missing_ok=True)
                    raise RuntimeError("自动下载未完成，请检查网络后重跑本格；已有 CSV/XLS/ZIP 会自动复用。") from exc
            official = pd.read_csv(source_path)
            # 检查官方原始表的行数和列数。
            assert official.shape == (30000, 25)
            original_names = ["", *[f"X{i}" for i in range(1, 24)], "Y"]
            standard_names = ["ID", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
                              "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
                              *[f"BILL_AMT{i}" for i in range(1, 7)],
                              *[f"PAY_AMT{i}" for i in range(1, 7)], "default payment next month"]
            # 检查表头与官方数据格式一致。
            assert list(official.columns) == ["ID", *original_names[1:]]
            # 转换成课程的两行表头；不排序、不删样本、不改数值。
            raw = pd.concat([pd.DataFrame([original_names, standard_names]),
                             pd.DataFrame(official.to_numpy())], ignore_index=True)
        data_path = cache_dir / csv_name
        partial_csv = data_path.with_suffix(".csv.partial")
        raw.to_csv(partial_csv, index=False, header=False, encoding="utf-8")
        converted = pd.read_csv(partial_csv, header=1, index_col=0)
        if converted.shape != (30000, 24) or "default payment next month" not in converted:
            partial_csv.unlink(missing_ok=True)
            raise ValueError("数据形状或表头不符合 UCI 350，请联系教师核查。")
        partial_csv.replace(data_path)
        print("已自动转换并缓存 CSV；下次无需联网。")
    else:
        print("复用已有 CSV：", data_path)
    return data_path
