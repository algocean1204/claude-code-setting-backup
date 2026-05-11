"""공통 픽스처 — 테스트 대상 모듈을 sys.path에 등록한다."""
from __future__ import annotations

import sys
from pathlib import Path

# bin/ 디렉터리를 import 경로에 추가
BIN_DIR = Path(__file__).resolve().parent.parent / "bin"
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))
