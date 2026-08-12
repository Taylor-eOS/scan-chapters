#!/usr/bin/env python3
from collections import defaultdict
from datetime import datetime

INPUT_FILE = 'input.txt'
OUTPUT_FILE = 'duplicate_report.txt'
NGRAM_SIZE = int(input("Ngram size (5): ") or 5)
CONTEXT_WORDS = 5

def extract_words(text):
    words = []
    for token in text.lower().split():
        cleaned = token.strip('.,!?"\'()[]{}')
        if cleaned:
            words.append(cleaned)
    return words

def find_ngram_duplicates(text, n=4):
    words = extract_words(text)
    ngrams = defaultdict(list)
    for i in range(len(words) - n + 1):
        ngram = tuple(words[i:i+n])
        ngrams[ngram].append(i)
    duplicates = {ngram: positions for ngram, positions in ngrams.items() if len(positions) > 1}
    return duplicates, words

def format_context(words, position, n, context_words=5):
    start = max(0, position - context_words)
    end = min(len(words), position + n + context_words)
    before = words[start:position]
    ngram = words[position:position+n]
    after = words[position+n:end]
    context = ' '.join(before) + ' [' + ' '.join(ngram) + '] ' + ' '.join(after)
    return context.strip()

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{INPUT_FILE}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    duplicates, words = find_ngram_duplicates(text, NGRAM_SIZE)
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as report:
            report.write(f"Duplicate N-gram Report\n")
            report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report.write(f"Input file: {INPUT_FILE}\n")
            report.write(f"N-gram size: {NGRAM_SIZE} words\n")
            report.write(f"Total words in document: {len(words)}\n")
            report.write("=" * 80 + "\n\n")
            if not duplicates:
                report.write(f"No duplicate {NGRAM_SIZE}-grams found.\n")
                print(f"Report written to {OUTPUT_FILE}")
                return
            report.write(f"Found {len(duplicates)} duplicate {NGRAM_SIZE}-gram sequences\n\n")
            sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
            for ngram, positions in sorted_duplicates:
                report.write(f"Frequency: {len(positions)} occurrences\n")
                report.write(f"Phrase: {' '.join(ngram)}\n\n")
                for idx, pos in enumerate(positions, 1):
                    context = format_context(words, pos, NGRAM_SIZE, CONTEXT_WORDS)
                    report.write(f"  [{idx}] Word position {pos}: {context}\n")
                report.write("\n")
        print(f"Report written to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing report: {e}")

if __name__ == '__main__':
    main()
