## Git 안전 — Superpowers 산출물

**`docs/superpowers/` 하위 파일을 절대 `git add`하거나 `git commit`하지 마세요.**
이들은 superpowers 스킬 시스템에서 생성된 임시 계획 산출물 (spec, plan)입니다.
`.gitignore`에 포함되어 있지만, 일부 도구는 `git add -f`로 `.gitignore`를 우회할 수
있습니다. 파일 생성은 괜찮습니다 — 커밋은 금지입니다.
