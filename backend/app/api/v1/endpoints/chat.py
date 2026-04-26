"""
Food AI Chat Endpoint - Powered by Google Gemini (google-genai SDK)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from google import genai
from google.genai import types
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

# Danh sách model fallback theo thứ tự ưu tiên
# Dùng prefix "models/" để tương thích với google-genai SDK mới
GEMINI_MODELS = [
    "gemini-2.0-flash",          # Ưu tiên 1: nhanh, miễn phí
    "models/gemini-2.5-flash",   # Ưu tiên 2: fallback nếu 2.0 bị rate limit
    "models/gemini-flash-latest", # Ưu tiên 3: luôn dùng phiên bản flash mới nhất
]

router = APIRouter()

# ===================== SYSTEM PROMPT =====================
FOOD_AI_SYSTEM_PROMPT = """Bạn là Food AI Assistant cho ứng dụng gợi ý món ăn cá nhân hóa tại Việt Nam.
Mục tiêu của bạn là giúp người dùng quyết định ăn gì nhanh, đúng mục tiêu, đúng ngân sách, đúng ngữ cảnh thực tế, và học dần theo phản hồi.

## Vai trò chính:
- **Goal-based Recommendation**: gợi ý theo mục tiêu cụ thể, không chỉ theo sở thích chung.
- **Feedback Loop**: sau mỗi gợi ý phải thu phản hồi (hợp/không hợp) và cập nhật hồ sơ sở thích.
- **Smart Combo Suggestion**: luôn có ít nhất 1 combo hoàn chỉnh, thực tế như app thật.

## Các mode bắt buộc hỗ trợ:
1. 🤖 **AI Decision Mode** – "Ăn gì hôm nay?"
2. 📸 **Scan/Realtime** – Phân tích ảnh/video món ăn hoặc quán
3. 🍱 **Combo Generator** – Xây bữa ăn hoàn chỉnh
4. 🗺️ **Food Map Explorer** – Tìm quán theo khu vực
5. 🌟 **Food Discovery** – Khám phá món mới
6. ⚖️ **Comparison Mode** – So sánh các món ăn
7. 🧭 **Journey Mode** – Ẩm thực theo hành trình/lịch trình
8. 🎭 **Mood-based** – Gợi ý theo tâm trạng
9. 📔 **Food Diary** – Nhật ký ăn uống và theo dõi dài hạn

## Cách chọn mode tự động:
- User hỏi chung chung "ăn gì" → AI Decision Mode 🤖
- User gửi ảnh/video món ăn → Scan/Realtime Mode 📸
- User muốn "bữa ăn đủ món", "combo" → Combo Generator 🍱
- User cần tìm quán theo khu vực/địa điểm → Food Map Explorer 🗺️
- User muốn khám phá, thử gì đó mới → Food Discovery 🌟
- User so sánh 2+ món → Comparison Mode ⚖️
- User nói về lịch trình, chuyến đi cả ngày → Journey Mode 🧭
- User đề cập tâm trạng → Mood-based 🎭
- User muốn theo dõi ăn uống lâu dài → Food Diary 📔

## Dữ liệu đầu vào có thể có:
- **user_profile**: khẩu vị, dị ứng, chế độ ăn, bệnh nền, mức chi tiêu.
- **context**: thời gian, vị trí, thời tiết, số người, phương tiện di chuyển.
- **user_goal**: ví dụ "ăn no dưới 50k", "giảm cân", "đi ăn 3 người", "ăn nhanh 20 phút".
- **available_options**: món, quán, khoảng cách, giá, giờ mở cửa.
- **feedback_history**: món đã thích hoặc không thích.
- **food_diary_data**: lịch sử ăn uống gần đây.

## Quy tắc bắt buộc:
1. Ưu tiên mục tiêu user trước.
2. Không bịa dữ liệu. Nếu thiếu dữ liệu quan trọng, hỏi tối đa 2 câu làm rõ.
3. Nếu user có dị ứng hoặc hạn chế ăn uống, ưu tiên an toàn tuyệt đối.
4. Mỗi lần trả lời phải có lý do rõ ràng, chi phí ước tính, mức phù hợp mục tiêu.
5. Luôn có 1 đề xuất tốt nhất, 2–4 lựa chọn thay thế, và ít nhất 1 combo hoàn chỉnh.
6. Luôn kết thúc bằng câu hỏi feedback ngắn: hợp hay không hợp, vì sao.
7. Trả lời ngắn gọn, thực tế, ra quyết định được ngay.
8. Dùng tiếng Việt tự nhiên, thân thiện, chuyên nghiệp.
9. Sử dụng emoji phù hợp để nội dung sinh động.

## Nguyên tắc Combo:
- Mỗi combo = món chính + món phụ + đồ uống (+ tráng miệng nếu phù hợp).
- Tổng giá không vượt ngân sách.
- Combo phải cân bằng: no, ngon, đúng mục tiêu sức khỏe.
- Ví dụ thực tế: Phở bò + giò lụa + Trà đá | Bánh mì thịt + Cà phê sữa đá.

## Định dạng trả lời chuẩn:
🎯 **Mode đang dùng**: [tên mode]
📋 **Nhu cầu**: [tóm tắt ngắn nhu cầu user]

⭐ **Đề xuất tốt nhất**: [Tên món/quán] — ~[giá]k
💡 Lý do: [giải thích ngắn gọn vì sao phù hợp]

🍱 **Combo gợi ý**:
- Món chính: [tên] ~[giá]k
- Món phụ: [tên] ~[giá]k
- Đồ uống: [tên] ~[giá]k
- 💰 Tổng: ~[tổng]k | 🕐 Khi nào nên chọn: [gợi ý]

🔄 **Lựa chọn thay thế**:
1. [Món A] — ~[giá]k — [lý do ngắn]
2. [Món B] — ~[giá]k — [lý do ngắn]
3. [Món C] — ~[giá]k — [lý do ngắn]

💬 **Feedback**: Bạn thấy gợi ý này hợp hay không hợp? Muốn đổi điều gì?

## Ràng buộc an toàn:
- Không đưa lời khuyên y tế tuyệt đối.
- Không khuyến khích hành vi ăn uống cực đoan.
- Nếu có dấu hiệu rối loạn ăn uống hoặc tình trạng sức khỏe nhạy cảm, khuyên user tham khảo chuyên gia phù hợp.
"""


# ===================== SCHEMAS =====================
class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    user_context: Optional[dict] = None  # profile, preferences, etc.


class ChatResponse(BaseModel):
    reply: str
    mode_detected: Optional[str] = None


# ===================== HELPER =====================
def detect_mode(message: str) -> str:
    """Phát hiện mode từ tin nhắn của user"""
    msg = message.lower()
    if any(k in msg for k in ["ăn gì", "an gi", "hôm nay", "đói", "bữa trưa", "bữa tối", "bữa sáng"]):
        return "AI Decision Mode 🤖"
    if any(k in msg for k in ["combo", "bữa đủ", "set", "xây bữa", "thực đơn"]):
        return "Combo Generator 🍱"
    if any(k in msg for k in ["quán", "gần đây", "khu vực", "địa điểm", "tìm quán", "nhà hàng"]):
        return "Food Map Explorer 🗺️"
    if any(k in msg for k in ["mới lạ", "khám phá", "thử món", "chưa ăn", "lạ miệng"]):
        return "Food Discovery 🌟"
    if any(k in msg for k in ["so sánh", "cái nào", "hay hơn", "tốt hơn", "phở hay", "hay bún"]):
        return "Comparison Mode ⚖️"
    if any(k in msg for k in ["hành trình", "chuyến đi", "cả ngày", "lịch trình", "du lịch"]):
        return "Journey Mode 🧭"
    if any(k in msg for k in ["tâm trạng", "mood", "buồn", "vui", "stress", "mệt", "tức", "cô đơn"]):
        return "Mood-based 🎭"
    if any(k in msg for k in ["nhật ký", "theo dõi", "lịch sử ăn", "diary", "calo", "calories"]):
        return "Food Diary 📔"
    return "AI Decision Mode 🤖"


# ===================== ENDPOINT =====================
@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat với Food AI Assistant (Google Gemini)
    - Hỗ trợ multi-turn conversation
    - Tự động nhận diện mode gợi ý
    - Có user context (profile, preferences)
    - Tự động fallback sang model khác nếu bị rate limit
    """
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key chưa được cấu hình. Vui lòng thêm GEMINI_API_KEY vào .env"
        )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Xây dựng lịch sử chat
    gemini_history = []
    for msg in (request.history or []):
        role = "user" if msg.role == "user" else "model"
        gemini_history.append(
            types.Content(
                role=role,
                parts=[types.Part(text=msg.content)]
            )
        )

    # Thêm context user nếu có
    user_message = request.message
    if request.user_context:
        ctx = request.user_context
        context_parts = []
        if ctx.get("name"):
            context_parts.append(f"Tên: {ctx['name']}")
        if ctx.get("budget"):
            context_parts.append(f"Ngân sách: {ctx['budget']}")
        if ctx.get("location"):
            context_parts.append(f"Vị trí: {ctx['location']}")
        if ctx.get("dietary"):
            context_parts.append(f"Chế độ ăn: {ctx['dietary']}")
        if ctx.get("allergies"):
            context_parts.append(f"Dị ứng: {ctx['allergies']}")
        if context_parts:
            user_message = f"[Thông tin người dùng: {', '.join(context_parts)}]\n\n{request.message}"

    # Cấu hình generate
    config = types.GenerateContentConfig(
        system_instruction=FOOD_AI_SYSTEM_PROMPT,
        temperature=0.8,
        max_output_tokens=2048,
    )

    # Gửi request với history
    contents = gemini_history + [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    # Thử từng model theo thứ tự fallback
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            logger.info(f"Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            detected_mode = detect_mode(request.message)
            logger.info(f"Success with model: {model_name}")
            return ChatResponse(
                reply=response.text,
                mode_detected=detected_mode
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Model {model_name} failed: {error_msg}")
            last_error = e

            # Nếu lỗi API key → dừng ngay, không thử model khác
            err_upper = error_msg.upper()
            if "API_KEY" in err_upper or "INVALID_ARGUMENT" in err_upper:
                raise HTTPException(
                    status_code=401,
                    detail=f"Gemini API key không hợp lệ: {error_msg}"
                )

            # Nếu bị rate limit → thử model kế tiếp
            is_rate_limit = (
                "resource_exhausted" in error_msg.lower()
                or "quota" in error_msg.lower()
                or "429" in error_msg
                or "rate" in error_msg.lower()
            )
            if is_rate_limit:
                logger.warning(f"Rate limit on {model_name}, trying next model...")
                await asyncio.sleep(0.5)  # Chờ ngắn trước khi thử model tiếp
                continue

            # Lỗi khác → không thử tiếp
            break

    # Tất cả models đều thất bại
    error_msg = str(last_error) if last_error else "Unknown error"
    err_upper = error_msg.upper()
    if "RESOURCE_EXHAUSTED" in err_upper or "quota" in error_msg.lower() or "429" in error_msg:
        raise HTTPException(
            status_code=429,
            detail="Đã vượt quá giới hạn Gemini API. Vui lòng thử lại sau vài phút."
        )
    raise HTTPException(status_code=500, detail=f"Lỗi AI: {error_msg}")


@router.get("/health")
async def chat_health():
    """Kiểm tra trạng thái kết nối Gemini"""
    has_key = bool(settings.GEMINI_API_KEY)
    return {
        "status": "ready" if has_key else "unconfigured",
        "provider": "Google Gemini",
        "model": "gemini-2.0-flash",
        "sdk": "google-genai",
        "api_key_configured": has_key
    }
