# Tin nhắn báo giảng viên — tình trạng model DeepSeek trên Bedrock chậm

> File này chỉ để bạn COPY nội dung nhắn/email cho giảng viên. Không phải phần của bài.

---

## Bản NGẮN (nhắn Zalo/Messenger)

Em báo cáo thầy/cô một vấn đề kỹ thuật khi chạy thí nghiệm bổ sung (thêm topology
cho phần phản biện reviewer):

Model **DeepSeek V3.2 trên Amazon Bedrock chạy rất chậm và không ổn định**. Em đo
5 lần gọi liên tiếp cùng một prompt thì thời gian phản hồi dao động mạnh: 3.8s, 4.7s,
8.3s **nhưng có lần lên tới 34s và 40s**. Có lần một cell còn bị "treo" (kẹt ở một
lần gọi API, đứng im 30–50 phút không xong). So sánh: model Llama 3.3 70B chạy cùng
cấu hình chỉ mất ~9 phút/cell, còn DeepSeek ước tính 40–90 phút/cell.

Em đã khắc phục bằng cách thêm giới hạn thời gian chờ (timeout 60s) và cho tự thử lại,
nên giờ không còn treo vô hạn. Em vẫn giữ DeepSeek vì nó cho kết quả khoa học tốt nhất
cho bảng thí nghiệm, chỉ là chạy lâu hơn (em chấp nhận chờ). Em sẽ báo lại khi có kết quả ạ.

---

## Bản DÀI (email, đầy đủ hơn)

Kính gửi thầy/cô,

Em xin cập nhật tiến độ và một vấn đề kỹ thuật gặp phải khi chạy thí nghiệm bổ sung
cho bài AAMAS 2027 (phần thêm cấu hình topology để trả lời phản biện của reviewer về
việc "chỉ có một model / một cấu hình").

**Vấn đề:** Trong 4 model dùng qua Amazon Bedrock, riêng **DeepSeek V3.2 phản hồi
rất chậm và độ trễ không ổn định**. Cụ thể, em đo 5 lần gọi liên tiếp với cùng một
prompt:

| Lần gọi | Thời gian phản hồi |
|---|---|
| 1 | 33.9 giây |
| 2 | 3.8 giây |
| 3 | 4.7 giây |
| 4 | 40.5 giây |
| 5 | 8.3 giây |

Độ trễ dao động từ ~4 giây tới ~40 giây cho cùng loại yêu cầu. Nghiêm trọng hơn, có
lần một tiến trình bị **treo ở một lần gọi API** (không nhận được phản hồi, đứng im
30–50 phút mà không báo lỗi).

**Nguyên nhân:** đây là đặc tính của endpoint DeepSeek trên Bedrock (model suy luận,
sinh nhiều token, đôi khi một request bị kẹt), cộng với việc thư viện gọi API ban đầu
**chưa đặt giới hạn thời gian chờ**, nên một request kẹt sẽ treo vô hạn.

**So sánh để thầy/cô hình dung:** cùng một cấu hình thí nghiệm (topology star, 40
lượt), model **Llama 3.3 70B chỉ mất ~9 phút**, trong khi **DeepSeek ước tính 40–90
phút** cho một cell.

**Cách em đã xử lý:**
1. Thêm **giới hạn thời gian chờ (timeout 60 giây)** và cơ chế **tự thử lại** cho các
   lần gọi Bedrock, để một request kẹt sẽ tự hủy và thử lại thay vì treo vô hạn.
2. Vẫn **giữ DeepSeek** trong thí nghiệm vì nó cho giá trị khoa học tốt nhất (mức lan
   truyền trung gian, giúp bảng topology thể hiện rõ khác biệt), chỉ chấp nhận thời
   gian chạy lâu hơn.

**Ảnh hưởng:** không ảnh hưởng đến kết quả đã có trong bài (bài đã trên ngưỡng chấp
nhận); đây chỉ là thí nghiệm **bổ sung để nâng chất lượng**. Em sẽ báo lại khi chạy xong.

Em cảm ơn thầy/cô ạ.
