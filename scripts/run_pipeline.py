#!/usr/bin/env python3
"""회의록(md) → docx 변환 → 메일 발송을 한 번에 실행한다.

전제: 에이전트가 CLAUDE.md 규칙대로 녹취록을 읽어 회의록 md 를 이미
      outputs/<날짜>/ 에 작성해 둔 상태.

사용:
  # 본인 테스트 발송
  python scripts/run_pipeline.py --minute outputs/2026-07-10/회의록_xxx.md --test

  # 실제 팀원 발송 (recipients.yaml 의 teams.default)
  python scripts/run_pipeline.py --minute outputs/2026-07-10/회의록_xxx.md --real
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def derive_subject(md_path):
    text = Path(md_path).read_text(encoding="utf-8")
    m = re.search(r"#\s*회의록\s*[—-]\s*(.+)", text)
    name = m.group(1).strip() if m else Path(md_path).stem
    d = re.search(r"일시\s*\|\s*([0-9.\s]+)", text)
    date = d.group(1).strip() if d else ""
    return f"[회의록] {name}" + (f" ({date})" if date else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minute", required=True, help="회의록 md 경로")
    ap.add_argument("--subject", help="메일 제목 (미지정 시 회의록 제목에서 자동 생성)")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--test", action="store_true", help="본인에게만 발송")
    grp.add_argument("--real", action="store_true", help="팀원 전체 발송")
    ap.add_argument("--team", default="default")
    ap.add_argument("--no-docx", action="store_true", help="docx 첨부 생략(md 본문만)")
    args = ap.parse_args()

    md = Path(args.minute)
    if not md.exists():
        sys.exit(f"[오류] 회의록 파일이 없습니다: {md}")

    subject = args.subject or derive_subject(md)

    # 1) docx 변환
    attach_args = []
    if not args.no_docx:
        docx_path = md.with_suffix(".docx")
        print(f"[1/2] docx 변환 → {docx_path.name}")
        r = subprocess.run([PY, str(ROOT / "scripts" / "md_to_docx.py"),
                            str(md), str(docx_path)])
        if r.returncode != 0:
            sys.exit("[오류] docx 변환 실패")
        attach_args = ["--attach", str(docx_path)]

    # 2) 발송
    mode = "--test" if args.test else "--real"
    print(f"[2/2] 메일 발송 ({mode})")
    cmd = [PY, str(ROOT / "scripts" / "send_email.py"),
           "--subject", subject, "--body-file", str(md), mode,
           "--team", args.team] + attach_args
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("[오류] 메일 발송 실패")
    print("[완료] 파이프라인 종료")


if __name__ == "__main__":
    main()
