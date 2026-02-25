
import time
def is_unique(s: str) -> bool:
    list = []
    for i in s:
        if i not in list:
            list.append(i)
        else:
            return False
    return True

def main():
    t0 = time.perf_counter()
    print(is_unique('abcdefgxijklmnop1234567890'))
    elapsed_time = time.perf_counter() - t0
    print(f"Time it took: {elapsed_time:.4f}s")
if __name__ == "__main__":
    main()
    