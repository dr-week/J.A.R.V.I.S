"""Fast consistency gate for backend OSS adapters and their documentation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    ROOT / "docs/dev/BACKEND_OSS_PLAN.md",
    ROOT / "docs/OSS.md",
    ROOT / "backend/plugins/http_resilience/__init__.py",
    ROOT / "backend/plugins/scheduler/__init__.py",
    ROOT / "backend/tests/test_backend_oss_adapters.py",
)


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing backend OSS artifacts:")
        print("\n".join(missing))
        return 1
    print(f"Backend OSS gate passed ({len(REQUIRED)} artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
