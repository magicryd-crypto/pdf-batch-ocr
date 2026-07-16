# -*- coding: utf-8 -*-
r"""
Устойчивый драйвер пакетного OCR: каждый PDF обрабатывается ОТДЕЛЬНЫМ процессом
(N одновременно). Жёсткое падение одного тома (нехватка памяти в Tesseract) не
валит остальные. Упавший том повторяется один раз; неподдающиеся — в отчёт.

Возобновляемо: тома с готовым .docx пропускаются.

Запуск:  venv\Scripts\python.exe -u run_all.py [N]
"""
import os, sys, glob, subprocess, time, ctypes

BASE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(BASE, "venv", "Scripts", "python.exe")
CONVERT = os.path.join(BASE, "convert.py")
IN = os.path.join(BASE, "input")
OUT = os.path.join(BASE, "output")
GB_PER_WORKER = 1.3  # запас памяти на один процесс OCR (200 DPI, fast-модель)


class _MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_gb():
    m = _MEM(); m.dwLength = ctypes.sizeof(_MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / (1024 ** 3)


# число потоков: из аргумента или авто по свободной памяти (с запасом 0.8 ГБ)
if len(sys.argv) > 1:
    N = max(1, int(sys.argv[1]))
else:
    N = max(1, min(4, int((free_gb() - 0.8) / GB_PER_WORKER)))

os.makedirs(OUT, exist_ok=True)


def is_done(pdf):
    name = os.path.splitext(os.path.basename(pdf))[0]
    return (os.path.exists(os.path.join(OUT, name + ".txt")) or
            os.path.exists(os.path.join(OUT, name + ".docx")))


def main():
    pdfs = sorted(glob.glob(os.path.join(IN, "**", "*.pdf"), recursive=True))
    total = len(pdfs)
    remaining = [p for p in pdfs if not is_done(p)]
    attempts = {p: 0 for p in pdfs}
    print(f"Свободно RAM: {free_gb():.1f} ГБ -> потоков: {N}", flush=True)
    print(f"Всего PDF: {total} | уже готово: {total - len(remaining)} | "
          f"к обработке: {len(remaining)} | одновременно: {N}", flush=True)
    print("-" * 64, flush=True)

    running = {}   # Popen -> pdf
    crashed = []
    t0 = time.time()
    while remaining or running:
        while remaining and len(running) < N:
            p = remaining.pop(0)
            attempts[p] += 1
            po = subprocess.Popen([PY, "-u", CONVERT, p],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            running[po] = p
        time.sleep(2)
        for po in list(running):
            if po.poll() is None:
                continue
            p = running.pop(po)
            if is_done(p):
                done = total - len([x for x in pdfs if not is_done(x)])
                print(f"[{done}/{total}] OK   {os.path.basename(p)}", flush=True)
            else:
                if attempts[p] < 2:
                    print(f"   ↻ повтор (попытка {attempts[p]+1}): {os.path.basename(p)} "
                          f"(exit {po.returncode})", flush=True)
                    remaining.append(p)
                else:
                    print(f"   ✗ НЕ УДАЛОСЬ: {os.path.basename(p)} (exit {po.returncode})", flush=True)
                    crashed.append(p)

    done = total - len([x for x in pdfs if not is_done(x)])
    mins = (time.time() - t0) / 60
    print("-" * 64, flush=True)
    print(f"Готово: {done}/{total} за {mins:.0f} мин.", flush=True)
    if crashed:
        print("Не поддались (нужна прицельная обработка):", flush=True)
        for p in crashed:
            print("   -", os.path.basename(p), flush=True)
    else:
        print("Все тома распознаны.", flush=True)


if __name__ == "__main__":
    main()
