import functools
import time
import timeit
from importlib import import_module
from statistics import mean

from scrapling import Selector as ScraplingSelector

large_html = (
    "<html><body>" + '<div class="item">' * 5000 + "</div>" * 5000 + "</body></html>"
)


def _import_or_raise(module_name, symbol=None):
    """Import benchmark-only dependencies lazily.

    This keeps module import safe for tooling (pytest doctest collection, IDE indexing)
    while still failing fast when benchmarks are executed without required extras.
    """
    try:
        module = import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"Missing benchmark dependency '{module_name}'. "
            "Install benchmark extras before running benchmarks."
        ) from exc

    if symbol is None:
        return module
    return getattr(module, symbol)


def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        benchmark_name = func.__name__.replace("test_", "").replace("_", " ")
        print(f"-> {benchmark_name}", end=" ", flush=True)
        # Warm-up phase
        timeit.repeat(
            lambda: func(*args, **kwargs), number=2, repeat=2, globals=globals()
        )
        # Measure time (1 run, repeat 100 times, take average)
        times = timeit.repeat(
            lambda: func(*args, **kwargs),
            number=1,
            repeat=100,
            globals=globals(),
            timer=time.process_time,
        )
        min_time = round(mean(times) * 1000, 2)  # Convert to milliseconds
        print(f"average execution time: {min_time} ms")
        return min_time

    return wrapper


@benchmark
def bench_lxml():
    etree = _import_or_raise("lxml.etree")
    html = _import_or_raise("lxml.html")
    return [
        e.text
        for e in etree.fromstring(
            large_html,
            # Scrapling and Parsel use the same parser inside, so this is just to make it fair
            parser=html.HTMLParser(recover=True, huge_tree=True),
        ).cssselect(".item")
    ]


@benchmark
def bench_bs4_lxml():
    BeautifulSoup = _import_or_raise("bs4", "BeautifulSoup")
    return [e.text for e in BeautifulSoup(large_html, "lxml").select(".item")]


@benchmark
def bench_bs4_html5lib():
    BeautifulSoup = _import_or_raise("bs4", "BeautifulSoup")
    return [e.text for e in BeautifulSoup(large_html, "html5lib").select(".item")]


@benchmark
def bench_pyquery():
    pq = _import_or_raise("pyquery", "PyQuery")
    return [e.text() for e in pq(large_html)(".item").items()]


@benchmark
def bench_scrapling():
    # No need to do `.extract()` like parsel to extract text
    # Also, this is faster than `[t.text for t in Selector(large_html, adaptive=False).css('.item')]`
    # for obvious reasons, of course.
    return ScraplingSelector(large_html, adaptive=False).css(".item::text").getall()


@benchmark
def bench_parsel():
    Selector = _import_or_raise("parsel", "Selector")
    return Selector(text=large_html).css(".item::text").extract()


@benchmark
def bench_mechanicalsoup():
    StatefulBrowser = _import_or_raise("mechanicalsoup", "StatefulBrowser")
    browser = StatefulBrowser()
    browser.open_fake_page(large_html)
    return [e.text for e in browser.page.select(".item")]


@benchmark
def bench_selectolax():
    HTMLParser = _import_or_raise("selectolax.parser", "HTMLParser")
    return [node.text() for node in HTMLParser(large_html).css(".item")]


def display(results):
    # Sort and display results
    sorted_results = sorted(results.items(), key=lambda x: x[1])  # Sort by time
    scrapling_time = results["Scrapling"]
    print("\nRanked Results (fastest to slowest):")
    print(f" i. {'Library tested':<18} | {'avg. time (ms)':<15} | vs Scrapling")
    print("-" * 50)
    for i, (test_name, test_time) in enumerate(sorted_results, 1):
        compare = round(test_time / scrapling_time, 3)
        print(f" {i}. {test_name:<18} | {str(test_time):<15} | {compare}")


@benchmark
def bench_scrapling_text(request_html):
    return ScraplingSelector(request_html, adaptive=False).find_by_text("Tipping the Velvet", first_match=True, clean_match=False).find_similar(ignore_attributes=["title"])


@benchmark
def bench_autoscraper(request_html):
    AutoScraper = _import_or_raise("autoscraper", "AutoScraper")
    # autoscraper by default returns elements text
    return AutoScraper().build(html=request_html, wanted_list=["Tipping the Velvet"])


if __name__ == "__main__":
    print(
        " Benchmark: Speed of parsing and retrieving the text content of 5000 nested elements \n"
    )
    results1 = {
        "Raw Lxml": bench_lxml(),
        "Parsel/Scrapy": bench_parsel(),
        "Scrapling": bench_scrapling(),
        "Selectolax": bench_selectolax(),
        "PyQuery": bench_pyquery(),
        "BS4 with Lxml": bench_bs4_lxml(),
        "MechanicalSoup": bench_mechanicalsoup(),
        "BS4 with html5lib": bench_bs4_html5lib(),
    }

    display(results1)
    print("\n" + "=" * 25)
    requests = _import_or_raise("requests")
    req = requests.get("https://books.toscrape.com/index.html")
    print(
        " Benchmark: Speed of searching for an element by text content, and retrieving the text of similar elements\n"
    )
    results2 = {
        "Scrapling": bench_scrapling_text(req.text),
        "AutoScraper": bench_autoscraper(req.text),
    }
    display(results2)
