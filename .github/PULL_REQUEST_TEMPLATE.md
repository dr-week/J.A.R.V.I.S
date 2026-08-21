## 📌 Summary of Changes

*Provide a clear, concise overview of what this pull request accomplishes, why it was made, and the context behind the changes.*

---

## 🎯 Linked Issues & DevLoop Work

- Closes #`[ISSUE-XXX]`
- DevLoop Owner: `@username`

---

## 🛠️ Type of Change

- [ ] 🐛 **Bug fix** (non-breaking change which fixes an issue)
- [ ] ✨ **New feature / Modular Connector** (non-breaking change adding functionality)
- [ ] ♻️ **Refactoring** (code structure improvement without behavior change)
- [ ] ⚡ **Performance improvement** (latency reduction, memory optimization)
- [ ] 📝 **Documentation update**
- [ ] 🧪 **Tests / CI improvement**

---

## 🧪 Verification & Testing

### Automated Test Pass
- [ ] Ran `python -m pytest backend/tests/ -v` (190+ tests passing)
- [ ] Ran `npm run lint` & `npm run build` in `clients/web/` (0 errors / warnings)
- [ ] Ran `python scripts/check_dev_env.py`

### Test Coverage Added
*Describe the unit tests or mock fixtures added in `backend/tests/` to verify your changes:*

---

## 🔒 Security & Quality Checklist

- [ ] **No Secrets Committed**: Verified `.env` files, API keys, or personal tokens are not included.
- [ ] **Flat & AI-Friendly Logic**: Code is modular, small, and contains clear developer rationale comments.
- [ ] **Confirmation Gating**: Sensitive or destructive tools are gated by `confirm_once` or `confirm_always`.
- [ ] **Documentation**: Updated `README.md`, `DOCS_MAP.md`, or relevant docs under `docs/`.
