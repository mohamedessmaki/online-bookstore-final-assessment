import timeit

from models import Book, Cart


def test_cart_total_performance_under_threshold():
    cart = Cart()
    book = Book("Perf", "Cat", 1.0, "/img")
    cart.add_book(book, 10000)

    # Measure execution time of get_total_price; expect fast due to O(n)
    duration = timeit.timeit(cart.get_total_price, number=50)

    # Threshold: 0.5s for 50 runs on CI runners (loose guardrail)
    assert duration < 0.5

def test_cart_total_cprofile_runs():
    # Basic cProfile run to capture hotspots without strict assertions
    import cProfile
    import pstats
    cart = Cart()
    book = Book("Perf", "Cat", 1.0, "/img")
    cart.add_book(book, 5000)
    profiler = cProfile.Profile()
    profiler.enable()
    cart.get_total_price()
    profiler.disable()
    stats = pstats.Stats(profiler)
    # Ensure profiling collected some function calls
    assert stats.total_calls > 0


