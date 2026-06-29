## 플레이스홀더 코드 금지 (MANDATORY)

스텁/플레이스홀더 코드를 절대 생성하지 마세요. 여기에는 다음이 포함됩니다:
- 주석 처리된 import: `# from dxnn_sdk import InferenceEngine`
- 가짜 결과: `result = np.zeros(...)`
- TODO 마커: `# TODO: implement actual inference`
- 실제 async 구현 없이 "sync 버전과 유사"

모든 생성된 코드는 knowledge base의 실제 API를 사용하여 기능적이어야 합니다.
필요한 SDK/API를 모르는 경우, 먼저 관련 스킬 문서를 읽으세요.
