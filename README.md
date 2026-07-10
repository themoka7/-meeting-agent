# 회의록 자동화 에이전트

녹취록 → 회의록 작성 → 팀원 메일 발송을 자동화하는 에이전트.

## 빠른 시작

1. **자격증명 설정** — `.env` 의 `SMTP_USER`(발신 Gmail), `SMTP_APP_PASSWORD`(앱 비밀번호 16자리)를 채운다.
   - 앱 비밀번호 발급: 2단계 인증 켠 뒤 https://myaccount.google.com/apppasswords
2. **수신자 설정** — `config/recipients.yaml` 에 팀원 이메일을 채운다.
3. **녹취록 투입** — `transcripts/` 에 `.txt`/`.pdf` 를 넣는다.
4. **회의록 작성** — 에이전트가 `skills/meeting-minutes` 규칙대로 작성해 `outputs/<날짜>/` 에 저장.
5. **발송**
   - 본인 테스트: `python scripts/send_email.py --subject "제목" --body-file outputs/<날짜>/회의록.md --test`
   - 팀원 발송: 위 명령에서 `--test` 를 `--real` 로, 필요 시 `--attach ...docx` 추가.

## 폴더 구조
```
.
├── CLAUDE.md                   # 에이전트 동작 규칙
├── README.md
├── .env.example                # SMTP 자격증명 템플릿 (복사해 .env 로)
├── skills/meeting-minutes/     # 회의록 작성 규칙·양식
├── scripts/                    # run_pipeline / send_email / md_to_docx / read_transcript
├── config/recipients.example.yaml  # 수신자 템플릿 (복사해 recipients.yaml 로)
├── docs/                       # 기획서 등 문서
├── transcripts/                # 입력 녹취록 (git 제외)
└── outputs/YYYY-MM-DD/          # 산출물 (git 제외)
```

> 처음 사용 시: `.env.example` → `.env`, `config/recipients.example.yaml` → `config/recipients.yaml` 로 복사한 뒤 실제 값을 채우세요.

## 안전장치
- 최초 발송은 반드시 본인(`test_recipient`)으로 테스트 → 확인 후 팀원 발송.
- `.env` 와 `outputs/`, `transcripts/` 는 `.gitignore` 로 제외.
