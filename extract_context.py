input_path = "input.txt"
output_path = "output.txt"

add_after = False

def read_segments(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    raw_segments = content.split("\n\n")
    segments = []
    for raw in raw_segments:
        lines = raw.split("\n")
        if raw.strip() == "" and len(lines) == 1:
            continue
        segments.append(lines)
    return segments

def find_matching_indices(lines, word):
    indices = set()
    for i, line in enumerate(lines):
        if word in line:
            indices.add(i)
    return indices

def expand_with_context(lines, indices):
    expanded = set()
    for i in indices:
        expanded.add(i)
        if i - 1 >= 0:
            expanded.add(i - 1)
        if add_after:
            if i + 1 < len(lines):
                expanded.add(i + 1)
    return expanded

def build_segment_output(lines, expanded_indices):
    output_lines = []
    for i in sorted(expanded_indices):
        output_lines.append(lines[i])
    return output_lines

def process_segments(segments, word):
    result_segments = []
    for lines in segments:
        indices = find_matching_indices(lines, word)
        if not indices:
            continue
        expanded_indices = expand_with_context(lines, indices)
        output_lines = build_segment_output(lines, expanded_indices)
        result_segments.append(output_lines)
    return result_segments

def write_segments(path, result_segments):
    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result_segments):
            f.write("\n".join(seg))
            if i != len(result_segments) - 1:
                f.write("\n\n")

def main():
    word = input("Enter search word: ")
    segments = read_segments(input_path)
    result_segments = process_segments(segments, word)
    write_segments(output_path, result_segments)
    print(f"Wrote {len(result_segments)} segment(s) to {output_path}")

if __name__ == "__main__":
    main()
