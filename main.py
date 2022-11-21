from concurrent.futures import ThreadPoolExecutor


def main():
    with ThreadPoolExecutor() as executor:
        executor.submit()