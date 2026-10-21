"""Проверка относительных ссылок в Markdown-файлах курса.

Ищет ссылки вида [текст](путь/файл.md) и проверяет, что файл существует.
Внешние ссылки (http/https), анкоры (#...) и почта пропускаются.

Запуск из корня репозитория:
    python -X utf8 temp/check_links.py Python
"""

import pathlib
import re
import sys

LINK = re.compile(r"\]\(([^)\s]+)\)")


def main(argv):
    root = pathlib.Path(argv[1] if len(argv) > 1 else "Python")
    files = sorted(root.rglob("*.md"))
    problems = 0
    checked = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        # примеры внутри ```-блоков ссылками не считаются
        text = re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.S | re.M)
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#")[0]
            if not clean:
                continue
            checked += 1
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                problems += 1
                name = str(path.relative_to(root)).encode("ascii", "replace").decode("ascii")
                bad = clean.encode("ascii", "replace").decode("ascii")
                print("BROKEN", name, "->", bad)
    print("---")
    print("files: %d, links checked: %d, broken: %d" % (len(files), checked, problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
