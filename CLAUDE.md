# 회의록 자동화 에이전트

녹취록을 입력받아 회의록을 작성하고, 지정된 팀원에게 메일로 자동 발송하는 에이전트다.

## 작업 절차 (반드시 이 순서로)

1. **녹취록 읽기** — `transcripts/` 의 파일을 읽는다.
   - `.txt` 는 그대로, `.pdf` 는 `python scripts/read_transcript.py <파일>` 로 텍스트화한다.
2. **회의록 작성** — `skills/meeting-minutes/SKILL.md` 규칙과 `template.md` 양식에 따라 작성한다.
3. **저장** — 실행일 기준 `outputs/YYYY-MM-DD/` 폴더를 만들고 아래를 저장한다.
   - `회의록_<회의명>.md` (원본)
   - `회의록_<회의명>.docx` (배포용 — `ddokham-meeting-minute` 스킬로 변환)
4. **발송** — `config/recipients.yaml` 의 수신자에게 `scripts/send_email.py` 로 발송한다.
   - **최초 발송은 반드시 `test_recipient`(본인)로만 테스트**한다.
   - 사용자가 수신을 확인한 뒤에만 `teams` 의 실제 팀원 전체에게 발송한다.

## 규칙

- 녹취록에 **없는 내용을 지어내지 않는다.** 모든 항목은 녹취록 근거만 사용한다.
- **결정사항**과 **할 일**은 담당자·기한을 반드시 명시한다. 불명확하면 `(미정)` 으로 표기한다.
- 발송 전 **수신자·제목·본문·첨부**를 사용자에게 요약 보고하고 승인받는다.
- SMTP 자격증명(`.env`)은 코드 밖으로 절대 출력하지 않는다. 로그·회의록·채팅에 노출 금지.
- 회의록 파일명·폴더명은 공백 대신 `_` 를 쓴다.

## 통합 실행 (원클릭)

녹취록을 읽어 회의록 md 를 `outputs/<날짜>/` 에 작성한 뒤, 아래 한 줄로 docx 변환 + 발송을 실행한다.

```
# 본인 테스트 발송
python scripts/run_pipeline.py --minute outputs/<날짜>/회의록_<회의명>.md --test

# 실제 팀원 전체 발송
python scripts/run_pipeline.py --minute outputs/<날짜>/회의록_<회의명>.md --real
```

- 제목은 회의록 제목에서 자동 생성(`--subject` 로 덮어쓰기 가능).
- 회의록 *작성*은 스크립트가 아니라 에이전트가 `skills/meeting-minutes` 규칙대로 수행한다.

## 폴더 구조

```
.
├── CLAUDE.md              # 이 파일
├── .env                   # SMTP 자격증명 (공유 금지, git 제외)
├── skills/meeting-minutes/ # 회의록 작성 규칙·양식
├── scripts/               # send_email.py, read_transcript.py, md_to_docx.py, run_pipeline.py
├── config/recipients.yaml # 수신자 목록 (git 제외, example 만 커밋)
├── docs/                  # 기획서 등 문서
├── transcripts/           # 입력 녹취록 (git 제외)
└── outputs/YYYY-MM-DD/     # 산출물 (회의록·발송로그, git 제외)
```
