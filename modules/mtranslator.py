import re
from transformers import MarianMTModel, MarianTokenizer

class Translator:
    def __init__(self):
        self.en_to_ru_model_name = 'Helsinki-NLP/opus-mt-en-ru'
        self.ru_to_en_model_name = 'Helsinki-NLP/opus-mt-ru-en'

        self.en_to_ru_tokenizer = MarianTokenizer.from_pretrained(self.en_to_ru_model_name)
        self.en_to_ru_model = MarianMTModel.from_pretrained(self.en_to_ru_model_name)

        self.ru_to_en_tokenizer = MarianTokenizer.from_pretrained(self.ru_to_en_model_name)
        self.ru_to_en_model = MarianMTModel.from_pretrained(self.ru_to_en_model_name)

        # Паттерн для спецтегов: *...*, [...], {...}, включая вложенные
        self.pattern = re.compile(r'(\*[^*]+\*|\[[^\]]+\]|\{[^}]+\})')

    def translate_segment(self, text, model, tokenizer):
        if not text.strip():
            return text
        inputs = tokenizer(text, return_tensors="pt", padding=True)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)

    def translate_text(self, text, direction='en-ru'):
        if direction == 'en-ru':
            model = self.en_to_ru_model
            tokenizer = self.en_to_ru_tokenizer
        else:
            model = self.ru_to_en_model
            tokenizer = self.ru_to_en_tokenizer

        # Разбиваем текст на сегменты: спецтеги и обычный текст
        segments = self.pattern.split(text)
        translated_segments = []

        for seg in segments:
            if not seg:
                continue
            if self.pattern.fullmatch(seg):
                # Спецтег: переводим текст внутри рекурсивно
                inner = seg[1:-1]
                translated_inner = self.translate_text(inner, direction)
                translated_segments.append(f"{seg[0]}{translated_inner}{seg[-1]}")
            else:
                # Обычный текст
                translated_segments.append(self.translate_segment(seg, model, tokenizer))

        # Восстанавливаем пробелы между сегментами, если их изначально не было
        result = ''
        for i, seg in enumerate(translated_segments):
            if i > 0 and not seg.startswith((' ', '*', '[', '{')) and not result.endswith(' '):
                result += ' '
            result += seg

        return result

    def user_to_ai(self, text):
        return self.translate_text(text, direction='ru-en')

    def ai_to_user(self, text):
        return self.translate_text(text, direction='en-ru')


if __name__ == "__main__":
    translator = Translator()
    user_text = "Привет, как дела?"
    ai_text = "*smiles warmly* I'm fine, thank you! How about you? *waves*"

    print("User → AI:", translator.user_to_ai(user_text))
    print("AI → User:", translator.ai_to_user(ai_text))
