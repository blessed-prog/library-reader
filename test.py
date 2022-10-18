from datetime import date, timedelta

from stats_extractor import StatsExtractor
from pdf_file_iterator import PdfFileIterator


def to_monday(input: date) -> date:
    start = input - timedelta(days=input.weekday())
    return start


if __name__ == "__main__":

    dir_to_scan = ''
    extractor = StatsExtractor()

    papers_by_date: dict = {}
    books_by_date: dict = {}
    all_by_date: dict = {}

    for pdf_file_path in PdfFileIterator().iterate(dir_to_scan):

        print(f"Checking {pdf_file_path}")
        for stats in extractor.get_read_stats(pdf_file_path):
            avg_pages = (stats.pages_count * 1.0) / stats.days_count
            day = stats.start_time - timedelta(days=1)
            for offset in range(1):
                day = to_monday(stats.start_time + timedelta(days=1))

                if day not in papers_by_date:
                    papers_by_date[day] = 0.0
                papers_by_date[day] = papers_by_date[day] + avg_pages
                print(f"Added {avg_pages} at {day} from {pdf_file_path}")

            pass

    day_to_check = to_monday(date.fromisoformat('2020-01-01'))
    today = to_monday(date.today())

    while day_to_check < today:
        if day_to_check not in papers_by_date:
            papers_by_date[day_to_check] = 0.0
        print(f"{day_to_check},{round(papers_by_date[day_to_check] / 7.0)}")

        day_to_check = day_to_check + timedelta(days=7)


