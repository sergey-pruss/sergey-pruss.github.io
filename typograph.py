#!/usr/bin/env python3
"""
Типограф — применяет правила русской типографики к HTML-файлам.
Обрабатывает только текстовые ноды, не трогает теги и атрибуты.
"""
import re
import os
import sys

NBSP = '\u00a0'  # неразрывный пробел

def typograph_text(text):
    """Применяет типографические правила к чистому тексту."""

    # 1. Многоточие
    text = re.sub(r'\.\.\.', '…', text)

    # 2. Кавычки "..." → «...»
    # Простая замена парных кавычек
    def replace_quotes(t):
        result = []
        open_q = True
        i = 0
        while i < len(t):
            c = t[i]
            if c == '"':
                result.append('«' if open_q else '»')
                open_q = not open_q
            else:
                result.append(c)
            i += 1
        return ''.join(result)
    text = replace_quotes(text)

    # 3. Тире: пробел-дефис-пробел → пробел-тире-пробел
    text = re.sub(r' - ', ' — ', text)
    # В начале строки
    text = re.sub(r'^- ', '— ', text, flags=re.MULTILINE)

    # 4. Неразрывный пробел после коротких предлогов и союзов
    prepositions = r'\b(в|во|на|не|ни|но|из|из-за|из-под|и|к|о|об|от|по|до|при|про|за|со|а|бы|же|ли|их|как|что|это|или|уже|ещё|еще|чем|так|он|она|оно|они|мы|вы|я)\s'
    text = re.sub(prepositions, lambda m: m.group(1) + NBSP, text, flags=re.IGNORECASE)

    # 5. Неразрывный пробел перед % ₽ и единицами измерения
    text = re.sub(r'(\d)\s+(%|₽|руб|тыс|млн|млрд|кг|км|см|мм|л|шт)', r'\1' + NBSP + r'\2', text)

    # 6. Дефис между числами (диапазон): 1-2 → 1–2
    text = re.sub(r'(\d)-(\d)', r'\1–\2', text)

    return text


def process_html(html):
    """
    Обрабатывает HTML: применяет типографику только к текстовым нодам,
    не трогая теги, атрибуты, скрипты, стили.
    """
    # Сохраняем блоки которые не нужно трогать
    protected = []

    def protect(m):
        protected.append(m.group(0))
        return f'\x00PROT{len(protected)-1}\x00'

    # Защищаем: <script>, <style>, HTML-теги, атрибуты
    html = re.sub(r'<script[\s\S]*?</script>', protect, html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', protect, html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', protect, html)

    # Применяем типографику к оставшемуся тексту
    html = typograph_text(html)

    # Восстанавливаем защищённые блоки
    for i, block in enumerate(protected):
        html = html.replace(f'\x00PROT{i}\x00', block)

    return html


def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    result = process_html(original)
    if result != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(result)
        return True
    return False


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else []

    if not targets:
        # По умолчанию — все HTML файлы сайта
        targets = ['index.html', 'blog.html']
        for f in os.listdir('posts/'):
            if f.endswith('.html'):
                targets.append(f'posts/{f}')

    changed = 0
    for path in targets:
        if os.path.exists(path):
            if process_file(path):
                changed += 1
                print(f'  ✓ {path}')

    print(f'\nОбработано файлов: {len(targets)}, изменено: {changed}')


if __name__ == '__main__':
    main()
