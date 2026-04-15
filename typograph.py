#!/usr/bin/env python3
"""
Типограф — расставляет неразрывные пробелы в HTML-файлах.
Не трогает кавычки, тире, многоточия — тексты уже написаны правильно.
"""
import re, os, sys

NBSP = '\u00a0'

def typograph_text(text):
    # После коротких предлогов, союзов, частиц
    prep = r'\b(в|во|на|не|ни|но|из|и|к|о|об|от|по|до|при|про|за|со|а|бы|же|ли|их|как|что|это|или|уже|ещё|еще|чем|так|он|она|оно|они|мы|вы|я|для|без|над|под)\s'
    text = re.sub(prep, lambda m: m.group(1) + NBSP, text, flags=re.IGNORECASE)
    # Перед % ₽ и единицами
    text = re.sub(r'(\d) (%|₽|руб|тыс|млн|млрд|кг|км|см|мм|шт)', r'\1' + NBSP + r'\2', text)
    return text

def process_html(html):
    protected = []
    def protect(m):
        protected.append(m.group(0))
        return f'\x00PROT{len(protected)-1}\x00'
    html = re.sub(r'<script[\s\S]*?</script>', protect, html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', protect, html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', protect, html)
    html = typograph_text(html)
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
        targets = ['index.html', 'blog.html']
        for d in ['posts', 'blog']:
            if os.path.isdir(d):
                targets += [f'{d}/{f}' for f in os.listdir(d) if f.endswith('.html')]
    changed = 0
    for path in targets:
        if os.path.exists(path) and process_file(path):
            changed += 1
            print(f'  ✓ {path}')
    print(f'\nОбработано: {len(targets)}, изменено: {changed}')

if __name__ == '__main__':
    main()
