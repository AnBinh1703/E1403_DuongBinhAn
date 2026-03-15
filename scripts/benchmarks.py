import argparse
import logging
import time
from pathlib import Path

import dask.dataframe as dd
import matplotlib.pyplot as plt
import pandas as pd
import psutil


def setup():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "data" / "heart_statlog_cleveland_hungary_final.csv"
    outputs = root / "outputs"
    figures = outputs / "figures"
    tables = outputs / "tables"
    logs = outputs / "logs"
    tmp = outputs / "tmp"
    for folder in [outputs, figures, tables, logs, tmp]:
        folder.mkdir(parents=True, exist_ok=True)
    return root, data_file, outputs, figures, tables, logs, tmp


def logger_at(path: Path):
    lg = logging.getLogger("bench")
    lg.handlers.clear()
    lg.setLevel(logging.INFO)
    fh = logging.FileHandler(path, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    lg.addHandler(fh)
    lg.addHandler(logging.StreamHandler())
    return lg


def sample_resource():
    return psutil.cpu_percent(interval=0.2), psutil.virtual_memory().percent


def make_scaled(df: pd.DataFrame, n_rows: int):
    repeats = max(1, (n_rows // len(df)) + (1 if n_rows % len(df) else 0))
    return pd.concat([df] * repeats, ignore_index=True).head(n_rows)


def run_single(df: pd.DataFrame, size: int, tmp_root: Path):
    data = make_scaled(df, size)
    partitions = max(1, size // 5000)
    chunk = len(data) // partitions
    temp_dir = tmp_root / f"size_{size}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for index in range(partitions):
        start = index * chunk
        end = len(data) if index == partitions - 1 else (index + 1) * chunk
        data.iloc[start:end].to_csv(temp_dir / f"part_{index:04d}.csv", index=False)

    cpu0, mem0 = sample_resource()
    start = time.time()
    _ = data.describe(include="all")
    _ = data.groupby("sex").mean(numeric_only=True)
    pandas_time = time.time() - start
    cpu1, mem1 = sample_resource()

    start = time.time()
    ddf = dd.read_csv(str(temp_dir / "part_*.csv"))
    _ = ddf.describe().compute()
    _ = ddf.groupby("sex").mean(numeric_only=True).compute()
    dask_time = time.time() - start
    cpu2, mem2 = sample_resource()

    for csv_file in temp_dir.glob("part_*.csv"):
        csv_file.unlink(missing_ok=True)

    return {
        "rows": size,
        "partitions": partitions,
        "pandas_time_s": round(pandas_time, 4),
        "dask_time_s": round(dask_time, 4),
        "speedup_pandas_over_dask": round(pandas_time / dask_time, 4) if dask_time > 0 else None,
        "cpu_before": cpu0,
        "mem_before": mem0,
        "cpu_after_pandas": cpu1,
        "mem_after_pandas": mem1,
        "cpu_after_dask": cpu2,
        "mem_after_dask": mem2,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[10000, 100000, 500000])
    args = parser.parse_args()

    _, data_file, outputs, figures, tables, logs, tmp = setup()
    log = logger_at(logs / "benchmarks.log")

    if not data_file.exists():
        raise FileNotFoundError(f"Dataset not found: {data_file}")

    raw = pd.read_csv(data_file)
    log.info("Loaded data shape=%s", raw.shape)

    rows = []
    for size in args.sizes:
        log.info("Running size=%s", size)
        result = run_single(raw, size, tmp)
        log.info("Result=%s", result)
        rows.append(result)

    benchmark = pd.DataFrame(rows)
    benchmark.to_csv(outputs / "benchmark_results.csv", index=False)
    benchmark.to_csv(tables / "benchmark_results.csv", index=False)
    benchmark.to_json(outputs / "benchmark_results.json", orient="records", indent=2)

    plt.figure(figsize=(8, 4))
    plt.plot(benchmark["rows"], benchmark["pandas_time_s"], marker="o", label="Pandas")
    plt.plot(benchmark["rows"], benchmark["dask_time_s"], marker="o", label="Dask")
    plt.xlabel("Rows")
    plt.ylabel("Time (s)")
    plt.title("Pandas vs Dask Runtime")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "benchmark_pandas_vs_dask.png", dpi=200)

    plt.figure(figsize=(8, 4))
    plt.plot(benchmark["rows"], benchmark["cpu_after_pandas"], marker="o", label="CPU% Pandas")
    plt.plot(benchmark["rows"], benchmark["cpu_after_dask"], marker="o", label="CPU% Dask")
    plt.plot(benchmark["rows"], benchmark["mem_after_pandas"], marker="o", label="MEM% Pandas")
    plt.plot(benchmark["rows"], benchmark["mem_after_dask"], marker="o", label="MEM% Dask")
    plt.xlabel("Rows")
    plt.ylabel("Resource %")
    plt.title("Benchmark Resource Usage")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "benchmark_resources.png", dpi=200)

    log.info("Completed benchmark generation")


if __name__ == "__main__":
    main()
