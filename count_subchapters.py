file_path = "input.txt"
report_path = "subchapter_report.txt"

def percentile(sorted_data, p):
    if not sorted_data:
        return 0
    idx = (len(sorted_data) - 1) * p / 100
    lo = int(idx)
    hi = lo + 1
    if hi >= len(sorted_data):
        return sorted_data[lo]
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])

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
    all_word_counts = [len(sub.split()) for _, subs in chapters for sub in subs]
    sorted_counts = sorted(all_word_counts)
    total_subs = len(all_word_counts)
    total_words = sum(all_word_counts)
    mean = total_words / total_subs if total_subs else 0
    median = percentile(sorted_counts, 50)
    q1 = percentile(sorted_counts, 25)
    q3 = percentile(sorted_counts, 75)
    low_fence = percentile(sorted_counts, 10)
    flagged_runs = []
    with open(report_path, 'w', encoding='utf-8') as out:
        global_idx = 0
        for chapter_idx, (title, subchapters) in enumerate(chapters, 1):
            chapter_words = sum(len(sub.split()) for sub in subchapters)
            out.write(f"[{chapter_idx}] {title}  ({chapter_words} words, {len(subchapters)} subchapters)\n")
            run_start = None
            for sub_idx, subchapter in enumerate(subchapters, 1):
                word_count = len(subchapter.split())
                is_short = word_count < low_fence
                flag = '*' if is_short else ' '
                preview = subchapter[:100] + ('...' if len(subchapter) > 100 else '')
                out.write(f" {flag}{sub_idx}. [{word_count}]  {preview}\n")
                global_idx += 1
                if is_short:
                    if run_start is None:
                        run_start = (chapter_idx, sub_idx)
                    run_end = (chapter_idx, sub_idx)
                else:
                    if run_start is not None:
                        flagged_runs.append((run_start, run_end))
                        run_start = None
            if run_start is not None:
                flagged_runs.append((run_start, run_end))
                run_start = None
        out.write(f"\n--- Summary ---\n")
        out.write(f"Chapters: {len(chapters)}  Subchapters: {total_subs}  Total words: {total_words}\n")
        out.write(f"Mean: {mean:.1f}  Median: {median:.1f}  Min: {min(all_word_counts)}  Max: {max(all_word_counts)}\n")
        out.write(f"Q1: {q1:.1f}  Q3: {q3:.1f}  P10 (low fence): {low_fence:.1f}\n")
        n_flagged = sum(1 for c in all_word_counts if c < low_fence)
        out.write(f"Flagged short (*): {n_flagged} subchapters below P10 ({low_fence:.1f} words)\n")
        if flagged_runs:
            out.write(f"\n--- Consecutive short subchapter runs ---\n")
            for (ch_s, sub_s), (ch_e, sub_e) in flagged_runs:
                length = sub_e - sub_s + 1 if ch_s == ch_e else '?'
                if ch_s == ch_e:
                    loc = f"ch.{ch_s} sub {sub_s}" if length == 1 else f"ch.{ch_s} subs {sub_s}-{sub_e}"
                else:
                    loc = f"ch.{ch_s} sub {sub_s} – ch.{ch_e} sub {sub_e}"
                    length = sub_e - sub_s + 1
                out.write(f"  {length}x  {loc}\n")
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    try:
        count_words_per_subchapter(file_path, report_path)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

