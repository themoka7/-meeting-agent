#!/usr/bin/env python3
"""녹취록 파일을 읽어 텍스트로 반환/출력한다. .txt 와 .pdf 를 지원.

사용: python scripts/read_transcript.py transcripts/파일.pdf
.pdf 는 pypdf 필요 (pip install pypdf).
"""
import sys
from pathlib import Path


def read_transcript(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    if p.suffix.lower() == ".txt":
        return p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            sys.exit("[오류] pdf 처리에는 pypdf 가 필요합니다: pip install pypdf")
        reader = PdfReader(str(p))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"지원하지 않는 형식: {p.suffix}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("사용: python scripts/read_transcript.py <파일>")
    print(read_transcript(sys.argv[1]))
