#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║                 🎹 NARAKA MUSIC PLAYER 🎹                        ║
║           Воспроизведение песен из файлов (JSON/TXT)            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import time
import json
import os
import subprocess
import sys
import threading

# ==================== ТВОЯ РАСКЛАДКА (Naraka) ====================
# Карта соответствия нот из файла клавишам на клавиатуре
KEY_MAP = {
    # Верхний ряд (Q..U)
    "1Key0": "q",   # do
    "1Key1": "w",   # re
    "1Key2": "e",   # mi
    "1Key3": "r",   # fa
    "1Key4": "t",   # so
    "1Key5": "y",   # la
    "1Key6": "u",   # ti
    
    # Средний ряд (A..J)
    "1Key7": "a",   # do
    "1Key8": "s",   # re
    "1Key9": "d",   # mi
    "1Key10": "f",  # fa
    "1Key11": "g",  # so
    "1Key12": "h",  # la
    "1Key13": "j",  # ti
    
    # Нижний ряд (Z..M)
    "1Key14": "z",  # do
    "1Key15": "x",  # re
    "1Key16": "c",  # mi
    "1Key17": "v",  # fa
    "1Key18": "b",  # so
    "1Key19": "n",  # la
    "1Key20": "m",  # ti
}
# =============================================================

# Цвета для красивого вывода (можно не менять)
CYAN = '\033[96m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_banner():
    os.system('clear')
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════════╗
║                 🎹 NARAKA MUSIC PLAYER 🎹                        ║
║           Воспроизведение песен из файлов (JSON/TXT)            ║
╚══════════════════════════════════════════════════════════════════╝{RESET}
    """)
    print(f"{BOLD}{MAGENTA}🐙 GitHub:{RESET} {CYAN}https://github.com/web-pentest{RESET}")
    print(f"{BOLD}{YELLOW}❄️  Проекты:{RESET} {GREEN}DarkVPN • TSandCode • PHPNoFluff • SNOWRECON{RESET}\n")

def send_key(key):
    """Эмулирует нажатие клавиши через xdotool"""
    subprocess.run(['xdotool', 'keydown', key])
    time.sleep(0.02)
    subprocess.run(['xdotool', 'keyup', key])

def find_notes(data):
    """Рекурсивно ищет ноты в JSON-файлах песен для Sky"""
    if isinstance(data, list):
        if any(isinstance(i, dict) and 'time' in i and 'key' in i for i in data):
            return data
        for item in data:
            res = find_notes(item)
            if res:
                return res
    elif isinstance(data, dict):
        for key in ['songNotes', 'notes', 'events', 'data']:
            if key in data and isinstance(data[key], list):
                notes = find_notes(data[key])
                if notes:
                    return notes
        for val in data.values():
            res = find_notes(val)
            if res:
                return res
    return None

def play_song(file_path):
    """Основная функция воспроизведения песни"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"{RED}❌ Ошибка чтения файла {file_path}: {e}{RESET}")
        return

    notes = find_notes(raw_data)
    if not notes:
        print(f"{RED}❌ Не найдены ноты в файле {file_path}{RESET}")
        return

    total_notes = len(notes)
    total_time_ms = max((n.get('time', 0) for n in notes), default=0)
    total_seconds = total_time_ms / 1000.0

    print(f"\n{GREEN}🎵 Песня:{RESET} {YELLOW}{os.path.basename(file_path)}{RESET}")
    print(f"{GREEN}🎼 Нот:{RESET} {YELLOW}{total_notes}{RESET}")
    print(f"{GREEN}⏱️  Длительность:{RESET} {YELLOW}{total_seconds:.1f} сек{RESET}")
    print(f"{YELLOW}⏳ 5 секунд до старта...{RESET}")

    for i in range(5, 0, -1):
        print(f"\r   Старт через {i}... ", end='', flush=True)
        time.sleep(1)
    print(f"\r{GREEN}▶️ ИГРАЮ!{RESET} (жми Ctrl+C для остановки)\n")

    start_time = time.time()
    played_notes = 0

    def progress_updater():
        nonlocal played_notes
        while time.time() - start_time < total_seconds:
            elapsed = time.time() - start_time
            progress = min(elapsed / total_seconds, 1.0)
            bar_length = 30
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{BOLD}{GREEN}[{bar}]{RESET} {BOLD}{GREEN}{int(progress * 100)}%{RESET}", end='', flush=True)
            time.sleep(0.2)
        bar = '█' * 30
        print(f"\r{BOLD}{GREEN}[{bar}]{RESET} {BOLD}{GREEN}100%{RESET}", end='', flush=True)
        print()

    progress_thread = threading.Thread(target=progress_updater, daemon=True)
    progress_thread.start()

    try:
        for note in notes:
            if 'time' not in note:
                continue
            target_time = note['time'] / 1000.0
            while (time.time() - start_time) < target_time:
                time.sleep(0.001)
            key_val = str(note.get('key', ''))
            if not key_val.startswith('1Key') and key_val.isdigit():
                key_val = f"1Key{key_val}"
            key = KEY_MAP.get(key_val)
            if key:
                send_key(key)
            played_notes += 1
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⏹ Воспроизведение остановлено пользователем.{RESET}")
        return

    print(f"\n{GREEN}✅ Воспроизведение завершено!{RESET}\n")

def main():
    while True:
        files = []
        for f in os.listdir('.'):
            if f.endswith(('.txt', '.json')):
                files.append(f)
        if os.path.isdir('songs'):
            for f in os.listdir('songs'):
                if f.endswith(('.txt', '.json')):
                    files.append(os.path.join('songs', f))

        if not files:
            print(f"{RED}❌ Нет .txt или .json файлов с песнями!{RESET}")
            break

        print(f"\n{BOLD}{CYAN}📁 Доступные песни:{RESET}")
        for i, filename in enumerate(files, 1):
            short = os.path.basename(filename)
            print(f"  {BOLD}{i}.{RESET} {short}")
        print(f"  {BOLD}{RED}0. Выход{RESET}")

        try:
            choice = input(f"\n{BOLD}{CYAN}🎤 Выбери номер: {RESET}")
            if choice == '0':
                print(f"\n{GREEN}❄️ Спасибо за использование! 🐙 github.com/web-pentest{RESET}\n")
                break

            idx = int(choice) - 1
            if 0 <= idx < len(files):
                play_song(files[idx])
            else:
                print(f"{RED}⚠️ Неверный номер.{RESET}")
        except ValueError:
            print(f"{RED}⚠️ Введи число.{RESET}")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Выход.{RESET}")
            break

if __name__ == "__main__":
    print_banner()
    main()
