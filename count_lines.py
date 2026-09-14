from settings import BOOK_PATH

file_path = BOOK_PATH
report_path = "line_report.txt"
neighbor_jump_ratio = 2.5
neighbor_jump_min_diff = 6

def percentile(sorted_data, p):
    if not sorted_data:
        return 0
    idx = (len(sorted_data) - 1) * p / 100
    lo = int(idx)
    hi = lo + 1
    if hi >= len(sorted_data):
        return sorted_data[lo]
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])

def read_lines(file_path):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            stripped = raw_line.rstrip('\n').strip()
            if stripped == '' or stripped.startswith('|'):
                continue
            lines.append(stripped)
    return lines

def compute_stats(word_counts):
    sorted_counts = sorted(word_counts)
    total_lines = len(word_counts)
    total_words = sum(word_counts)
    mean = total_words / total_lines if total_lines else 0
    stats = {
        'total_lines': total_lines,
        'total_words': total_words,
        'mean': mean,
        'median': percentile(sorted_counts, 50),
        'q1': percentile(sorted_counts, 25),
        'q3': percentile(sorted_counts, 75),
        'low_fence': percentile(sorted_counts, 10),
        'high_fence': percentile(sorted_counts, 90),
        'min': min(word_counts) if word_counts else 0,
        'max': max(word_counts) if word_counts else 0,
    }
    return stats

def is_neighbor_jump(word_counts, idx):
    count = word_counts[idx]
    neighbors = []
    if idx > 0:
        neighbors.append(word_counts[idx - 1])
    if idx < len(word_counts) - 1:
        neighbors.append(word_counts[idx + 1])
    if not neighbors:
        return False
    for neighbor in neighbors:
        diff = abs(count - neighbor)
        if diff < neighbor_jump_min_diff:
            continue
        smaller = min(count, neighbor) if min(count, neighbor) > 0 else 1
        ratio = max(count, neighbor) / smaller
        if ratio >= neighbor_jump_ratio:
            return True
    return False

def classify_lines(lines, word_counts, stats):
    flags = []
    for idx in range(len(lines)):
        count = word_counts[idx]
        if count < stats['low_fence']:
            flags.append('short')
        elif count > stats['high_fence']:
            flags.append('long')
        elif is_neighbor_jump(word_counts, idx):
            flags.append('jump')
        else:
            flags.append(None)
    return flags

def find_runs(flags, categories):
    runs = []
    run_start = None
    for idx, flag in enumerate(flags):
        if flag in categories:
            if run_start is None:
                run_start = idx
            run_end = idx
        else:
            if run_start is not None:
                runs.append((run_start, run_end))
                run_start = None
    if run_start is not None:
        runs.append((run_start, run_end))
    return runs

def write_report(report_path, lines, word_counts, flags, stats):
    flag_symbols = {'short': '-', 'long': '+', 'jump': '~'}
    with open(report_path, 'w', encoding='utf-8') as out:
        for idx, line in enumerate(lines):
            count = word_counts[idx]
            flag = flags[idx]
            symbol = flag_symbols.get(flag, ' ')
            preview = line[:100] + ('...' if len(line) > 100 else '')
            out.write(f" {symbol}{idx + 1}. [{count}]  {preview}\n")
        out.write(f"\n--- Summary ---\n")
        out.write(f"Lines: {stats['total_lines']}  Total words: {stats['total_words']}\n")
        out.write(f"Mean: {stats['mean']:.1f}  Median: {stats['median']:.1f}  Min: {stats['min']}  Max: {stats['max']}\n")
        out.write(f"Q1: {stats['q1']:.1f}  Q3: {stats['q3']:.1f}  P10: {stats['low_fence']:.1f}  P90: {stats['high_fence']:.1f}\n")
        n_short = sum(1 for f in flags if f == 'short')
        n_long = sum(1 for f in flags if f == 'long')
        n_jump = sum(1 for f in flags if f == 'jump')
        out.write(f"Flagged short (-): {n_short} lines below P10 ({stats['low_fence']:.1f} words)\n")
        out.write(f"Flagged long (+): {n_long} lines above P90 ({stats['high_fence']:.1f} words)\n")
        out.write(f"Flagged local jump (~): {n_jump} lines diverging sharply from a neighbor\n")
        short_runs = find_runs(flags, {'short'})
        if short_runs:
            out.write(f"\n--- Consecutive short line runs ---\n")
            for start, end in short_runs:
                length = end - start + 1
                loc = f"line {start + 1}" if length == 1 else f"lines {start + 1}-{end + 1}"
                out.write(f"  {length}x  {loc}\n")
        long_runs = find_runs(flags, {'long'})
        if long_runs:
            out.write(f"\n--- Consecutive long line runs ---\n")
            for start, end in long_runs:
                length = end - start + 1
                loc = f"line {start + 1}" if length == 1 else f"lines {start + 1}-{end + 1}"
                out.write(f"  {length}x  {loc}\n")
        irregular_runs = find_runs(flags, {'short', 'long', 'jump'})
        if irregular_runs:
            out.write(f"\n--- Consecutive irregular line runs (any flag) ---\n")
            for start, end in irregular_runs:
                length = end - start + 1
                loc = f"line {start + 1}" if length == 1 else f"lines {start + 1}-{end + 1}"
                out.write(f"  {length}x  {loc}\n")

def analyze_line_lengths(file_path, report_path):
    lines = read_lines(file_path)
    word_counts = [len(line.split()) for line in lines]
    stats = compute_stats(word_counts)
    flags = classify_lines(lines, word_counts, stats)
    write_report(report_path, lines, word_counts, flags, stats)
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    try:
        analyze_line_lengths(file_path, report_path)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
