from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DocStats:
    num_docs: int
    min_len: int
    max_len: int
    average_len: float

def read_lines(path: str) -> list[str]:

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
        
    docs = [w_line.strip() for w_line in lines if w_line.strip()]
    return docs

def compute_stats(docs: list[str]) -> DocStats:
    lengths = [len(d) for d in docs]
    return DocStats(
        num_docs=len(docs),
        min_len=min(lengths),
        max_len=max(lengths),
        average_len=sum(lengths) / len(lengths),
    )

def compute_stats_safe(docs: list[str]) -> DocStats | None:
    if isinstance(docs, list):
        if docs:
            return compute_stats(docs)
        else:
            return None

if __name__ == "__main__":
    line_words = read_lines("input.txt")
    stats = compute_stats_safe(line_words)
    print(f"Average length: {stats.average_len}")
    print(f"Print first 5 words {line_words[:5]}")
    print(f"Show doc stats: {stats}")

# What does splitlines() do differently vs split("\n")?
# I think splitlines automatically splits the word after it sees a newline whereas split; lets you specify when or what to split after
