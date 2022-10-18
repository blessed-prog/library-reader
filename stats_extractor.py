import fitz
from datetime import datetime, date, timedelta


class ReadStats:
    def __init__(self, start_time: date, days_count, pages_count, type_str: str):
        self.start_time = start_time
        self.days_count = days_count
        self.pages_count = pages_count
        self.type_str = type_str

    def __str__(self):
        return f"Read {self.pages_count} pages of {self.type_str} from {self.start_time} in {self.days_count} days"


class StatsExtractor:

    def get_read_stats(self, file_path: str):
        try:
            doc = fitz.open(file_path)

            if not self._has_annotations(doc):
                return

            if self.find_last_modify_time_from_annotations(doc).year < 2020:
                return

            if doc.page_count < 30:
                type_str = 'papers'
                mod_time = self.find_last_modify_time_from_annotations(doc)
                # papers
                if self._has_annotations(doc):
                    yield ReadStats(mod_time.date(), days_count=1, pages_count=doc.page_count, type_str=type_str)
                    pass
                else:
                    yield ReadStats(mod_time.date(), days_count=1, pages_count=doc.page_count / 3, type_str=type_str)
                pass
                return

            prev_annotation_time = datetime.fromtimestamp(0)
            prev_annotation_page = 0

            for page in doc:
                for annotation in page.annots():
                    annotation_time = self._parse_time(annotation)

                    if page.number == prev_annotation_page:
                        continue
                    if annotation_time < prev_annotation_time:
                        continue

                    if prev_annotation_page > 0:
                        delta = annotation_time - prev_annotation_time
                        if delta.days == 0:
                            delta = timedelta(days=1)
                        pages_count = page.number - prev_annotation_page
                        if pages_count < 25:
                            yield ReadStats(prev_annotation_time.date(), pages_count=pages_count, days_count=delta.days, type_str='books')

                    prev_annotation_time = annotation_time
                    prev_annotation_page = page.number
        except RuntimeError:
            pass
        except ValueError:
            pass

    def find_last_modify_time_from_annotations(self, doc) -> datetime:

        mod_timestamp = 0

        for page in doc:
            for annotation in page.annots():
                mod_timestamp = max(mod_timestamp, self._parse_time(annotation).timestamp())
        return datetime.fromtimestamp(mod_timestamp)

    def _has_annotations(self, doc) -> bool:
        for page in doc:
            for annot in page.annots():
                return True
        return False

    def _parse_time(self, annotation) -> datetime:
        to_parse = annotation.info['modDate']
        return datetime.strptime(to_parse[2:14], '%Y%m%d%H%M')
