def build_create_prompt(p: dict) -> str:
    idea   = p.get("idea","")
    style  = p.get("style","trung tính")
    words  = int(p.get("length_words", 800))
    notes  = p.get("notes","")
    return f"""Bạn là biên kịch chuyên nghiệp. Hãy viết kịch bản bằng tiếng Việt (~{words} từ), phong cách {style}.
Yêu cầu:
- Mạch lạc, có mở đầu - cao trào - kết thúc
- Lời thoại tự nhiên, rõ tên nhân vật
- Dàn ý rõ ràng theo mục

Ý tưởng: {idea}

Ghi chú đặc biệt:
{notes}
"""
    
def build_podcast_prompt(p: dict) -> str:
    topic  = p.get("topic","chủ đề bất kỳ")
    style  = p.get("style","Trò chuyện thân mật")
    roles  = p.get("characters",[["Host","dẫn dắt"], ["Khách","chia sẻ"]])
    roles_str = "\n".join([f"- {n}: {d}" for n,d in roles])
    return f"""Bạn là nhà sản xuất podcast. Hãy viết kịch bản đối thoại tự nhiên, có mở đầu, thân bài, kết thúc.
Chủ đề: {topic}
Phong cách: {style}
Nhân vật:
{roles_str}

Yêu cầu: lời thoại tự nhiên, chèn cue chuyển cảnh ngắn, tổng thể gọn gàng.
"""

def build_rewrite_prompt(p: dict) -> str:
    text   = p.get("text","")
    tone   = p.get("tone","tự nhiên")
    target = p.get("target","ngắn gọn, dễ hiểu")
    return f"""Hãy viết lại đoạn sau bằng tiếng Việt, giữ ý chính, giọng {tone}, mục tiêu {target}.
---
{text}
---
"""
