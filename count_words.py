from settings import BOOK_PATH

filename = BOOK_PATH
MAX_SHOWN = 20

def read_and_split_segments(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    raw_segments = content.split('\n\n')
    segments = []
    for seg in raw_segments:
        seg = seg.strip()
        if not seg:
            continue
        if seg.startswith('||'):
            pos = seg.find('|', 2)
            if pos != -1:
                seg = seg[pos+1:].lstrip()
        if seg:
            segments.append(seg)
    return segments

def get_words(segment):
    return segment.split()

def print_segment_info(segment, index):
    words = get_words(segment)
    word_count = len(words)
    preview_words = words[:10]
    preview_str = ' '.join(preview_words)
    if len(preview_words) < len(words):
        preview_str += " …"
    print(f"Segment {index}:")
    print(f"Word count: {word_count}")
    print(f"{preview_str}")
    print()

def main():
    try:
        segments = read_and_split_segments(filename)
    except FileNotFoundError:
        print("File not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    if not segments:
        print("The file contains no segments (empty or only blank lines).")
        return
    total = len(segments)
    print(f"\nFound {total} segments.\n")
    while True:
        user_input = input(f"Enter starting segment number (1–{total}), or press Enter to quit: ").strip()
        if not user_input:
            print("Goodbye.")
            break
        try:
            start = int(user_input)
            if start < 1 or start > total:
                print(f"Please enter a number between 1 and {total}.")
                continue
        except ValueError:
            print("Please enter a valid number or press Enter to quit.")
            continue
        end = min(start + MAX_SHOWN - 1, total)
        shown_count = end - start + 1
        print(f"\nShowing segments {start} to {end} ({shown_count} of {total})\n")
        for i in range(start-1, end):
            print_segment_info(segments[i], i+1)

if __name__ == "__main__":
    main()
