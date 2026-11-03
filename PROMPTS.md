# 단계별 개발 프롬프트

각 단계의 프롬프트를 순서대로 Claude Code에 붙여넣어 사용하세요. 모든 프롬프트는 `PRD.md`를 기준으로 합니다.

---

## 1단계: 기본 뼈대 작성

```
PRD.md를 읽고, 번역기 앱의 기본 뼈대만 먼저 만들어줘. 이 단계에서는 번역 기능은 구현하지 마.

만들 것:
1. 프로젝트 구조 (PRD 7.4 기준)
   - app.py
   - requirements.txt (streamlit, openai, python-dotenv)
   - .env.example (OPENAI_API_KEY, OPENAI_MODEL=gpt-6-astra)
   - .gitignore (.env, __pycache__, .venv 포함)
2. app.py 뼈대
   - load_dotenv()로 환경 변수 로드하는 부분
   - 언어 딕셔너리 {"영어": "English", "일본어": "Japanese", "베트남어": "Vietnamese"}
   - 페이지 제목, 여러 줄 텍스트 입력창(st.text_area)
   - 영어/일본어/베트남어 버튼 3개 (한 줄에 나란히)
   - 결과 표시 영역 (지금은 버튼을 누르면 "번역 기능 준비 중" 정도의 자리표시자만 보여줘)
3. translate(text, target_language) 함수의 빈 껍데기(시그니처와 docstring만, 본문은 NotImplementedError 또는 TODO)

완료 후:
- pip install -r requirements.txt 와 streamlit run app.py 로 앱이 에러 없이 뜨는지 확인해줘.
- 만든 파일 목록과 실행 방법을 간단히 요약해줘.
```

---

## 2단계: 주요 기능 추가

```
PRD.md의 기능 요구사항 F1~F8과 예외 처리(9장)를 기준으로 app.py에 번역 기능을 구현해줘.

구현할 것:
1. translate() 함수 구현
   - .env의 OPENAI_API_KEY, OPENAI_MODEL(기본값 gpt-6-astra)을 사용해 OpenAI API 호출
   - 시스템 프롬프트: "You are a professional translator. Translate the user's text into {target_language}. Output only the translated text, with no explanations or quotes. Preserve line breaks and tone."
   - temperature는 0.2
2. 버튼 클릭 동작
   - 버튼 클릭 시 입력 문장을 해당 언어로 번역해 결과 영역에 표시
   - 번역 중 st.spinner 표시
   - 번역 결과는 st.session_state에 저장해 화면이 다시 그려져도 유지
   - 결과에 어떤 언어로 번역했는지 라벨 표시 (예: "번역 결과 (English)")
3. 검증과 예외 처리
   - 입력이 비어 있으면 st.warning("번역할 글을 입력해 주세요.") 표시, API 호출 안 함
   - OPENAI_API_KEY가 없으면 .env 설정 안내 st.error 표시 후 중단
   - 모델명 오류, 네트워크 오류, 레이트 리밋 등 API 예외를 구분해 사용자 친화적 메시지로 표시 (앱이 죽으면 안 됨, API 키는 화면과 로그에 노출 금지)
   - 입력 글자 수 제한 5,000자 및 초과 시 안내
4. 결과 복사가 쉽도록 st.code 등으로 표시 (선택 기능 F7)

완료 후:
- 가짜 키/빈 입력/긴 입력 등 에러 경로를 직접 실행해서 확인해줘.
- 실제 API 키가 없으면 정상 번역 경로는 openai 호출을 모킹해서 테스트하고, 그렇게 했다고 알려줘.
- 변경 사항을 요약해줘.
```

---

## 3단계: UI 디자인

```
frontend-design 스킬을 참고해서, 동작은 바꾸지 말고 app.py의 UI만 다듬어줘.

요구사항:
1. 전체 인상: 깔끔하고 가벼운 번역 도구 느낌. 기본 Streamlit 템플릿처럼 보이지 않게 색상, 여백, 타이포그래피를 의도적으로 정해줘.
2. 레이아웃
   - 상단에 제목과 한 줄 설명
   - 입력 카드: 입력창 + 글자 수 표시 (예: 123 / 5000)
   - 언어 버튼 3개를 같은 너비로 한 줄 배치, 각 버튼에 국기 이모지나 아이콘 사용 가능
   - 결과 카드: 어떤 언어인지 배지/라벨로 보여주고 번역문을 읽기 좋게 표시, 복사하기 쉬운 형태 유지
3. 구현 방식
   - st.markdown(unsafe_allow_html=True)의 CSS 주입 또는 .streamlit/config.toml 테마 사용
   - 가능하면 라이트/다크 모드 모두에서 읽기 좋게
   - 모바일 폭(약 375px)에서도 버튼과 카드가 깨지지 않게
4. 경고/에러/로딩 상태도 디자인에 맞게 자연스럽게 보이게 해줘.

제약:
- 번역 로직, 예외 처리, session_state 구조는 변경하지 마.
- 추가 패키지 설치 없이 구현해줘.

완료 후: streamlit run app.py 로 실행해서 정상 동작하는지 확인하고, 바꾼 디자인 포인트를 요약해줘.
```

---

## 4단계: 검토 및 QA (Playwright 사용)

```
PRD.md를 기준으로 현재 앱이 올바르게 개발됐는지, 버그가 없는지 Playwright로 직접 브라우저를 조작해서 꼼꼼히 검토해줘.

준비:
- streamlit run app.py 를 백그라운드로 실행하고 Playwright로 해당 주소에 접속해.
- 실제 API 키가 없으면 정상 번역 경로는 openai 호출을 모킹하거나 테스트용 .env로 확인해. 어떤 방식으로 확인했는지 보고서에 명시해줘.

검토 항목:
A. 기능 (PRD 4장, 10장 수용 테스트)
   1. 한국어 문장 입력 후 영어/일본어/베트남어 버튼 각각 클릭 → 올바른 언어로 결과가 나오는지
   2. 같은 글을 다른 언어 버튼으로 연속 번역할 때 결과가 올바르게 바뀌는지
   3. 빈 입력, 공백만 입력 → 경고 표시, API 미호출
   4. 5,000자 초과 입력 → 안내 표시
   5. 여러 줄 입력, 특수문자, 이모지, 따옴표가 포함된 입력의 처리
   6. 로딩 스피너가 번역 중 표시되는지
B. 예외 처리 (PRD 9장)
   1. OPENAI_API_KEY 없음, 잘못된 키, 잘못된 모델명, 네트워크 오류 상황에서 앱이 죽지 않고 안내 메시지를 보여주는지
   2. 에러 화면, 콘솔, 로그 어디에도 API 키가 노출되지 않는지
C. UI/UX (PRD 8장 비기능)
   1. 데스크톱(1280px)과 모바일(375px)에서 레이아웃이 깨지지 않는지 스크린샷으로 확인
   2. 라이트/다크 모드에서 가독성
   3. 브라우저 콘솔 에러/경고 확인
D. 코드 점검
   1. .env, .env.example, .gitignore, requirements.txt가 PRD 7장과 일치하는지
   2. 언어 목록이 딕셔너리로 관리돼 언어 추가가 쉬운지
   3. 중복 코드, 불필요한 코드, 잠재적 버그(session_state 꼬임, 버튼 중복 클릭 등)

결과물:
- PRD 요구사항별 통과/실패 체크리스트 표
- 발견한 버그 목록 (재현 방법, 심각도, 원인 추정)
- 주요 화면 스크린샷 경로
- 발견한 버그 중 수정이 명확한 것은 수정하고, 수정 후 해당 시나리오를 Playwright로 다시 검증해서 결과를 보고해줘. 판단이 필요한 사항은 수정하지 말고 질문으로 남겨줘.
```
