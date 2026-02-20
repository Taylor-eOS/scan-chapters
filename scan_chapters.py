import re
from settings import BOOK_PATH

file_path = BOOK_PATH

def count_empty_lines_between_titles(file_path):
    titles = []
    empty_counts = []
    current_title = None
    empty_line_count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('||'):
                if current_title is not None:
                    empty_counts.append(empty_line_count)
                title_text = line[2:].strip()
                if not title_text:
                    title_text = "(no title)"
                titles.append(title_text)
                current_title = title_text
                empty_line_count = 0  
            else:
                if line.strip() == '':
                    empty_line_count += 1
    if current_title is not None:
        empty_counts.append(empty_line_count)
    print("Document structure report:")
    if not titles:
        print("No chapter markers found in the file.")
        return
    print(f"Found {len(titles)} sections:")
    for i, (title, count) in enumerate(zip(titles, empty_counts), 1):
        print(f"{i}. {title}")
        print(f"   → {count} segments before the next chapter title")
        if i < len(titles):
            print()
    #total_empty = sum(empty_counts)
    #print(f"\nTotal empty lines between sections: {total_empty} (miscounts)")
    #print(f"Total sections: {len(titles)}")

if __name__ == "__main__":
    try:
        count_empty_lines_between_titles(file_path)
    except FileNotFoundError:
        print(f"Error: File {BOOK_PATH} not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

