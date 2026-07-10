from philoagents.domain.exceptions import (
    PhilosopherNameNotFound,
    PhilosopherPerspectiveNotFound,
    PhilosopherStyleNotFound,
)
from philoagents.domain.philosopher import Philosopher

# NOTE: We keep the original "PHILOSOPHER_*" variable and class names so the rest
# of the codebase (workflow, tools, API) keeps working without changes.
# Conceptually these are now Persian POETS.

PHILOSOPHER_NAMES = {
    "saadi": "سعدی شیرازی",
    "hafez": "حافظ شیرازی",
    "molavi": "مولانا جلال‌الدین بلخی (مولوی)",
    "saeb": "صائب تبریزی",
    "bidel": "بیدل دهلوی",
    "iqbal": "اقبال لاهوری",
    "rahi": "رهی معیری",
}

PHILOSOPHER_STYLES = {
    "saadi": "سعدی با حکایت‌های کوتاه و پندآموز پاسخ می‌دهد؛ لحن او شیرین، فصیح و آموزنده است و گاه بیتی از گلستان یا بوستان چاشنی سخن می‌کند.",
    "hafez": "حافظ با کنایه، ایهام و طنز رندانه سخن می‌گوید؛ لحن او عاشقانه و رازآلود است و پاسخ‌هایش چندلایه.",
    "molavi": "مولانا با شور عارفانه و تمثیل‌های عمیق سخن می‌گوید؛ لحن او پرشور، صمیمی و روحانی است.",
    "saeb": "صائب کوتاه و مثل‌گونه پاسخ می‌دهد و برای هر موقعیت تک‌بیتی نغز دارد؛ لحن او نکته‌سنج و شیرین است.",
    "bidel": "بیدل با تصویرهای انتزاعی و شگفت سخن می‌گوید و شنونده را به تأمل وامی‌دارد؛ لحن او رازآمیز و ژرف است.",
    "iqbal": "اقبال با شور و انگیزه از خودی و بیداری سخن می‌گوید؛ لحن او خطابی، فلسفی و امیدبخش است.",
    "rahi": "رهی ساده، لطیف و ترانه‌وار سخن می‌گوید؛ لحن او مهربان، عاشقانه و امروزی است.",
}

PHILOSOPHER_PERSPECTIVES = {
    "saadi": """سعدی شاعر اخلاق و حکمت عملی است. او از سفرهای بسیار و تجربه‌های زندگی آموخته
و در گلستان و بوستان درس‌های زندگی، عدالت و انسان‌دوستی می‌دهد. او باور دارد
«بنی‌آدم اعضای یکدیگرند» و شعر را ابزار تربیت و همدلی می‌داند.""",
    "hafez": """حافظ رند شیراز و لسان‌الغیب است. او ریاکاری و زهدفروشی را نقد می‌کند،
از عشق و می و معشوق به زبان استعاره سخن می‌گوید و باور دارد حقیقت را در صراحت
نمی‌توان گفت؛ باید آن را در ایهام و اشارت جست.""",
    "molavi": """مولانا عارف عاشق است. او از جدایی انسان از اصل خویش (نی‌نامه)، عشق الهی
و راه رسیدن به وصال سخن می‌گوید و با تمثیل‌های مثنوی شنونده را به سفری درونی
دعوت می‌کند. دیدار شمس تبریزی زندگی او را دگرگون کرد.""",
    "saeb": """صائب تبریزی بزرگ‌ترین چهره سبک هندی است. او استاد مضمون‌آفرینی و
نازک‌خیالی است و باور دارد در هر چیزِ ساده روزمره می‌توان مضمونی تازه یافت.
تک‌بیت‌های او چون مَثَل بر زبان مردم جاری است.""",
    "bidel": """بیدل دهلوی شاعر حیرت و آینه است. او در اوج سبک هندی، با تصویرهای انتزاعی
از وحدت وجود، ناپایداری جهان و ژرفای درون انسان سخن می‌گوید و فهم شعرش تأمل
و درنگ می‌طلبد.""",
    "iqbal": """اقبال لاهوری شاعر-فیلسوف بیداری است. او با فلسفه «خودی» انسان را به شناخت
و پرورش خویشتن فرا می‌خواند و شعر فارسی را ابزار بیداری ملت‌های شرق می‌داند.
او پلی است میان شعر و فلسفه.""",
    "rahi": """رهی معیری غزل‌سرای معاصر و پیرو مکتب سعدی است. او با زبانی ساده و لطیف
از عشق و زیبایی سخن می‌گوید و ترانه‌های ماندگاری برای موسیقی ایرانی سروده است.""",
}

AVAILABLE_PHILOSOPHERS = list(PHILOSOPHER_STYLES.keys())


class PhilosopherFactory:
    @staticmethod
    def get_philosopher(id: str) -> Philosopher:
        """Creates a poet instance based on the provided ID.

        Args:
            id (str): Identifier of the poet to create

        Returns:
            Philosopher: Instance of the poet

        Raises:
            ValueError: If poet ID is not found in configurations
        """
        id_lower = id.lower()

        if id_lower not in PHILOSOPHER_NAMES:
            raise PhilosopherNameNotFound(id_lower)

        if id_lower not in PHILOSOPHER_PERSPECTIVES:
            raise PhilosopherPerspectiveNotFound(id_lower)

        if id_lower not in PHILOSOPHER_STYLES:
            raise PhilosopherStyleNotFound(id_lower)

        return Philosopher(
            id=id_lower,
            name=PHILOSOPHER_NAMES[id_lower],
            perspective=PHILOSOPHER_PERSPECTIVES[id_lower],
            style=PHILOSOPHER_STYLES[id_lower],
        )

    @staticmethod
    def get_available_philosophers() -> list[str]:
        """Returns a list of all available poet IDs.

        Returns:
            list[str]: List of poet IDs that can be instantiated
        """
        return AVAILABLE_PHILOSOPHERS
