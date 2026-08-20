# Chuẩn Dẫn Kinh Dễ Đọc Cho Series Theravāda

## Mục Tiêu

Người đọc không cần biết trước `MN`, `SN`, `AN` hay `DN`. Nghĩa và lý do trích dẫn phải xuất hiện trước; mã Kinh và segment ID được giữ ở lớp kiểm chứng.

## Quy Tắc Lần Đầu Nhắc Nguồn

Không viết trơ: `MN 26 nói rằng…`

Viết:

> **Kinh về Cuộc Tìm Cầu Cao Quý**, bài 26 của **Trung Bộ Kinh** (*Majjhima Nikāya*; mã nguồn `MN 26`), mô tả…

Thứ tự hiển thị:

1. tên Việt dễ hiểu;
2. tên Hán-Việt truyền thống nếu đã xác minh;
3. tên Pāli của bài Kinh nếu có;
4. tên đầy đủ của bộ Kinh;
5. mã viết tắt trong ngoặc hoặc dòng nguồn.

Không xác minh được tên Hán-Việt thì để trống. Không dịch từng chữ để tự tạo tên Hán-Việt.

## Source Card Cho Claim Quan Trọng

> [!quote] Nguồn Kinh dễ hiểu
> **Tên dễ hiểu:** Kinh về Cuộc Tìm Cầu Cao Quý  
> **Nằm ở đâu:** *Ariyapariyesanā Sutta*, bài 26 của Trung Bộ Kinh (*Majjhima Nikāya*)  
> **Đoạn này nói gì:** mô tả trung tính nội dung nằm trong chính đoạn trích  
> **Mã kiểm chứng:** `MN 26`, đoạn `mn26:12.1–12.3`; [mở nguồn gốc](https://suttacentral.net/mn26)
>
> **Pāli gốc:** …
>
> **Dịch sát nghĩa:** dùng khi bản dịch bao phủ đầy đủ khối Pāli  
> **Dịch rút gọn có đánh dấu:** dùng thay dòng trên nếu bản dịch có `…` hoặc chủ ý lược bớt  
> **Nói nôm na:** một takeaway bình dân, không giả làm bản dịch  
> **Vì sao dùng ở đây:** claim cụ thể trong bài mà đoạn Kinh đang hỗ trợ

`Tên truyền thống/Hán-Việt` là field tùy chọn. Không có tên bài Kinh đã xác minh thì ẩn cả dòng; tên bộ như **Trung Bộ Kinh** vẫn hiện trong `Nằm ở đâu`.

## Ba Lớp Dịch

1. **Pāli gốc:** exact text từ segment đã kiểm chứng.
2. **Dịch sát nghĩa tiếng Việt:** chỉ dùng khi dịch đủ toàn bộ khối Pāli, không thêm claim ngoài segment. Nếu có lược bớt, đổi nhãn thành **Dịch rút gọn có đánh dấu**.
3. **Nói nôm na:** một takeaway bình dân, phải khác với mô tả literal và không giả làm bản dịch.
4. **Vì sao dùng ở đây:** nêu claim cụ thể trong bài được đoạn Kinh hỗ trợ; không lặp lại takeaway.

**Hán-Việt** dùng cho tên bộ Kinh, tên bài Kinh hoặc thuật ngữ truyền thống có nguồn. Nó không thay cho bản dịch tiếng Việt dễ hiểu.

## Nhắc Lại Trong Cùng Bài

Sau source card đầu tiên, dùng tên dễ hiểu: “Kinh về Cuộc Tìm Cầu Cao Quý”. Mã `MN 26` chỉ cần xuất hiện trong link/source line hoặc ngoặc nhỏ khi tránh nhập nhằng.

Không lặp toàn bộ Pāli mỗi lần cùng một claim được nhắc lại.

## Abhidhamma, Chú Giải Và Khoa Học

- **Vi Diệu Pháp canonical:** ghi “thuộc Vi Diệu Pháp tạng Theravāda”, không gọi là Kinh sớm.
- **Chú giải/sách thủ bản:** ghi tên tác phẩm, niên đại/lớp nguồn và dùng paraphrase nếu bản quyền không cho trích.
- **Khoa học:** ghi loại nghiên cứu, quần thể/kết cục và giới hạn. Không dùng làm bằng chứng cho nghiệp, tái sinh, Nibbāna, vũ trụ luận, vô ngã hoặc sát-na tâm.

## Mã Bộ Kinh

- `DN` — *Dīgha Nikāya* — **Trường Bộ Kinh** — tuyển tập các bài kinh dài.
- `MN` — *Majjhima Nikāya* — **Trung Bộ Kinh** — tuyển tập các bài kinh độ dài vừa.
- `SN` — *Saṁyutta Nikāya* — **Tương Ưng Bộ Kinh** — các bài kinh nhóm theo chủ đề tương ứng.
- `AN` — *Aṅguttara Nikāya* — **Tăng Chi Bộ Kinh** — các bài kinh sắp theo số pháp.

## Gate Biên Tập

- Không còn mã Kinh trơ trong reader-facing prose.
- Mọi source card có tên dễ hiểu, bộ Kinh đầy đủ, Pāli, một translation label trung thực, nói nôm na, vì sao dùng và source line.
- Ba field semantic phải làm ba việc khác nhau; không copy cùng một summary.
- Tên Hán-Việt không có verification source phải để null và ẩn cả dòng.
- Exact-Pāli audit và translation review vẫn bắt buộc.
- Bibliography, YAML, URLs, filenames, segment IDs và provenance enums không bị Việt hóa tự động.
