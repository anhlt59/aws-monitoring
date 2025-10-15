# Quy trình triển khai tính năng mới với Claude AI

## 1. Phân tích yêu cầu
- **Thu thập thông tin:** Đầu tiên, xác định rõ yêu cầu của tính năng (user stories, tiêu chí nghiệm thu). Ghi chép vào file Markdown (ví dụ `requirements.md`). Hỏi rõ các trường hợp biên (edge cases) và yêu cầu phi chức năng (hiệu năng, bảo mật).
- **Sử dụng Claude để phân tích yêu cầu:** Dùng một subagent chuyên biệt (ví dụ `yeucau-agent`) với ngữ cảnh dự án để soát lại yêu cầu. Claude có thể đề xuất bổ sung hoặc điều chỉnh yêu cầu dựa trên thông tin đã có. Ví dụ, Claude Code có thể phân tích ý tưởng ban đầu và sinh ra tài liệu yêu cầu dự án chi tiết cùng tổng quan kiến trúc. Nghiên cứu cho thấy các công cụ AI như ChatGPT giúp giảm thời gian định nghĩa yêu cầu và xác định chính xác nhu cầu người dùng hơn.
- **Checklist:**
  - [ ] Đảm bảo yêu cầu đã đầy đủ, rõ ràng và hiểu được bằng tiếng tự nhiên.
  - [ ] Yêu cầu được lưu trữ trong Markdown, version control cùng code.
  - [ ] Nhờ Claude kiểm tra tính hợp lý và bổ sung các luồng nghiệp vụ nếu thiếu.
- **Ví dụ minh họa:** Giả sử tính năng “Tìm kiếm sản phẩm” – yêu cầu ban đầu: “Người dùng nhập từ khóa, hệ thống trả về danh sách sản phẩm liên quan”. Hỏi Claude: “Có cần gợi ý từ khóa, phân trang kết quả, hay xử lý ngoại lệ khi không tìm thấy?”. Claude sẽ đề xuất các hạng mục bổ sung và soạn thảo `requirements.md` tương ứng.

## 2. Thiết kế hệ thống và kiến trúc
- **Xác định kiến trúc sơ bộ:** Dựa trên yêu cầu, tạo sơ đồ kiến trúc tổng thể (các module, luồng dữ liệu, tích hợp). Có thể dùng các công cụ hỗ trợ vẽ sơ đồ (Mermaid, UML) hoặc hỏi Claude mô tả kiến trúc bằng ngôn ngữ tự nhiên.
- **Lập kế hoạch chi tiết:** Chuyển sang “Plan mode” của Claude Code để chia tính năng thành các công việc nhỏ. Claude sẽ tạo danh sách TO-DO chi tiết, đồ thị phụ thuộc giữa nhiệm vụ, chiến lược kiểm thử và quy trình deploy.
- **Cập nhật tài liệu thiết kế:** Cập nhật file `system_design.md` và `database_design.md` với sơ đồ và mô tả logic. Sử dụng Mermaid hoặc công cụ AI để tạo biểu đồ minh họa (ví dụ flowchart, ERD). Ngoài ra, có thể chia nhỏ các hướng dẫn riêng cho từng phần dự án bằng cách đặt các file `CLAUDE.md` lồng nhau trong các thư mục con.
- **Checklist:**
  - [ ] Bản vẽ kiến trúc hệ thống đã được cập nhật trong tài liệu (sơ đồ thành phần, sequence diagrams,…).
  - [ ] Cấu trúc dữ liệu và sơ đồ cơ sở dữ liệu (`database_design.md`) khớp với yêu cầu.
  - [ ] Tất cả các thay đổi kiến trúc được giải thích rõ trong tài liệu, có minh họa kèm.
- **Ví dụ minh họa:** Với tính năng tìm kiếm, ta có thể yêu cầu Claude “Generate a Mermaid diagram for the search feature workflow” và nhận được sơ đồ luồng người dùng từ nhập từ khóa đến trả kết quả. Claude cũng có thể đề xuất phương án thiết kế cache hay index để tăng tốc tìm kiếm.

## 3. Viết/mở rộng mã nguồn
- **Chia nhỏ công việc:** Theo danh sách TO-DO đã lên kế hoạch, triển khai từng task một. Tạo branch riêng hoặc commit từng phần chức năng, đảm bảo dễ kiểm soát.
- **Dùng Claude để sinh code:** Khi viết code, hãy yêu cầu Claude thực thi một số công việc lặp lại. Ví dụ, dùng Claude subagent (`code-generator`) với ngữ cảnh backend Python để tạo template controller, model, hoặc mã gọi AWS cho phần hạ tầng. Claude Code có thể tự động sinh code, gỡ lỗi ban đầu và tối ưu giải pháp.
- **Ghi chú và commit:** Trong quá trình triển khai, để Claude tự động tạo comment hoặc docstring hữu ích cho hàm, module mới. Sau khi hoàn thành một tính năng con, commit code kèm tin nhắn mô tả chi tiết (hoặc nhờ Claude đề xuất commit message). Đồng thời, hãy yêu cầu Claude cập nhật tài liệu dự án.
- **Checklist:**
  - [ ] Code chạy đúng chức năng, có kèm test cơ bản.
  - [ ] Tất cả logic mới đều có comment, docstring hoặc giải thích trong mã.
  - [ ] Mã nguồn được commit với thông điệp rõ ràng, và các thay đổi code được lưu log trong `CHANGELOG.md` hoặc tương tự.
- **Ví dụ minh họa:** Ở task “API tìm kiếm”, Claude có thể tự động viết code định nghĩa endpoint `/search`, logic truy vấn cơ sở dữ liệu và trả kết quả JSON.

## 4. Review mã nguồn và kiểm thử
- **Code Review tự động:** Sau khi code mới được viết, dùng subagent “code-reviewer” của Claude ngay lập tức để rà soát. Subagent này sẽ chạy `git diff`, tập trung vào file mới và đưa ra checklist: đặt tên biến rõ ràng, tránh trùng lặp, thêm xử lý lỗi, xác thực input, đảm bảo bảo mật dữ liệu…
- **Kiểm thử và sửa lỗi:** Thực thi bộ test (unit, integration) hoặc tự động sinh test case bằng Claude. Ví dụ, yêu cầu Claude “Generate unit tests for search feature” để nhận các kịch bản test mẫu.
- **Checklist:**
  - [ ] Tất cả code mới đều trải qua code review và sửa các vấn đề được nêu ra.
  - [ ] Mọi tính năng mới đều có test tương ứng và passing 100%.
  - [ ] PR bao gồm phần đánh giá/tóm tắt của code-reviewer, khuyến nghị chỉnh sửa (nếu có).

## 5. Tự động cập nhật và duy trì tài liệu
- **Cập nhật tài liệu theo thay đổi:** Mọi thay đổi trong code cần được phản ánh vào tài liệu dự án. Có thể dùng Claude subagent (`doc-updater`) để tự động gợi ý phần cần sửa/tạo.
- **Kiểm tra và hợp nhất docs:** Đưa tài liệu vào quy trình review. Mỗi PR ngoài review code phải có phần review tài liệu.
- **Checklist:**
  - [ ] Tài liệu yêu cầu (`requirements.md`), thiết kế (`system_design.md`), cấu trúc DB, hướng dẫn triển khai… đã được cập nhật phù hợp với mã mới.
  - [ ] Sử dụng công cụ AI kiểm tra chênh lệch giữa code và docs, bổ sung nếu cần.
  - [ ] Mỗi lần merge code, đảm bảo tài liệu liên quan cũng đã được review và merge song hành.

## 6. Lời khuyên đảm bảo tài liệu luôn đồng bộ và duy trì
- **Đóng gói tài liệu cùng mã:** Xem tài liệu như là “code” – lưu trữ vào Git, review cùng pull request.
- **Xây dựng subagent chuyên biệt:** Tạo các subagent Claude có nhiệm vụ riêng như: `yeucau-agent`, `architect-agent`, `code-gen-agent`, `code-reviewer`, `doc-updater`…
- **Viết prompt chi tiết:** Đưa ra hướng dẫn rõ ràng cho Claude và subagents.
- **Kiểm soát công cụ:** Cho phép subagent chỉ truy cập những công cụ cần thiết.
- **Ôn tập định kỳ:** Định kỳ rà soát lại các tài liệu lớn (architecture, README).
