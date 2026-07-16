# Batch PDF OCR → Word + Text (RU/EN)

Локальный пакетный распознаватель PDF в Word (`.docx`) и текст (`.txt`).
Всё считается на вашем ПК — ничего не уходит в облако. Заточен под русский
язык и большие пачки сканов (сотни файлов, тысячи страниц).

*Local batch OCR pipeline: turns folders of scanned/native PDFs into Word +
plain-text, offline, tuned for Russian. Built for large document sets.*

## Возможности

- **Авто-определение типа страницы:** цифровая (есть текстовый слой →
  извлечение через PyMuPDF/pdfplumber, точно) или скан (→ OCR Tesseract `rus+eng`).
- **Устойчивость к большим объёмам и слабой памяти:**
  - потоковая запись текста (память не растёт на длинных томах);
  - постраничная защита — сбой одной страницы не рушит весь файл;
  - каждый файл обрабатывается изолированным процессом, упавший повторяется;
  - число параллельных задач авто-подбирается под свободную RAM;
  - возобновляемость — готовые файлы пропускаются, можно прерывать и продолжать.
- **Выход:** `.txt` (всегда) и `.docx` (Word) на каждый PDF.

## Установка

1. **Python 3.10+**.
2. **Tesseract OCR 5.x** + языковые модели `rus`, `eng`, `osd`
   (рекомендуется лёгкая сборка моделей `tessdata_fast` — меньше памяти).
   Windows: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
3. Зависимости Python:
   ```bash
   python -m venv venv
   venv\Scripts\python -m pip install -r requirements.txt   # Windows
   # source venv/bin/activate && pip install -r requirements.txt  # Linux/macOS
   ```
4. В `convert.py` (вверху) при необходимости поправьте путь к `tesseract.exe`
   (`TESSERACT_EXE`) и папку моделей (`TESSDATA_DIR`).

## Использование

```bash
# Windows: положите PDF в input\ и запустите
run.bat

# или напрямую — устойчивый драйвер (число потоков по свободной памяти):
venv\Scripts\python -u run_all.py

# один файл:
venv\Scripts\python convert.py "path\to\file.pdf" "out_dir"

# вся папка (свой путь):
venv\Scripts\python convert.py "in_dir" "out_dir" [jobs]
```

Результат — в `output/`: `<имя>.txt` и `<имя>.docx` на каждый PDF.

## Параметры (вверху `convert.py`)

| Параметр | Смысл |
|---|---|
| `LANG` | языки OCR (по умолчанию `rus+eng`) |
| `DPI` | разрешение рендера сканов (150 — экономно по памяти; выше = точнее, но тяжелее) |
| `TEXT_LAYER_MIN_CHARS` | порог «цифровая страница vs скан» |
| `DEFAULT_JOBS` | число параллельных задач (драйвер `run_all.py` подбирает сам) |

## Ограничения

- **Плотные табличные сканы** (мелкий шрифт, финотчётность на фотокопиях)
  распознаются ненадёжно — крупный текст читается, структура таблиц теряется.
  Для сложных таблиц специализированные OCR (напр. ABBYY FineReader) точнее.
- Качество зависит от исходного скана: чистый печатный текст — отлично,
  штампы/рукопись/перекосы — хуже.

## Стек

PyMuPDF · pdfplumber · pytesseract (Tesseract) · OpenCV · Pillow · pandas ·
python-docx · openpyxl

## Лицензия

MIT — см. [LICENSE](LICENSE).
