import re
import configparser
from pathlib import Path
from typing import Dict, Tuple
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import sys

# /home/nkmr/lilith_ai/modules/translator.py
# GitHub Copilot
# Класс переводчика на основе NLLB-200 с сохранением фраз в скобках/кавычках/звездочках и т.д.
# Требует: transformers, torch, configparser
# Замена $PLACEHOLDER$: обновлённый класс Translator с сохранением только ограждающих символов,
# при этом содержимое внутри *, (), [], {}, кавычек и т.д. переводится.
class Translator:
    """
    Класс переводит текст с source_lang -> target_lang с помощью модели NLLB-200.
    Сохраняет нетронутыми только ограждающие символы (*, (), [], {}, "", '', ``, «», “ ” и т.п.),
    а текст внутри этих ограждений переводит.
    """
    _PROTECT_PATTERN = re.compile(
        r'(\*[^*]+\*|\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|«[^»]*»|“[^”]*”|"[^"]*"|\'[^\']*\'|`[^`]*`)',
        re.MULTILINE,
    )

    def __init__(self, config_path: str = "config.ini", model_name: str = "facebook/nllb-200-distilled-600M"):
        cfg = configparser.ConfigParser()
        read_files = cfg.read(config_path)
        if not read_files:
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        if "translator" not in cfg:
            raise KeyError("Config file must contain [translator] section with source_lang and target_lang")

        src = cfg["translator"].get("source_lang")
        tgt = cfg["translator"].get("target_lang")
        if not src or not tgt:
            raise KeyError("translator.source_lang and translator.target_lang must be set in config.ini")

        self.source_lang = self._normalize_lang(src)
        self.target_lang = self._normalize_lang(tgt)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Принудительный BOS для целевого языка (NLLB-специфика)
        try:
            self.forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(self.target_lang)
        except Exception:
            # fallback: None (модель/токенизатор может не требовать)
            self.forced_bos_token_id = None

    @staticmethod
    def _normalize_lang(code: str) -> str:
        code = code.strip()
        if "_" in code:
            return code  # считаем, что это уже NLLB-код вида eng_Latn
        code_lower = code.lower()
        if code_lower in _SIMPLE_LANG_MAP:
            return _SIMPLE_LANG_MAP[code_lower]
        raise ValueError(f"Не удалось сопоставить язык '{code}'. Укажите полный NLLB-код (например 'eng_Latn') или один из: {', '.join(sorted(_SIMPLE_LANG_MAP.keys()))}")

    def translate(self, text: str, max_length: int = 512, **generate_kwargs) -> str:
        """
        Переводит текст, переводя содержимое внутри ограждений, но оставляя сами ограждающие
        символы (например звездочки, скобки, кавычки) нетронутыми.
        """
        if not text:
            return text

        gen_kwargs = dict(max_length=max_length, num_beams=4)
        if self.forced_bos_token_id is not None:
            gen_kwargs["forced_bos_token_id"] = self.forced_bos_token_id
        gen_kwargs.update(generate_kwargs)

        parts = self._PROTECT_PATTERN.split(text)
        translated_parts = []

        for part in parts:
            if not part:
                translated_parts.append(part)
                continue

            # Если часть полностью соответствует защищённому шаблону,
            # то переводим внутреннее содержимое, оставляя ограждающие символы.
            if self._PROTECT_PATTERN.fullmatch(part):
                # разделим на ограждающий символ(ы) и содержимое
                opener = part[0]
                closer = part[-1]
                inner = part[1:-1]

                # если внутри нет текста — оставляем как есть
                if not inner.strip():
                    translated_parts.append(part)
                    continue

                m = re.match(r'^(\s*)(.*?)(\s*)$', inner, re.DOTALL)
                if m:
                    lead, core, trail = m.groups()
                else:
                    lead, core, trail = "", inner, ""

                if core == "":
                    translated_parts.append(part)
                    continue

                inputs = self.tokenizer(core, return_tensors="pt", truncation=True, max_length=max_length)
                outputs = self.model.generate(**inputs, **gen_kwargs)
                decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

                translated_parts.append(f"{opener}{lead}{decoded}{trail}{closer}")
                continue

            # Иначе переводим как обычно (учитываем ведущие/замыкающие пробелы)
            m = re.match(r'^(\s*)(.*?)(\s*)$', part, re.DOTALL)
            if m:
                lead, core, trail = m.groups()
            else:
                lead, core, trail = "", part, ""

            if core == "":
                translated_parts.append(part)
                continue

            inputs = self.tokenizer(core, return_tensors="pt", truncation=True, max_length=max_length)
            outputs = self.model.generate(**inputs, **gen_kwargs)
            decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

            translated_parts.append(lead + decoded + trail)

        return "".join(translated_parts)

def translate(self, text: str, max_length: int = 512, **generate_kwargs) -> str:
    """
    Переводит текст, но теперь переводит также содержимое защищённых фрагментов
    (внутри *, (), [], {}, "", '', ``, «», “ ” и т.п.), сохраняя сами ограждающие
    символы нетронутыми.
    """
    if not text:
        return text

    gen_kwargs = dict(forced_bos_token_id=self.forced_bos_token_id, max_length=max_length, num_beams=4)
    gen_kwargs.update(generate_kwargs)

    parts = self._PROTECT_PATTERN.split(text)
    translated_parts = []

    for part in parts:
        if not part:
            translated_parts.append(part)
            continue

        # если часть полностью соответствует шаблону защиты, переводим внутренность,
        # но оставляем ограждающие символы
        if self._PROTECT_PATTERN.fullmatch(part):
            # разделим на ограждающий символ(ы) и содержимое
            opener = part[0]
            closer = part[-1]
            inner = part[1:-1]

            # если внутри нет текста — оставляем как есть
            if not inner.strip():
                translated_parts.append(part)
                continue

            m = re.match(r'^(\s*)(.*?)(\s*)$', inner, re.DOTALL)
            if m:
                lead, core, trail = m.groups()
            else:
                lead, core, trail = "", inner, ""

            if core == "":
                translated_parts.append(part)
                continue

            inputs = self.tokenizer(core, return_tensors="pt", truncation=True, max_length=max_length)
            outputs = self.model.generate(**inputs, **gen_kwargs)
            decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

            # собираем обратно: opener + lead + decoded + trail + closer
            translated_parts.append(f"{opener}{lead}{decoded}{trail}{closer}")
            continue

        # иначе переводим как раньше (части между защищёнными фрагментами)
        m = re.match(r'^(\s*)(.*?)(\s*)$', part, re.DOTALL)
        if m:
            lead, core, trail = m.groups()
        else:
            lead, core, trail = "", part, ""

        if core == "":
            translated_parts.append(part)
            continue

        inputs = self.tokenizer(core, return_tensors="pt", truncation=True, max_length=max_length)
        outputs = self.model.generate(**inputs, **gen_kwargs)
        decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

        translated_parts.append(lead + decoded + trail)

    return "".join(translated_parts)

# Простая таблица соответствия двухбуквенных кодов -> NLLB-200 кодов.
# Если в config указан полный код вида "eng_Latn", он используется напрямую.
_SIMPLE_LANG_MAP = {
    "en": "eng_Latn",
    "ru": "rus_Cyrl",
    "uk": "ukr_Cyrl",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "de": "deu_Latn",
    "pt": "por_Latn",
    "it": "ita_Latn",
    "zh": "zho_Hans",
    "ar": "ara_Arab",
    "hi": "hin_Deva",
    # при необходимости дополняйте
}


# class Translator:
#     """
#     Класс переводит текст с source_lang -> target_lang с помощью модели NLLB-200.
#     Сохраняет нетронутыми фрагменты, взятые в: *, (), [], {}, "", '', ``, «», кавычки-ёлочки.
#     Конфигурация читается из config.ini: секция [translator], ключи source_lang и target_lang.
#     """

#     _PROTECT_PATTERN = re.compile(
#         r'(\*[^*]+\*|\([^)]*\)|\[[^\]]*\]|\{[^}]*\}|«[^»]*»|“[^”]*”|"[^"]*"|\'[^\']*\'|`[^`]*`)',
#         re.MULTILINE,
#     )

#     def __init__(self, config_path: str = "config.ini", model_name: str = "facebook/nllb-200-distilled-600M"):
#         cfg = configparser.ConfigParser()
#         read_files = cfg.read(config_path)
#         if not read_files:
#             raise FileNotFoundError(f"Config file not found at: {config_path}")

#         if "translator" not in cfg:
#             raise KeyError("Config file must contain [translator] section with source_lang and target_lang")

#         src = cfg["translator"].get("source_lang")
#         tgt = cfg["translator"].get("target_lang")
#         if not src or not tgt:
#             raise KeyError("translator.source_lang and translator.target_lang must be set in config.ini")

#         self.source_lang = self._normalize_lang(src)
#         self.target_lang = self._normalize_lang(tgt)

#         # Загрузка модели и токенизатора
#         self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#         # у NLLB-tokenizer есть map lang_code_to_id; устанавливаем поведение
#         # Если источник/цель заданы пользователем, убедимся что такой ключ есть
#         # if not hasattr(self.tokenizer, "lang_code_to_id"):
#         #     raise RuntimeError("Tokenizer does not support lang_code_to_id mapping required for NLLB models")

#         # if self.target_lang not in self.tokenizer.lang_code_to_id:
#         #     raise ValueError(f"Target language code '{self.target_lang}' not recognized by tokenizer")

#         # # установить исходный язык (некоторые версии токенизаторов используют это поле)
#         # try:
#         #     self.tokenizer.src_lang = self.source_lang
#         # except Exception:
#         #     pass

#         self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

#         # forced_bos_token_id принудительно ставит токен начала для целевого языка (NLLB специфично)
#         self.forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(self.target_lang)

#     @staticmethod
#     def _normalize_lang(code: str) -> str:
#         code = code.strip()
#         if "_" in code:
#             return code  # считаем, что это уже NLLB-код вида eng_Latn
#         code_lower = code.lower()
#         if code_lower in _SIMPLE_LANG_MAP:
#             return _SIMPLE_LANG_MAP[code_lower]
#         raise ValueError(f"Не удалось сопоставить язык '{code}'. Укажите полный NLLB-код (например 'eng_Latn') или один из: {', '.join(sorted(_SIMPLE_LANG_MAP.keys()))}")

#     def _protect_spans(self, text: str) -> Tuple[str, Dict[str, str]]:
#         """
#         Заменяет все фрагменты, подходящие под шаблон, на плейсхолдеры.
#         Возвращает (masked_text, mapping placeholder->original).
#         """
#         mapping = {}
#         parts = []
#         last = 0
#         idx = 0
#         for m in self._PROTECT_PATTERN.finditer(text):
#             start, end = m.span()
#             # добавляем промежуток между предыдущим матчем и текущим
#             parts.append(text[last:start])
#             placeholder = f"<<<PROT_{idx}>>>"
#             parts.append(placeholder)
#             mapping[placeholder] = m.group(0)
#             last = end
#             idx += 1
#         parts.append(text[last:])
#         masked = "".join(parts)
#         return masked, mapping

#     def _restore_spans(self, text: str, mapping: Dict[str, str]) -> str:
#         # Простая замена плейсхолдеров на оригинальные фрагменты
#         for ph, orig in mapping.items():
#             text = text.replace(ph, orig)
#         return text

#     def translate(self, text: str, max_length: int = 512, **generate_kwargs) -> str:
#         """
#         Переводит текст, сохраняя защищённые фрагменты.
#         Дополнительные параметры генерации можно передавать в generate_kwargs.
#         Реализация теперь разбивает исходный текст на сегменты (защищённые и незащищённые),
#         переводит только незащищённые сегменты по отдельности и затем собирает результат,
#         чтобы защита фрагментов оставалась точной и не зависела от поведения токенизатора.
#         """
#         if not text:
#             return text

#         # Параметры генерации для модели
#         gen_kwargs = dict(forced_bos_token_id=self.forced_bos_token_id, max_length=max_length, num_beams=4)
#         gen_kwargs.update(generate_kwargs)

#         parts = self._PROTECT_PATTERN.split(text)
#         translated_parts = []

#         for part in parts:
#             if not part:
#                 # пустая строка — просто добавляем
#                 translated_parts.append(part)
#                 continue

#             # Если часть полностью соответствует защищённому шаблону — оставляем её как есть
#             if self._PROTECT_PATTERN.fullmatch(part):
#                 translated_parts.append(part)
#                 continue

#             # Иначе переводим только "содержимую" часть, сохраняя ведущие/замыкающие пробелы
#             m = re.match(r'^(\s*)(.*?)(\s*)$', part, re.DOTALL)
#             if m:
#                 lead, core, trail = m.groups()
#             else:
#                 lead, core, trail = "", part, ""

#             if core == "":
#                 translated_parts.append(part)
#                 continue

#             inputs = self.tokenizer(core, return_tensors="pt", truncation=True, max_length=max_length)
#             outputs = self.model.generate(**inputs, **gen_kwargs)
#             decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

#             translated_parts.append(lead + decoded + trail)

#         return "".join(translated_parts)


if __name__ == "__main__":
    # Мини-тест, выполняемый при запуске модуля как скрипта.
    # Требуется наличие config.ini рядом или в CWD с секцией [translator].
    # Пример config.ini:
    # [translator]
    # source_lang = en
    # target_lang = ru

    try:
        cfg_path = Path("config.ini")
        if not cfg_path.exists():
            print("config.ini не найден в текущей директории. Создайте файл с секцией [translator].")
            sys.exit(2)

        t = Translator(config_path=str(cfg_path))
        sample = 'This is a test sentence with *protected phrase*, a (bracketed part), and "quoted text".'
        print("ORIGINAL:")
        print(sample)
        print("\nTRANSLATED:")
        print(t.translate(sample))
    except Exception as e:
        print(f"Error during test run: {e}")
        sys.exit(1)