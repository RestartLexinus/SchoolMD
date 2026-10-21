"""Проверка статей Python/Теория.

Что проверяет:
  1. Каждый блок ```python компилируется (кроме помеченных <!-- no-check -->).
  2. Блоки без input()/open()/turtle/time.sleep выполняются и не падают.
  3. Ссылки оглавления (#anchor) ведут на существующие заголовки.
  4. В заголовках ## и глубже нет эмодзи и символов, которые ломают анкоры.

Блок, который специально не запускается (например, бесконечный цикл
в разделе «Типичные ошибки»), помечается строкой <!-- no-check -->
на отдельной строке прямо перед открывающими ```python.

Запуск (из корня репозитория):
    python -X utf8 temp/check_theory.py "Python/Теория"
    python -X utf8 temp/check_theory.py "Python/Теория/003_Python_Циклы.md"

Код возврата 1, если найдены проблемы.
"""

import contextlib
import io
import pathlib
import re
import sys

# В заголовках ##+ разрешены буквы, цифры, пробелы и . , : - _
ALLOWED_HEADING = re.compile(r"[^\w\s.,:\-]", re.UNICODE)
NO_CHECK = "<!-- no-check -->"


class CappedOutput(io.StringIO):
    """Заглушка stdout: не даёт бесконечному print съесть память."""

    limit = 20000

    def write(self, value):
        if self.tell() > self.limit:
            raise RuntimeError("__ENDLESS_OUTPUT__")
        return super().write(value)


def make_slug(text):
    """Приближение slug-генератора GitHub для заголовка."""
    out = []
    for ch in text.strip().lower():
        if ch.isalnum() or ch in ("_", "-"):
            out.append(ch)
        elif ch == " ":
            out.append("-")
    return "".join(out).strip("-")


def ascii_safe(value):
    return str(value).encode("ascii", "replace").decode("ascii")


def check_file(path):
    problems = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # --- заголовки и анкоры ---
    headings = {}
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        slug = make_slug(title)
        if slug in headings:
            problems.append(
                "duplicate heading slug #%s (lines %d and %d)" % (slug, headings[slug], number)
            )
        headings[slug] = number
        if level >= 2 and ALLOWED_HEADING.search(title):
            problems.append(
                "heading line %d has punctuation/emoji that breaks anchors: %s"
                % (number, ascii_safe(title))
            )

    for number, line in enumerate(lines, start=1):
        for target in re.findall(r"\]\(#([^)]+)\)", line):
            if target not in headings:
                problems.append(
                    "line %d: TOC link #%s has no matching heading" % (number, ascii_safe(target))
                )

    # --- оглавление должно совпадать с ##-разделами ---
    level2 = []
    toc_links = []
    seen_first_heading = False
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading and len(heading.group(1)) == 2:
            seen_first_heading = True
            level2.append(make_slug(heading.group(2).strip()))
        elif not seen_first_heading:
            toc_links.extend(re.findall(r"\]\(#([^)]+)\)", line))

    if level2:
        if toc_links != level2:
            missing = [slug for slug in level2 if slug not in toc_links]
            extra = [slug for slug in toc_links if slug not in level2]
            if missing:
                problems.append("TOC misses sections: %s" % ", ".join(ascii_safe(s) for s in missing))
            if extra:
                problems.append("TOC has links to non-section headings: %s" % ", ".join(ascii_safe(s) for s in extra))
            if not missing and not extra:
                problems.append("TOC order differs from section order")

    # --- блоки кода ---
    matches = list(re.finditer(r"```python\n(.*?)```", text, re.S))
    if not matches:
        problems.append("no ```python blocks found")
    for index, match in enumerate(matches, start=1):
        block = match.group(1)
        before = text[max(0, match.start() - 80) : match.start()]
        skip = NO_CHECK in before
        block_lines = block.splitlines()
        try:
            code = compile(block, "block%d" % index, "exec")
        except SyntaxError as exc:
            if skip:
                continue
            source = ""
            if exc.lineno and exc.lineno <= len(block_lines):
                source = ascii_safe(block_lines[exc.lineno - 1].strip())[:70]
            problems.append(
                "block %d: SyntaxError line %s: %s | %s"
                % (index, exc.lineno, ascii_safe(exc.msg), source)
            )
            continue

        if skip:
            continue
        if any(token in block for token in ("turtle", "time.sleep", "open(")):
            continue
        if "while True" in block and "input(" not in block:
            continue

        def fake_input(*args, **kwargs):
            raise RuntimeError("__NEEDS_INPUT__")

        namespace = {"__name__": "__main__", "input": fake_input}
        try:
            with contextlib.redirect_stdout(CappedOutput()):
                exec(code, namespace)
        except RuntimeError as exc:
            message = str(exc)
            if "__NEEDS_INPUT__" in message:
                continue
            if "__ENDLESS_OUTPUT__" in message:
                problems.append("block %d: endless output - probably infinite loop" % index)
            else:
                problems.append("block %d: RuntimeError: %s" % (index, ascii_safe(exc)))
        except Exception as exc:  # noqa: BLE001 - проверка учебных примеров
            problems.append(
                "block %d: %s: %s" % (index, type(exc).__name__, ascii_safe(exc)[:90])
            )
    return problems


def main(argv):
    if len(argv) < 2:
        print("usage: check_theory.py <file-or-dir> [...]")
        return 2
    files = []
    for item in argv[1:]:
        path = pathlib.Path(item)
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        else:
            files.append(path)
    total = 0
    for path in files:
        if not path.exists():
            print("MISSING", ascii_safe(path.name))
            total += 1
            continue
        problems = check_file(path)
        name = ascii_safe(path.name)
        if problems:
            total += len(problems)
            print("FAIL", name)
            for problem in problems:
                print("   -", problem)
        else:
            print("OK  ", name)
    print("---")
    print("files checked: %d, problems: %d" % (len(files), total))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
