# Copilot Agent Hub và khóa T1: Hướng dẫn sử dụng

[English](../README.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [ไทย](README.th.md) · [Bahasa Indonesia](README.id.md) · **Tiếng Việt**

Đây là ứng dụng web chạy cục bộ, giúp nhân viên học cách xây dựng **một tác nhân Microsoft 365 Copilot với một mục đích**, kiểm thử và sử dụng an toàn. Sau khóa đào tạo, ứng dụng trở thành cửa ngõ duy nhất cho các tác nhân Copilot trong tổ chức: danh mục tác nhân kèm đánh giá quản trị, bảng ý tưởng, yêu cầu giấy phép, mạng lưới huấn luyện viên, thư viện câu lệnh, thông tin chuyên sâu về mức độ áp dụng và đối chuẩn với các công ty dẫn đầu.

Ứng dụng chạy trên mọi máy tính có Python. Không cần cài thêm gì và không cần kết nối Internet; toàn bộ dữ liệu được lưu trong một tệp SQLite. Toàn bộ ứng dụng có sẵn bằng **tiếng Anh, tiếng Nhật, tiếng Trung giản thể, tiếng Thái, tiếng Indonesia và tiếng Việt**.

## Bắt đầu nhanh

1. Cài **Python 3.8 trở lên** từ <https://www.python.org/downloads/>. Trên Windows, đánh dấu *Add Python to PATH* khi cài đặt.
2. Tải xuống hoặc sao chép (clone) thư mục này.
3. Khởi động ứng dụng:
   - **Windows:** nhấp đúp `start_windows.bat`
   - **macOS / Linux:** chạy `./start_mac_linux.sh`
   - **Hoặc từ bất kỳ cửa sổ dòng lệnh nào:** `python app.py`
4. Trình duyệt sẽ mở <http://127.0.0.1:8000>. Ở lần đầu, hãy tạo tài khoản quản trị viên.
5. Học viên chọn **Tạo tài khoản** ở trang đăng nhập và đăng ký bằng mã nhân viên.

Để dừng ứng dụng, nhấn `Ctrl+C` trong cửa sổ dòng lệnh (hoặc đóng cửa sổ).

## Đổi ngôn ngữ

Mọi trang (kể cả trang đăng nhập) đều có menu **Ngôn ngữ** ở phía trên. Lựa chọn của bạn sẽ được ghi nhớ.

Màn hình, bài học, câu hỏi và giải thích trong bài kiểm tra, các bước thực hành, mẫu, bảng thuật ngữ, bảng đối chuẩn, thông báo và chứng chỉ đều đã được dịch. Có hai thứ được cố ý giữ nguyên tiếng Anh:

- **Nhãn giao diện của Microsoft** như *New agent*, *Configure*, *Try it*, *Can chat* và *Settings > Personalization*. Học viên thấy đúng các nhãn này trong Microsoft 365 Copilot, nên khóa học dùng nguyên văn.
- **Tiêu đề các trang nguồn trên Microsoft Learn**, để người đứng lớp dễ tìm trang gốc.

Trên trang Mẫu, mỗi mẫu đã dịch đều có thêm **Bản gốc tiếng Anh**, vì một số tổ chức yêu cầu viết hướng dẫn cho tác nhân bằng tiếng Anh. Văn bản do quản trị viên tự nhập (câu hỏi riêng của tổ chức, hướng dẫn sử dụng) được hiển thị đúng như đã viết.

## Hướng dẫn cho học viên

1. Tại **trang chủ**, xem tiến độ và bước tiếp theo.
2. Trong **Khóa học của tôi**, học khóa cốt lõi (10 mô-đun, 29 bài học, khoảng 150 phút). Đọc xong mỗi bài, nhấn *Đánh dấu đã học xong*. Nếu ít thời gian, hãy theo lộ trình cốt lõi 60 phút được mô tả trong bài 1.3.
3. Cuối mỗi mô-đun có một **bài kiểm tra** ngắn. Đáp án đúng và giải thích hiện ngay sau khi nộp, và bạn có thể làm lại nhiều lần.
4. Trong **Bản điều lệ tác nhân của tôi**, lập kế hoạch mục đích, việc nên làm và không nên làm, cùng nguồn kiến thức của tác nhân. Ứng dụng soạn sẵn bản nháp hướng dẫn từ bản điều lệ, và bạn có thể đăng ký tác nhân vào trung tâm ngay.
5. Mở trang **Thực hành** trong khi làm 12 bước trong Microsoft 365 Copilot, và đánh dấu từng bước khi điều kiện "Xong khi" được đáp ứng. Bước 1 đến 10 là bắt buộc.
6. **Bài đánh giá cuối khóa** lấy 15 câu từ ngân hàng 58 câu hỏi, luôn bao gồm 3 câu kiểm tra kiến thức chính. Điểm đạt mặc định là 80%.
7. Khi đã xong mọi bài học, các bước thực hành 1 đến 10 và bài đánh giá cuối khóa, bạn sẽ nhận được **Chứng chỉ**, có thể in hoặc lưu thành PDF.

Làm bài **Tự đánh giá kỹ năng** (khoảng 2 phút) để nhận gợi ý mô-đun. Trong **Lộ trình học**, xem các cấp độ người xây dựng 1 đến 3 và phạm vi chia sẻ được mở khóa ở mỗi cấp. **Lộ trình lãnh đạo** cho quản lý và **Lộ trình huấn luyện viên** cho huấn luyện viên là tùy chọn.

**Bộ công cụ** gồm các mẫu có nút sao chép, thẻ tham khảo nhanh để in, bảng thuật ngữ, tài liệu tham khảo của Microsoft, hướng dẫn cho người đứng lớp, cùng trang chính sách và trợ giúp.

## Cách dùng Trung tâm tác nhân

| Tính năng | Cách dùng |
|---|---|
| **Danh mục tác nhân** | Mọi tác nhân được chia sẻ cho người khác đều được đăng ký kèm mục đích, chủ sở hữu, cấp, nguồn kiến thức, mức độ nhạy cảm của dữ liệu, phạm vi chia sẻ, một KPI có giá trị cơ sở, kết quả kiểm thử và ngày đánh giá. Trước khi xây dựng, hãy tìm trong danh mục đã phê duyệt xem đã có tác nhân nào dùng lại được chưa. |
| **Đánh giá quản trị** | Tác nhân sẽ chia sẻ với nhóm hoặc toàn tổ chức, hoặc dùng dữ liệu mật, được đưa vào hàng đợi đánh giá của huấn luyện viên và kiểm tra theo danh sách 8 mục. Cấp 3 và 4 (hành động trên dữ liệu hoặc tự động) do CoE đánh giá. Người gửi phải có chứng chỉ T1. |
| **Đánh giá giá trị 90 ngày** | Tác nhân đã phê duyệt có ngày đánh giá. Chủ sở hữu ghi lại kết quả KPI, và tác nhân không có giá trị đo lường được sẽ bị ngừng sử dụng. |
| **Bảng ý tưởng** | Đăng công việc Copilot có thể hỗ trợ, bình chọn và bình luận. Tác nhân xây dựng từ một ý tưởng được liên kết lại với ý tưởng đó. |
| **Yêu cầu giấy phép** | Nhóm yêu cầu suất Microsoft 365 Copilot kèm tình huống sử dụng và số giờ dự kiến tiết kiệm. CoE phê duyệt theo từng đợt, ưu tiên giá trị kỳ vọng cao nhất. |
| **Cộng đồng** | Danh bạ huấn luyện viên kèm giờ tư vấn, sự kiện (promptathon, buổi chia sẻ, đào tạo trực tiếp) và thư viện câu lệnh có chấm điểm. |
| **Hỏi CoE** | Gửi câu hỏi về chính sách, dữ liệu, giấy phép và sự cố. Hướng dẫn sử dụng và quy tắc dữ liệu nằm cùng trang. |
| **Ghi lại số giờ tiết kiệm** | Ghi số giờ tiết kiệm mỗi tuần tại trang chủ của trung tâm. |
| **Thông báo** | Nhận kết quả đánh giá, quyết định về giấy phép, bình luận về ý tưởng và câu trả lời từ CoE. |

## Hướng dẫn cho huấn luyện viên

- Nên có khoảng 1 huấn luyện viên trên 60 nhân viên (khoảng 170 người cho 10.000 nhân viên).
- Ghi giờ tư vấn trong hồ sơ để tên bạn hiển thị trong danh bạ cộng đồng.
- Trong **Hàng đợi đánh giá**, xem các tác nhân sẽ được chia sẻ với nhóm hoặc tổ chức. Đọc mục đích, cấp, nguồn kiến thức, mức độ nhạy cảm của dữ liệu và kết quả kiểm thử, xin chủ sở hữu liên kết trò chuyện, rồi tự chạy ba bài kiểm thử.
- Bạn chỉ có thể phê duyệt khi mọi mục trong danh sách kiểm tra đều đạt. Nếu không, chọn *Yêu cầu chỉnh sửa* và giải thích cần thay đổi gì. Bạn không thể tự đánh giá tác nhân của mình.

## Hướng dẫn cho quản trị viên (CoE)

- **Tổng quan**: số nhân viên đã nhập, số người đã chứng nhận, đang học và chưa bắt đầu; điểm cuối khóa và góp ý trung bình; tỷ lệ chứng nhận theo phòng ban; và phễu mô-đun.
- **Học viên**: tìm kiếm và lọc, chỉnh sửa thông tin, đặt lại mật khẩu, hoặc *Đặt người này làm huấn luyện viên*.
- **Nhập danh sách nhân viên**: tải lên CSV (`associate_id, name, email, department, location`). Nhập lại sẽ cập nhật thông tin và giữ nguyên tiến độ.
- **Xuất CSV**: báo cáo tiến độ đầy đủ, và ngân hàng câu hỏi kèm đáp án ở một hoặc mọi ngôn ngữ.
- **Ngân hàng câu hỏi**: sắp xếp theo tỷ lệ trả lời đúng từ thấp nhất. Có thể tắt câu hỏi hoặc thêm câu hỏi riêng của tổ chức.
- **Cài đặt**: tên tổ chức, điểm đạt, và hướng dẫn sử dụng của tổ chức (để trống sẽ hiển thị hướng dẫn mẫu đã dịch).
- **Thông tin chuyên sâu** và **Đối chuẩn**: xem đào tạo, tác nhân, ý tưởng, giấy phép và số giờ tiết kiệm trên một bảng điều khiển, và so sánh với mục tiêu điều chỉnh theo số nhân viên.

## Triển khai cho 10.000 nhân viên

- **Nhập trước danh sách nhân viên**: đưa danh sách từ bộ phận nhân sự vào mẫu CSV rồi nhập, hoặc chạy `python app.py import-users associates.csv`.
- **Dùng chung một cơ sở dữ liệu**: chạy `python app.py --host 0.0.0.0 --port 8000` trên một máy truy cập được từ mạng nội bộ. Ứng dụng dùng HTTP, nên chỉ mở trên mạng nội bộ tin cậy, hoặc đặt sau reverse proxy HTTPS của tổ chức. Hãy trao đổi với bộ phận CNTT trước.
- **Sao lưu**: toàn bộ dữ liệu nằm trong `data/training.db`. Hãy sao chép tệp này khi ứng dụng đã dừng.

## Danh sách lệnh

```text
python app.py                          Khởi động ứng dụng (mở trình duyệt)
python app.py --port 8080 --no-browser Dùng cổng khác và không mở trình duyệt
python app.py --host 0.0.0.0           Lắng nghe trên mạng (xem lưu ý triển khai ở trên)
python app.py create-admin             Thêm quản trị viên, hoặc nâng quyền tài khoản có sẵn
python app.py import-users FILE.csv    Nhập hoặc cập nhật nhân viên từ CSV
python app.py export FILE.csv          Xuất báo cáo tiến độ ra CSV
python app.py reseed                   Tải lại nội dung khóa học sau khi sửa training/content.py
python app.py demo-data 500            Thêm 500 học viên DEMO giả định để dùng thử
python app.py i18n-extract --check     Hiển thị số đoạn còn thiếu bản dịch ở mỗi ngôn ngữ
python app.py i18n-extract --missing vi  Liệt kê văn bản tiếng Anh chưa được dịch sang tiếng Việt
```

Chỉ dùng `demo-data` trên cơ sở dữ liệu thử nghiệm.

## Cập nhật nội dung và bản dịch

1. Sửa văn bản tiếng Anh trong `training/content.py` và `training/blocks.py`.
2. Chạy `python app.py reseed`. Tiến độ và lịch sử làm bài của học viên được giữ nguyên.
3. Chạy `python app.py i18n-extract --check` để xem đoạn nào đã thay đổi nhưng chưa được dịch ở từng ngôn ngữ, rồi thêm bản dịch vào `training/locales/`. Khi chưa có bản dịch, ứng dụng hiển thị tiếng Anh.
4. Khởi động lại ứng dụng.

**Trước khi giảng dạy**, người đứng lớp nên:
- Mở từng trang Microsoft Learn trên trang Tài liệu tham khảo và xác nhận các bước và nhãn vẫn khớp với tenant của bạn. Microsoft thường xuyên thay đổi giao diện Copilot.
- Thêm ảnh chụp màn hình đã xác minh của chính tổ chức cho mô-đun 4. Ứng dụng không kèm ảnh chụp màn hình của Microsoft.
- Kiểm tra lại nguồn của các ví dụ thực tế và số liệu đối chuẩn trước khi trình bày.
- Thay hướng dẫn sử dụng mẫu bằng hướng dẫn đã được phê duyệt tại Quản trị → Cài đặt.

## Phạm vi và giới hạn

- Ứng dụng không kết nối với Microsoft 365, nên không thấy được tác nhân trong tenant và không xác minh được học viên có thật sự xây dựng tác nhân hay không. Phần thực hành và danh mục là tự khai báo, và huấn luyện viên xác minh qua liên kết trò chuyện khi đánh giá.
- Số liệu đối chuẩn lấy từ nguồn công khai của công ty, nhà cung cấp và báo chí, có ghi ngày trong ứng dụng, và chưa được kiểm toán độc lập.
- Không có đăng nhập một lần (Microsoft Entra ID). Tài khoản được quản lý trong ứng dụng.
- Bản dịch được chuẩn bị cho dự án này. Như mọi tài liệu đào tạo khác, hãy nhờ người đứng lớp bản ngữ ở từng quốc gia rà soát trước khi triển khai.
