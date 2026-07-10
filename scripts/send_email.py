#!/usr/bin/env python3
"""Gmail SMTP 로 회의록 메일을 발송한다.

사용 예:
  # 본인 테스트 발송 (recipients.yaml 의 test_recipient 로)
  python scripts/send_email.py --subject "회의록" --body-file outputs/2026-07-10/회의록.md --test

  # 실제 팀원 전체 발송 (teams.default)
  python scripts/send_email.py --subject "회의록" --body-file outputs/2026-07-10/회의록.md --real \
      --attach outputs/2026-07-10/회의록.docx
"""
import argparse
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env(path=ROOT / ".env"):
    """아주 단순한 .env 파서 (KEY=VALUE)."""
    env = {}
    if not path.exists():
        sys.exit(f"[오류] .env 파일이 없습니다: {path}")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def load_recipients(path=ROOT / "config" / "recipients.yaml"):
    """의존성 없이 recipients.yaml 을 읽는 최소 파서."""
    test_recipient = None
    teams = {}
    current_team = None
    pending_name = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        s = raw.strip()
        if s.startswith("test_recipient:"):
            test_recipient = s.split(":", 1)[1].strip()
        elif s == "teams:":
            current_team = None
        elif indent == 2 and s.endswith(":"):
            current_team = s[:-1].strip()
            teams[current_team] = []
        elif s.startswith("- name:"):
            pending_name = s.split(":", 1)[1].strip()
        elif s.startswith("email:"):
            email = s.split(":", 1)[1].strip()
            if current_team is not None:
                teams[current_team].append({"name": pending_name, "email": email})
    return test_recipient, teams


def build_message(env, to_list, subject, body, attach=None):
    msg = EmailMessage()
    sender_name = env.get("SENDER_NAME", "회의록 자동화")
    msg["From"] = f"{sender_name} <{env['SMTP_USER']}>"
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    msg.set_content(body)
    if attach:
        p = Path(attach)
        data = p.read_bytes()
        # docx MIME
        msg.add_attachment(
            data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=p.name,
        )
    return msg


def send(env, msg):
    port = int(env.get("SMTP_PORT", "587"))
    host = env.get("SMTP_HOST", "smtp.gmail.com")
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        # 앱 비밀번호는 공백이 있어도 되지만 제거해도 무방
        server.login(env["SMTP_USER"], env["SMTP_APP_PASSWORD"].replace(" ", ""))
        server.send_message(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", help="본문으로 쓸 텍스트/마크다운 파일")
    ap.add_argument("--body", help="본문 문자열 (body-file 대신)")
    ap.add_argument("--attach", help="첨부 파일 경로 (예: .docx)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--test", action="store_true", help="본인(test_recipient)에게만 발송")
    group.add_argument("--real", action="store_true", help="teams 실제 팀원에게 발송")
    ap.add_argument("--team", default="default", help="real 발송 시 대상 팀 (기본 default)")
    args = ap.parse_args()

    env = load_env()
    for key in ("SMTP_USER", "SMTP_APP_PASSWORD"):
        if not env.get(key) or env[key].startswith("여기에"):
            sys.exit(f"[오류] .env 의 {key} 를 실제 값으로 채워주세요.")

    test_recipient, teams = load_recipients()

    if args.test:
        to_list = [test_recipient]
    else:
        members = teams.get(args.team, [])
        to_list = [m["email"] for m in members]
        bad = [m for m in members if "여기에" in m["email"] or "example.com" in m["email"]]
        if bad or not to_list:
            sys.exit("[오류] recipients.yaml 의 팀원 이메일을 실제 값으로 채워주세요.")

    body = args.body or (Path(args.body_file).read_text(encoding="utf-8") if args.body_file else "")

    msg = build_message(env, to_list, args.subject, body, args.attach)
    print(f"발송 대상: {to_list}")
    send(env, msg)
    print("[성공] 메일 발송 완료")


if __name__ == "__main__":
    main()
