from settings import BOOK_PATH

file_path = BOOK_PATH
report_path = "line_report.txt"
cv_flag_threshold = 0.6
short_line_ratio = 0.5
short_line_fraction_threshold = 0.4
long_line_ratio = 2.0
long_line_fraction_threshold = 0.4
global_low_ratio = 0.3
global_high_ratio = 2.5
top_longest_lines_count = 20

def percentile(sorted_data, p):
    if not sorted_data:
        return 0
    idx = (len(sorted_data) - 1) * p / 100
    lo = int(idx)
    hi = lo + 1
    if hi >= len(sorted_data):
        return sorted_data[lo]
    return sorted_data[lo] + (idx - lo) * (sorted_data[hi] - sorted_data[lo])

def read_segments(file_path):
    segments = []
    current_lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            stripped = raw_line.rstrip('\n').strip()
            if stripped == '' or stripped.startswith('|'):
                if current_lines:
                    segments.append(current_lines)
                    current_lines = []
                continue
            current_lines.append(stripped)
    if current_lines:
        segments.append(current_lines)
    return segments

def mean_and_stdev(word_counts):
    n = len(word_counts)
    if n == 0:
        return 0, 0
    mean = sum(word_counts) / n
    if n == 1:
        return mean, 0
    variance = sum((c - mean) ** 2 for c in word_counts) / n
    return mean, variance ** 0.5

def evaluate_segment(word_counts, global_mean):
    mean, stdev = mean_and_stdev(word_counts)
    cv = stdev / mean if mean > 0 else 0
    short_cutoff = mean * short_line_ratio
    long_cutoff = mean * long_line_ratio
    n = len(word_counts)
    short_fraction = sum(1 for c in word_counts if c < short_cutoff) / n if n else 0
    long_fraction = sum(1 for c in word_counts if c > long_cutoff) / n if n else 0
    global_low_cutoff = global_mean * global_low_ratio
    global_high_cutoff = global_mean * global_high_ratio
    reasons = []
    if cv >= cv_flag_threshold and n >= 3:
        reasons.append(f"high variance (cv={cv:.2f})")
    if short_fraction >= short_line_fraction_threshold and n >= 3:
        reasons.append(f"over-split ({short_fraction * 100:.0f}% of lines under {short_cutoff:.1f} words)")
    if long_fraction >= long_line_fraction_threshold and n >= 3:
        reasons.append(f"under-split ({long_fraction * 100:.0f}% of lines over {long_cutoff:.1f} words)")
    if global_mean > 0 and mean < global_low_cutoff:
        reasons.append(f"segment mean ({mean:.1f}) far below typical segment ({global_mean:.1f})")
    if global_mean > 0 and mean > global_high_cutoff:
        reasons.append(f"segment mean ({mean:.1f}) far above typical segment ({global_mean:.1f})")
    return mean, stdev, cv, reasons

def compute_global_stats(all_word_counts):
    sorted_counts = sorted(all_word_counts)
    total_lines = len(all_word_counts)
    total_words = sum(all_word_counts)
    mean = total_words / total_lines if total_lines else 0
    stats = {
        'total_lines': total_lines,
        'total_words': total_words,
        'mean': mean,
        'median': percentile(sorted_counts, 50),
        'q1': percentile(sorted_counts, 25),
        'q3': percentile(sorted_counts, 75),
        'min': min(all_word_counts) if all_word_counts else 0,
        'max': max(all_word_counts) if all_word_counts else 0,
    }
    return stats

def compute_segment_means(segments):
    return [mean_and_stdev([len(line.split()) for line in lines])[0] for lines in segments]

def collect_longest_lines(segments):
    entries = []
    for seg_idx, lines in enumerate(segments, 1):
        for line_idx, line in enumerate(lines, 1):
            entries.append((len(line.split()), seg_idx, line_idx, line))
    entries.sort(key=lambda entry: entry[0], reverse=True)
    return entries[:top_longest_lines_count]

def write_report(report_path, segments, stats):
    flagged_segments = []
    segment_means = compute_segment_means(segments)
    reference_mean = percentile(sorted(segment_means), 50)
    longest_lines = collect_longest_lines(segments)
    with open(report_path, 'w', encoding='utf-8') as out:
        for seg_idx, lines in enumerate(segments, 1):
            word_counts = [len(line.split()) for line in lines]
            mean, stdev, cv, reasons = evaluate_segment(word_counts, reference_mean)
            marker = '*' if reasons else ' '
            out.write(f"{marker}[{seg_idx}] {len(lines)} lines, mean {mean:.1f} words/line, stdev {stdev:.1f}, cv {cv:.2f}\n")
            if reasons:
                for reason in reasons:
                    out.write(f"    - {reason}\n")
                flagged_segments.append(seg_idx)
            for line_idx, line in enumerate(lines, 1):
                count = word_counts[line_idx - 1]
                preview = line[:100] + ('...' if len(line) > 100 else '')
                out.write(f"    {line_idx}. [{count}]  {preview}\n")
        out.write(f"\n--- Summary ---\n")
        out.write(f"Segments: {len(segments)}  Lines: {stats['total_lines']}  Total words: {stats['total_words']}\n")
        out.write(f"Mean: {stats['mean']:.1f}  Median: {stats['median']:.1f}  Min: {stats['min']}  Max: {stats['max']}\n")
        out.write(f"Q1: {stats['q1']:.1f}  Q3: {stats['q3']:.1f}\n")
        out.write(f"Flagged segments: {len(flagged_segments)} of {len(segments)}\n")
        if flagged_segments:
            ids = ', '.join(str(i) for i in flagged_segments)
            out.write(f"Flagged segment numbers: {ids}\n")
        out.write(f"\n--- Top {len(longest_lines)} Longest Lines ---\n")
        for count, seg_idx, line_idx, line in longest_lines:
            preview = line[:100] + ('...' if len(line) > 100 else '')
            out.write(f"[{count}] segment {seg_idx}, line {line_idx}: {preview}\n")

def analyze_line_lengths(file_path, report_path):
    segments = read_segments(file_path)
    all_word_counts = [len(line.split()) for lines in segments for line in lines]
    stats = compute_global_stats(all_word_counts)
    write_report(report_path, segments, stats)
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    try:
        analyze_line_lengths(file_path, report_path)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
