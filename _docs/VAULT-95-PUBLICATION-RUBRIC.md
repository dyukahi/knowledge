# redpill.wiki 9.5 Publication Rubric

A page/pack is **9.5-ready** when it is not only correct, but publishable as a premium editorial asset.

## Score layers

| Layer | Weight | 9.5 standard |
|---|---:|---|
| Thesis clarity | 20% | The first screen tells the reader exactly what the page is really about and why it matters. |
| Claim discipline | 20% | Fact, pattern, symbol and speculative synthesis are not mixed. High-risk claims have a clear reading frame. |
| Vault voice | 15% | Sharp, bilingual, mystical-critical, not generic SEO prose. |
| Mobile readability | 15% | No long horizontal code/chains; paragraphs breathe; tables/mermaid used only when useful. |
| Graph/navigation | 15% | Page links into a reading path, not a dead end. Related pages are intentional. |
| Public utility | 10% | Reader leaves with a map, lens, or practical discernment tool. |
| Metadata hygiene | 5% | Title, description, aliases, tags, status and related are clean. |

## Pack-level gates

A publication pack must have:

1. A clear entry article.
2. A 3-7 article reading path.
3. A bridge note or index section explaining why the pack exists.
4. Consistent claim discipline across high-risk pages.
5. No hard QC blockers:
   - broken links = 0
   - duplicate titles = 0
   - missing descriptions = 0
   - missing aliases = 0
   - mobile-hostile code = 0

## Priority publication packs

### 1. Core Matrix Pack

Purpose: define the operating system of the vault.

Path:

1. [[Cách Đọc Red Pill Wiki]]
2. [[Ma Trận]]
3. [[Ma Trận - Giải Phẫu Hoàn Chỉnh]]
4. [[Monad]]
5. [[Gnosis]]
6. [[Sự Nhất Thể]]
7. [[Loosh - Năng Lượng Thu Hoạch Từ Con Người]]

### 2. Health Sovereignty Pack

Purpose: help readers separate terrain/body sovereignty from reckless medical contrarianism.

Path:

1. [[Y Tế Tự Nhiên]]
2. [[Kính Chiếu Yêu - Nhìn Thấu Tây Y]]
3. [[Thuyết Vi Sinh Nội Sinh]]
4. [[Ung Thư - Metabolic Protocol]]
5. [[Ketogenic Diet]]
6. [[Prolonged Fasting]]

### 3. Family, Dopamine & Orphan Train Pack

Purpose: explain why dating/gender/family collapse is a systems problem, not a scapegoat war.

Path:

1. [[Dopamine Economy - Nền Kinh Tế Của Sự Thèm Muốn]]
2. [[Tâm Lý Học Tiến Hóa Về Giới Tính]]
3. [[Care Economy Và Cách Ma Trận Làm Rỗng Gia Đình]]
4. [[Orphan Train 2.0 - Khi Ma Trận Chở Trẻ Em Ra Khỏi Dòng Máu]]
5. [[Tình Nghĩa Là Hạ Tầng Cuối Cùng]]

### 4. Financial Sovereignty Pack

Purpose: move readers from fiat awareness to self-custody/privacy/risk literacy.

Path:

1. [[Bitcoin]]
2. [[Bitcoin Sẽ Chết Nếu Không Có Privacy]]
3. [[Privacy]]
4. [[Giữ Tiền Quan Trọng Hơn Kiếm Tiền]]
5. [[Chainlink - Mắt Xích Của Tokenized World]]

### 5. Disclosure & Spectacle Pack

Purpose: read current events as ritual/media/predictive programming without claiming certainty.

Path:

1. [[Predictive Programming - Cấy Tương Lai Vào Tiềm Thức]]
2. [[Hollywood - Cây Đũa Phép Của Phù Thủy]]
3. [[Bộ Tam Thánh Mind Control - NASA Disney Hollywood]]
4. [[A LIE N - SpaceX IPO, Disclosure Day và Nghi Lễ Tên Lửa]]
5. [[Brazil Norway 2026 - Japan Gate Transfer Va Mot Thesis Bi Falsify]]
6. [[Spectacle Ritual - World Cup, Super Bowl Và Nghi Lễ Đồng Bộ Đại Chúng]]

## Pre-publish ritual

Before pushing a pack upgrade:

```bash
python3 _docs/build-knowledge-map.py
python3 scripts/vault_qc_audit.py
```

Then read the first screen of every edited article on mobile width if possible.
