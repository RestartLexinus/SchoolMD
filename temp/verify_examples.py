"""Сверка примеров ошибок: текст трассировки в статье против реального Python.

Для каждой пары «блок ```python с <!-- no-check -->, сразу за ним блок ```text»
запускает код отдельным процессом (как настоящий файл main.py) и сравнивает
последнюю строку трассировки с тем, что написано в статье.

Блоки с turtle пропускаются: они открывают окно. Бесконечные циклы
(while без break) тоже пропускаются — их трассировки в тексте не бывает.

Дополнительно печатает фактический вывод блоков с random.seed(), чтобы сверить
комментарии «# результат» с реальностью.

Запуск: python -X utf8 temp/verify_examples.py "Python/Теория"
"""

import pathlib
import re
import subprocess
import sys
import tempfile

NO_CHECK = "<!-- no-check -->"


def last_error_line(text):
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1].strip() if lines else ""


def is_infinite_loop_demo(block):
    return "while " in block and "break" not in block and "input(" not in block and "for " not in block


def run_as_file(block):
    """Возвращает (stdout, stderr)."""
    with tempfile.TemporaryDirectory() as folder:
        script = pathlib.Path(folder) / "main.py"
        script.write_text(block, encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(script)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
            )
        except subprocess.TimeoutExpired:
            return "", "TIMEOUT"
    return result.stdout, result.stderr


def main(argv):
    root = pathlib.Path(argv[1] if len(argv) > 1 else "Python/Теория")
    problems = 0
    pairs_checked = 0
    seeds_checked = 0
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        blocks = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"```python\n(.*?)```", text, re.S)]
        text_blocks = [(m.start(), m.group(1)) for m in re.finditer(r"```text\n(.*?)```", text, re.S)]
        name = str(path.name)
        for start, end, block in blocks:
            if "turtle" in block:
                continue
            marked = NO_CHECK in text[max(0, start - 80) : start]
            stdout, stderr = run_as_file(block)

            if "random.seed(" in block:
                seeds_checked += 1
                print("SEED OUTPUT", name)
                for line in stdout.splitlines():
                    print("     ", line)
                if stderr:
                    print("   stderr:", last_error_line(stderr))

            following = [(pos, body) for pos, body in text_blocks if pos > end and not text[end:pos].strip()]
            if not following:
                continue
            expected = following[0][1]

            if marked and ("Error" in expected or "Traceback" in expected):
                if is_infinite_loop_demo(block):
                    continue
                pairs_checked += 1
                actual = last_error_line(stderr)
                wanted = last_error_line(expected)
                if not actual:
                    print("MISMATCH (no error raised)", name)
                    print("   expected:", wanted)
                    problems += 1
                elif actual != wanted:
                    print("MISMATCH", name)
                    print("   expected:", wanted)
                    print("   actual  :", actual)
                    problems += 1
    print("---")
    print(
        "tracebacks compared: %d, seed blocks run: %d, problems: %d"
        % (pairs_checked, seeds_checked, problems)
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
