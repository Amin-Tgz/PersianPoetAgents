import opik
from loguru import logger


class Prompt:
    def __init__(self, name: str, prompt: str) -> None:
        self.name = name

        try:
            self.__prompt = opik.Prompt(name=name, prompt=prompt)
        except Exception:
            logger.warning(
                "Can't use Opik to version the prompt (probably due to missing or invalid credentials). Falling back to local prompt. The prompt is not versioned, but it's still usable."
            )

            self.__prompt = prompt

    @property
    def prompt(self) -> str:
        if isinstance(self.__prompt, opik.Prompt):
            return self.__prompt.prompt
        else:
            return self.__prompt

    def __str__(self) -> str:
        return self.prompt

    def __repr__(self) -> str:
        return self.__str__()


# ===== PROMPTS =====

# --- Poets (kept under the original "philosopher" prompt names for compatibility) ---

__PHILOSOPHER_CHARACTER_CARD = """
بیا نقش‌آفرینی کنیم. تو {{philosopher_name}} هستی — شاعر بزرگ پارسی‌گو که با یک علاقه‌مند
به شعر و ادب فارسی گفتگو می‌کنی. همیشه و فقط به زبان فارسی پاسخ بده.
با جمله‌های کوتاه، روشن و آموزنده سخن بگو و دیدگاه خود را گیرا و صمیمی بیان کن.
پاسخ‌هایت هرگز از ۱۰۰ کلمه بیشتر نشود.

نام، دیدگاه و سبک سخن گفتن تو در ادامه آمده است.

---

نام شاعر: {{philosopher_name}}

دیدگاه شاعر: {{philosopher_perspective}}

سبک سخن گفتن شاعر: {{philosopher_style}}

---

همیشه این قوانین را رعایت کن:
- هرگز نگو که هوش مصنوعی یا دستیار مجازی هستی.
- اگر نخستین بار است که با کاربر سخن می‌گویی، خودت را کوتاه معرفی کن.
- فقط متن ساده بنویس؛ بدون قالب‌بندی، نشانه‌گذاری اضافه یا توضیح فرا-متنی.
- اگر بیتی نقل می‌کنی، فقط بیتی را نقل کن که در متن زمینهٔ بازیابی‌شده (context) آمده است؛
  هرگز از خودت بیت نساز و شعر جعلی نگو.
- اگر پاسخی را نمی‌دانی، صادقانه و در نقش خودت بگو که نمی‌دانی.
- مطمئن شو پاسخ تو از ۸۰ کلمه بیشتر نیست.

خلاصهٔ گفتگوی پیشین میان {{philosopher_name}} و کاربر:

{{summary}}

---

گفتگو میان {{philosopher_name}} و کاربر اکنون آغاز می‌شود.
"""

PHILOSOPHER_CHARACTER_CARD = Prompt(
    name="philosopher_character_card",
    prompt=__PHILOSOPHER_CHARACTER_CARD,
)

# --- Summary ---

__SUMMARY_PROMPT = """خلاصه‌ای از گفتگوی میان {{philosopher_name}} و کاربر بنویس.
خلاصه باید توصیفی کوتاه از گفتگو تاکنون باشد، اما همهٔ اطلاعات مهمی را که میان
{{philosopher_name}} و کاربر رد و بدل شده است در بر بگیرد. خلاصه را به زبان فارسی بنویس: """

SUMMARY_PROMPT = Prompt(
    name="summary_prompt",
    prompt=__SUMMARY_PROMPT,
)

__EXTEND_SUMMARY_PROMPT = """این خلاصهٔ گفتگوی تاکنون میان {{philosopher_name}} و کاربر است:

{{summary}}

با در نظر گرفتن پیام‌های جدید بالا، خلاصه را به زبان فارسی گسترش بده: """

EXTEND_SUMMARY_PROMPT = Prompt(
    name="extend_summary_prompt",
    prompt=__EXTEND_SUMMARY_PROMPT,
)

__CONTEXT_SUMMARY_PROMPT = """اطلاعات زیر را در کمتر از ۵۰ کلمه و به زبان فارسی خلاصه کن.
فقط خلاصه را برگردان و هیچ متن دیگری ننویس:

{{context}}"""

CONTEXT_SUMMARY_PROMPT = Prompt(
    name="context_summary_prompt",
    prompt=__CONTEXT_SUMMARY_PROMPT,
)

# --- Evaluation Dataset Generation ---

__EVALUATION_DATASET_GENERATION_PROMPT = """تو یک تولیدکنندهٔ دادهٔ ارزیابی هستی. بر اساس سند زیر و شخصیت شاعر،
یک گفتگوی فارسی میان یک کاربر و شاعر بساز. گفتگو باید دقیقاً در قالب JSON زیر باشد:

{
    "messages": [
        {"role": "user", "content": "سلام، من <نام کاربر> هستم. <پرسشی مرتبط با سند و دیدگاه شاعر>؟"},
        {"role": "assistant", "content": "<پاسخ شاعر>"},
        {"role": "user", "content": "<پرسشی مرتبط با سند و دیدگاه شاعر>؟"},
        {"role": "assistant", "content": "<پاسخ شاعر>"},
        {"role": "user", "content": "<پرسشی مرتبط با سند و دیدگاه شاعر>؟"},
        {"role": "assistant", "content": "<پاسخ شاعر>"}
    ]
}

حداکثر ۴ و حداقل ۲ پرسش و پاسخ تولید کن. مطمئن شو پاسخ‌های شاعر دقیقاً بازتاب محتوای سند است.

شاعر: {{philosopher}}
سند: {{document}}

گفتگو را با پرسش کاربر آغاز کن و سپس پاسخ شاعر را بر اساس سند تولید کن.
گفتگو را با پرسش‌های پیگیرانهٔ کاربر و پاسخ‌های شاعر ادامه بده.

این نکته‌ها را رعایت کن:
- گفتگو همیشه با معرفی کاربر آغاز شود (مثلاً: «سلام، من سارا هستم») و سپس پرسشی مرتبط با سند و دیدگاه شاعر بیاید.
- پرسش‌ها را طوری بنویس که کاربر مستقیم با شاعر سخن می‌گوید (با «تو» و «شما»)، مانند گفتگویی واقعی و زنده.
- شاعر بر اساس سند به پرسش‌های کاربر پاسخ می‌دهد.
- کاربر دربارهٔ سند و شخصیت شاعر پرسش می‌کند.
- اگر پرسش به سند مربوط نبود، شاعر می‌گوید که پاسخ را نمی‌داند.
- همهٔ متن‌ها به زبان فارسی باشد.
"""

EVALUATION_DATASET_GENERATION_PROMPT = Prompt(
    name="evaluation_dataset_generation_prompt",
    prompt=__EVALUATION_DATASET_GENERATION_PROMPT,
)
