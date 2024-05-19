from typing import List, Dict, Union
from tabula import read_pdf

from infrastructure.models.section import Section
from infrastructure.models.course import Course
from infrastructure.models.enums import Column

coursed_options = {'header': None,
                   'names': ['School', 'Level', 'Course Abbr', 'S/T', 'Course Title',
                             'Cr(U\rS)', 'Cr(E\rCTS)',
                             'Start Date', 'End Date', 'Days', 'Time',
                             'Enr', 'Cap', 'Faculty', 'Room']}


class PdfParser:
    def __init__(self, path: str):
        self.path = path
        self.pdf_json = self.load_schedule()
        self.abbrs: List[str] = []
        self.sections = self.get_sections_list()
        self.courses = self.distribute_sections()

    def load_schedule(self) -> Dict[str, any]:
        sections_json: List[Dict[str, any]] = read_pdf(self.path, pandas_options=coursed_options, pages='all',
                                                       output_format='json', lattice=True, encoding='cp1252')
        return sections_json

    def get_sections_list(self) -> List[Section]:
        sections: List[Section] = []
        for page in self.pdf_json:
            for sid, row in enumerate(page['data']):
                if self.__get_abbr(row) == 'Course Abbr':
                    continue

                variables = (self.__get_school(row), self.__get_level(row), self.__get_abbr(row), self.__get_ctype(row),
                             self.__get_title(row), self.__get_credits_us(row), self.__get_credits_eu(row),
                             self.__get_start_date(row), self.__get_end_date(row), self.__get_weekdays(row),
                             self.__get_time(row), self.__get_enrolled(row), self.__get_course_capacity(row),
                             self.__get_faculty(row), self.__get_room(row))  # WHAT THE FUCK

                (school, level, abbr, ctype, title,
                 cus, ceu, start_date, end_date, days, times, enr, cap, faculty, room) = variables

                if not abbr:  # additional info appears on newline, so [if no abbr on row -> its addition info]
                    last_course = sections.pop()
                    last_course.add_time(days, times)
                    last_course.faculty = last_course.faculty + faculty
                    last_course.room = last_course.room + room
                    sections.append(last_course)
                    continue

                temp = Section(sid, abbr, ctype, title,
                               cus, ceu,
                               start_date, end_date,
                               days, times, enr, cap, faculty, room)
                sections.append(temp)
                self.abbrs.append(abbr)

        # sections.pop(0)
        return sections

    def distribute_sections(self) -> List[Course]:
        courses: List[Course] = []
        unique_abbrs = list(set(self.abbrs))
        for section in self.sections:
            if section.abbr in unique_abbrs:
                unique_abbrs.remove(section.abbr)
                course = Course(section.abbr, section.title)
                course.add_section(section)
                courses.append(course)
            else:
                for course in courses:
                    if course.abbr == section.abbr:
                        course.add_section(section)

        return courses

    def __get_school(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.SCHOOL)

    def __get_level(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.LEVEL)

    def __get_abbr(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.ABBR)

    def __get_ctype(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.CTYPE)

    def __get_title(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.TITLE)

    def __get_credits_us(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.CRED_US)

    def __get_credits_eu(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.CRED_EU)

    def __get_start_date(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.START)

    def __get_end_date(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.END)

    def __get_weekdays(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.DAYS)

    def __get_time(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.TIME)

    def __get_enrolled(self, row: List[Dict[str, any]]) -> Union[str, int]:
        temp = self.get_column(row, Column.ENR)
        if temp.isnumeric():
            return int(temp)

        return temp

    def __get_course_capacity(self, row: List[Dict[str, any]]) -> Union[str, int]:
        temp = self.get_column(row, Column.CAP)
        if temp.isnumeric():
            return int(temp)

        return temp

    def __get_faculty(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.FACULTY)

    def __get_room(self, row: List[Dict[str, any]]) -> str:
        return self.get_column(row, Column.ROOM)

    @staticmethod
    def get_column(row: List[Dict[str, any]], column: Column) -> str:
        cid = column.value
        try:
            temp = row[cid]['text'].replace('\r', ' ')
        except Exception as e:
            print(e)
            temp = "-"
        return temp
