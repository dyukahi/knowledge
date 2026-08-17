---
title: "Chuẩn Nguồn Và Xuất Xứ Theravāda"
description: "Quy chuẩn phân biệt Kinh sớm, Luật, Vi Diệu Pháp, chú giải, nghiên cứu và diễn giải hiện đại trong toàn bộ series Theravāda."
aliases: ["Theravāda Provenance Standard", "Chuẩn Nguồn Pāli"]
tags: [theravada, pali, provenance, sources]
status: refined
related:
  - "[[theravada/index|Theravāda Và Kinh Tạng Pāli]]"
  - "[[Từ Điển Pāli Cốt Lõi]]"
  - "[[Mục Lục Kinh Dẫn Pāli]]"
---

# Chuẩn Nguồn Và Xuất Xứ Theravāda

**Mục tiêu của chuẩn này là ngăn nhiều lớp truyền thống bị trộn thành một giọng nói duy nhất.** Một ý có thể quan trọng trong Theravāda mà không nhất thiết là nguyên văn lời Phật trong Kinh sớm.

---

## Thứ Bậc Nguồn

### Cấp A — Văn Bản Gốc

1. Pāli gốc với mã kinh chuẩn: DN, MN, SN, AN, KN; mã Luật; mã Vi Diệu Pháp.
2. SuttaCentral segmented text/public-domain Pāli là nguồn làm việc chính.
3. Khi có dị bản hoặc vấn đề dịch, ghi rõ ấn bản và đoạn đang dùng.

### Cấp B — Bản Dịch

1. Đối chiếu ít nhất hai bản dịch khi một thuật ngữ hoặc câu có tranh luận.
2. Ưu tiên bản dịch có người dịch, giấy phép và mã kinh rõ.
3. Không trích dài nếu giấy phép không cho phép; tự diễn giải và dẫn về nguồn.
4. Mọi câu do Vault tự dịch phải ghi **Bản dịch làm việc của redpill.wiki**.

### Cấp C — Nghiên Cứu Và Truyền Thống

1. Nghiên cứu lịch sử/văn bản học hiện đại.
2. Các trưởng lão, thiền sư và học giả Theravāda có xuất xứ rõ.
3. Quan điểm của một dòng thiền không được trình bày như đồng thuận toàn truyền thống.

### Cấp D — So Sánh Hiện Đại

Tâm lý học, khoa học thần kinh, vật lý, triết học tiến trình và huyền học so sánh. Luôn nằm trong mục riêng: **Cộng hưởng khái niệm, không phải bằng chứng**.

---

## Nhãn Xuất Xứ Bắt Buộc

Mỗi bài khai báo một hoặc nhiều nhãn:

| Nhãn hiển thị | Giá trị frontmatter | Phạm vi |
|---|---|---|
| Kinh sớm | `early-sutta` | Các bài kinh thuộc lớp văn bản sớm, có mã và văn cảnh rõ |
| Luật tạng | `vinaya` | Luật và câu chuyện hình thành giới luật |
| Vi Diệu Pháp | `abhidhamma` | Hệ thống canonical trong Theravāda, tách khỏi Kinh sớm |
| Chú giải | `commentary` | Aṭṭhakathā, Visuddhimagga và hệ thống hậu kỳ |
| Nghiên cứu lịch sử | `historical-scholarship` | Lịch sử, văn bản học, khảo cứu hiện đại |
| Diễn giải hiện đại | `modern-theravada` | Giáo thọ/dòng thiền hiện đại |
| So sánh liên truyền thống | `comparative` | Mahāyāna, Hindu, Gnostic hoặc truyền thống khác |
| Đối chiếu khoa học | `science-comparison` | Khoa học thần kinh, vật lý, tâm lý học |

Một heading có khẳng định quan trọng phải cho người đọc biết nó thuộc lớp nào nếu không rõ từ văn cảnh.

---

## Mẫu Frontmatter Cho Bài Học

```yaml
tradition: theravada
series: pali-canon-path
module: 1
lesson: 1
canonical_role: historical-buddha
prerequisites: []
next_reading: []
provenance:
  - early-sutta
  - historical-scholarship
canonical_refs:
  - "MN 26"
  - "DN 16"
pali_terms:
  - buddha
translation_policy: redpill-working-translation-cross-checked
source_license_checked: true
```

`canonical_role` phải duy nhất trong 36 bài. `prerequisites` chỉ được trỏ về tài liệu Batch 0 hoặc bài có số nhỏ hơn.

---

## Quy Tắc Pāli

- Dùng Unicode Pāli có dấu: `dukkha`, `anicca`, `anattā`, `paṭiccasamuppāda`, `nibbāna`.
- Lần xuất hiện đầu: **Pāli — cách đọc gần đúng — nghĩa làm việc**.
- Không áp một nghĩa tiếng Việt duy nhất cho mọi văn cảnh.
- [[Từ Điển Pāli Cốt Lõi]] lưu lemma, dấu phụ, cách đọc hỗ trợ, mã kinh mẫu và các cách dịch cạnh tranh.
- “Cách đọc” không được gọi là chuẩn phát âm duy nhất.

---

## Quy Tắc Trích Dẫn

Mẫu ngắn:

> **Pāli:** …
>
> **Dịch nghĩa:** …
>
> **Nguồn:** SN 56.11, đoạn …; Pāli từ SuttaCentral; bản dịch làm việc đã đối chiếu …

Không dùng câu trích không tìm được mã kinh. Nếu câu phổ biến là diễn giải hậu kỳ, ghi rõ: **Câu tổng hợp, không phải nguyên văn kinh**.

---

## Phân Biệt Lớp Văn Bản

- Kinh sớm không mặc nhiên đồng nghĩa toàn bộ Tam Tạng Pāli.
- Vi Diệu Pháp là canonical trong Theravāda nhưng là một hệ thống hóa riêng; không viết “Đức Phật nói” khi chi tiết chỉ xuất hiện ở Vi Diệu Pháp/chú giải.
- *Thanh Tịnh Đạo* và chú giải được tôn trọng nhưng phải gắn nhãn hậu kỳ.
- Tranh luận về thiền, duyên khởi, sát-na tâm và Nibbāna phải trình bày nhiều cách đọc có uy tín.
- Luật tạng cung cấp bối cảnh tăng đoàn; không áp nguyên xi mọi giới luật xuất gia cho người tại gia.

---

## Kỷ Luật Khẳng Định

Mỗi bài kết bằng bốn câu hỏi:

1. **Văn bản nói gì?**
2. **Truyền thống giải thích gì?**
3. **Bài này suy luận gì?**
4. **Điều gì chưa được chứng minh?**

Tuyệt đối không dùng:

- vật lý lượng tử để chứng minh nghiệp/tái sinh;
- sóng vô tuyến hoặc vật chất tối để chứng minh 31 cõi;
- trải nghiệm thiền cá nhân làm bằng chứng phổ quát;
- bài huyền học cũ làm nguồn canonical.

---

## Giấy Phép Theo Từng Ấn Bản

- Pāli gốc/public domain: được trích với xuất xứ rõ.
- SuttaCentral: kiểm tra giấy phép của từng bản dịch/ấn bản, không giả định mọi bản dịch được lưu trên cùng nền tảng có cùng giấy phép.
- Dhammatalks, Access to Insight, PTS, VRI, Budsas và nguồn tiếng Việt: kiểm tra từng tác phẩm; ưu tiên dẫn và diễn giải hơn sao chép dài.
- Ghi URL, người dịch, ấn bản, ngày truy cập và trạng thái giấy phép trong source manifest.

---

## Cấu Trúc Mỗi Bài

1. Câu hỏi bài giải quyết.
2. Thuật ngữ Pāli cốt lõi.
3. Đoạn kinh nền.
4. Giải thích theo văn cảnh.
5. Lớp Vi Diệu Pháp/chú giải nếu có.
6. Ứng dụng thực hành.
7. Hiểu lầm thường gặp.
8. Kỷ luật khẳng định.
9. Cần đọc trước / đọc tiếp.
10. Nguồn và giấy phép.

---

## Chuẩn Hình Ảnh

- Chỉ tạo hình cho batch đang phát hành.
- Hình mang phong cách hiện thực biên tập/thiền quán, không giả làm bằng chứng lịch sử.
- Tránh khuôn mặt Đức Phật như ảnh chụp sự kiện thật; ưu tiên biểu tượng, cảnh quan, cây Bồ-đề, bánh xe Pháp và bản đồ khái niệm.
- Không yêu cầu AI viết chữ Pāli lên hình.
