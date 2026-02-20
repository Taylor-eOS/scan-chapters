from settings import BOOK_PATH

file_path = BOOK_PATH
report_path = "subchapter_report.txt"

def count_words_per_subchapter(file_path, report_path):
    chapters = []
    current_chapter = "(preamble)"
    current_subchapters = []
    current_block_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('||'):
                if current_block_lines:
                    current_subchapters.append(' '.join(current_block_lines))
                    current_block_lines = []
                if current_subchapters or current_chapter != "(preamble)":
                    chapters.append((current_chapter, current_subchapters))
                title_text = line[2:].strip() or "(no title)"
                current_chapter = title_text
                current_subchapters = []
            elif line.strip() == '':
                if current_block_lines:
                    current_subchapters.append(' '.join(current_block_lines))
                    current_block_lines = []
            else:
                current_block_lines.append(line.strip())
    if current_block_lines:
        current_subchapters.append(' '.join(current_block_lines))
    chapters.append((current_chapter, current_subchapters))
    with open(report_path, 'w', encoding='utf-8') as out:
        total_words = 0
        total_subs = 0
        for chapter_idx, (title, subchapters) in enumerate(chapters, 1):
            chapter_words = sum(len(sub.split()) for sub in subchapters)
            total_words += chapter_words
            total_subs += len(subchapters)
            out.write(f"[{chapter_idx}] {title}  ({chapter_words} words, {len(subchapters)} subchapters)\n")
            for sub_idx, subchapter in enumerate(subchapters, 1):
                word_count = len(subchapter.split())
                preview = subchapter[:100] + ('...' if len(subchapter) > 100 else '')
                out.write(f"  {sub_idx}. [{word_count}]  {preview}\n")
        out.write(f"\nTotal: {len(chapters)} chapters, {total_subs} subchapters, {total_words} words\n")
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    try:
        count_words_per_subchapter(file_path, report_path)
    except FileNotFoundError:
        print(f"Error: File {BOOK_PATH} not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
