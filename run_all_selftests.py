import sys, subprocess, platform, datetime
from pathlib import Path

SERVICES = [
    ("auth_service", "Auth"),
    ("catalog_service", "Catalog"),
    ("cart_service", "Cart"),
    ("order_service", "Order"),
]

def _pkg_versions():
    vers = {}
    try:
        import fastapi; vers["fastapi"] = fastapi.__version__
    except Exception: pass
    try:
        import sqlalchemy; vers["sqlalchemy"] = sqlalchemy.__version__
    except Exception: pass
    try:
        import pydantic; vers["pydantic"] = pydantic.__version__
    except Exception: pass
    try:
        import passlib; vers["passlib"] = passlib.__version__
    except Exception: pass
    try:
        import httpx; vers["httpx"] = httpx.__version__
    except Exception: pass
    return vers

def main():
    root = Path(__file__).resolve().parent
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)
    report_path = docs_dir / "tests-summary.txt"

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = []
    header.append(f"Self-tests report — {ts}")
    header.append(f"Python {sys.version.split()[0]} on {platform.system()} {platform.release()}")
    vers = _pkg_versions()
    if vers:
        header.append("Package versions: " + ", ".join(f"{k}={v}" for k, v in vers.items()))
    header.append("-" * 80)
    header_text = "\n".join(header) + "\n"

    print(header_text, end="")
    report_lines = [header_text]

    overall_ok = True
    results = []

    for folder, label in SERVICES:
        svc_path = root / "services" / folder
        title = f"=== {label} ({folder}) ==="
        print(title)
        report_lines.append(title + "\n")

        script = svc_path / "run_selftest.py"
        if not script.exists():
            msg = f"[SKIP] {script} no existe\n"
            print(msg.strip())
            report_lines.append(msg + "\n")
            results.append((label, "SKIP"))
            continue

        cp = subprocess.run([sys.executable, "run_selftest.py"], cwd=svc_path, capture_output=True, text=True)
        out = (cp.stdout or "") + (("\n" + cp.stderr) if cp.stderr else "")
        print(out, end="" if out.endswith("\n") else "\n")
        report_lines.append(out + "\n")

        status = "PASS" if cp.returncode == 0 else "FAIL"
        results.append((label, status))
        overall_ok &= (cp.returncode == 0)
        report_lines.append("\n")

    summary = "Summary: " + ", ".join(f"{label}={status}" for label, status in results) + "\n"
    sep = "-" * 80 + "\n"
    print(sep + summary, end="")
    report_lines.append(sep + summary)

    report_path.write_text("".join(report_lines), encoding="utf-8")
    print(f"Reporte guardado en {report_path}")
    sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()