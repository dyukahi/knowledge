# Chuẩn Dẫn Kinh Tự Nhiên Cho Series Theravāda

## Mục Tiêu

Người đọc không cần biết trước `MN`, `SN`, `AN` hay `DN`. Bài viết phải dẫn họ vào nội dung Kinh bằng tiếng Việt tự nhiên; mã Kinh và segment ID chỉ nằm ở lớp kiểm chứng yên tĩnh.

## Cách Nhắc Nguồn Trong Văn Xuôi

Không viết trơ: `MN 26 nói rằng…`

Viết:

> **Kinh về cuộc tìm cầu cao quý**, thuộc **Trung Bộ Kinh**, mô tả…

Lần đầu có thể giữ tên Pāli trong dòng nguồn. Những lần sau chỉ dùng tên Việt dễ hiểu và link.

## Khối Trích Dẫn Chuẩn

```markdown
> [!quote] Kinh về cuộc tìm cầu cao quý — Trung Bộ Kinh
> Đức Phật mô tả một người đang chịu sinh–già–bệnh–chết nhưng bắt đầu tìm con đường thoát khỏi chính vòng trói buộc ấy.
>
> **Pāli**
> *…*
>
> **Dịch Việt rút gọn**
> …
>
> <small>Nguồn kiểm chứng: <a href="https://suttacentral.net/mn26">MN 26, đoạn 12.1–12.3</a> · <i>Ariyapariyesanā Sutta</i></small>
```

Sau khối trích là văn xuôi bình thường giải thích ý nghĩa. Không nhét các field như “Tên dễ hiểu”, “Nằm ở đâu”, “Nói nôm na” hay “Vì sao dùng ở đây” vào giao diện đọc.

## Chức Năng Của Từng Phần

1. **Tiêu đề:** tên Việt tự nhiên + tên bộ Kinh Hán-Việt đã xác minh.
2. **Câu dẫn:** một câu trung tính mô tả nội dung exact passage.
3. **Pāli:** nguyên văn từ segment đã kiểm chứng.
4. **Dịch Việt:** dùng khi dịch đủ toàn bộ khối Pāli.
5. **Dịch Việt rút gọn:** bắt buộc khi bản dịch có `…` hoặc chủ ý lược bớt.
6. **Dòng nguồn:** mã, segment, link và tên Pāli; nhỏ, thứ cấp nhưng vẫn audit được.
7. **Văn xuôi sau khối:** takeaway và claim-specific explanation, không lặp metadata.

## Hán-Việt Và Tên Việt

- Tên bộ Kinh đã khóa: **Trường Bộ Kinh, Trung Bộ Kinh, Tương Ưng Bộ Kinh, Tăng Chi Bộ Kinh**.
- Tên bài Kinh Hán-Việt chỉ dùng khi có nguồn xác minh.
- Không xác minh được thì dùng tên Việt mô tả tự nhiên và ẩn hoàn toàn dòng Hán-Việt riêng; không hiện disclaimer kỹ thuật cho độc giả.

## Các Họ Nguồn

- `DN` — *Dīgha Nikāya* — Trường Bộ Kinh.
- `MN` — *Majjhima Nikāya* — Trung Bộ Kinh.
- `SN` — *Saṁyutta Nikāya* — Tương Ưng Bộ Kinh.
- `AN` — *Aṅguttara Nikāya* — Tăng Chi Bộ Kinh.
- `Ud` — *Udāna* — Kinh Tự Thuyết.
- `Iti` — *Itivuttaka* — Kinh Phật Thuyết Như Vậy.
- `pli-tv-kd` — Luật tạng Theravāda, phần *Cullavagga*.
- `ds` / `vb` — Vi Diệu Pháp canonical; phải gắn đúng lớp, không trình bày như Kinh sớm.

## Abhidhamma, Chú Giải Và Khoa Học

- **Vi Diệu Pháp canonical:** ghi rõ thuộc Vi Diệu Pháp tạng Theravāda.
- **Chú giải/sách thủ bản:** ghi tên tác phẩm và lớp hậu kỳ; paraphrase khi giấy phép không cho trích.
- **Khoa học:** ghi loại nghiên cứu, kết cục và giới hạn. Không dùng làm bằng chứng cho nghiệp, tái sinh, Nibbāna, vũ trụ luận, vô ngã hoặc sát-na tâm.

## Gate Biên Tập

- Không còn mã Kinh trơ trong heading hoặc reader-facing prose.
- Mỗi narrative quote có tiêu đề tự nhiên, câu dẫn, Pāli, đúng một translation label và dòng nguồn.
- `Dịch Việt` không được chứa dấu lược `…`; nếu có phải đổi thành `Dịch Việt rút gọn`.
- Không có metadata-form labels hoặc `REVIEW_REQUIRED` trên bài đã hoàn tất.
- Exact-Pāli audit, semantic review, mobile render và build vẫn bắt buộc.
- YAML, URL, filename, segment ID và provenance enum không bị Việt hóa tự động.
