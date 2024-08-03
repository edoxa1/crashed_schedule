from typing import NamedTuple
from typing import Dict, Union, Any
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
        self.abbrs: list[str] = []
        self.courses: list[Course] = []
        self.parse_courses()

    def load_schedule(self) -> Dict[str, Any]:
        sections_json: list[Dict[str, Any]] = read_pdf(self.path, pandas_options=coursed_options, pages='all',
                                                       output_format='json', lattice=True, encoding='cp1252')
        return sections_json

    def parse_courses(self):
        last_section = None
        for page in self.pdf_json:
            for sid, row in enumerate(page['data']):
                if self.__get_abbr(row) == 'Course Abbr':
                    continue

                variables = {
                    'school': self.__get_school(row),
                    'level': self.__get_level(row),
                    'abbr': self.__get_abbr(row),
                    'name': self.__get_ctype(row),
                    'title': self.__get_title(row),
                    'credits_us': self.__get_credits_us(row),
                    'credits_eu': self.__get_credits_eu(row),
                    'start_date': self.__get_start_date(row),
                    'end_date': self.__get_end_date(row),
                    'weekdays': self.__get_weekdays(row),
                    'times': self.__get_time(row),
                    'enrolled': self.__get_enrolled(row),
                    'course_capacity': self.__get_course_capacity(row),
                    'faculty': self.__get_faculty(row),
                    'room': self.__get_room(row)
                }

                # additional info appears on newline, so [if no abbr on row -> its addition info]
                if not variables.get('abbr'):
                    print(last_section.abbr)
                    last_section.add_time(variables.get('weekdays'),
                                          variables.get('times'))
                    last_section.faculty = last_section.faculty + variables.get('faculty')
                    last_section.room = last_section.room + variables.get('room')
                    continue

                section = Section(**variables)
                abbr = variables.get('abbr')
                if abbr not in self.abbrs:
                    self.abbrs.append(abbr)
                    course = Course(abbr=abbr, title=variables.get('title'))
                    course.add_section(section)
                    self.courses.append(course)
                else:
                    index = self.courses.index(abbr)  # search by abbr, since __eq__ is defined
                    course = self.courses[index]
                    course.add_section(section)

                last_section = section

    def __get_school(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.SCHOOL)

    def __get_level(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.LEVEL)

    def __get_abbr(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.ABBR)

    def __get_ctype(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.CTYPE)

    def __get_title(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.TITLE)

    def __get_credits_us(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.CRED_US)

    def __get_credits_eu(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.CRED_EU)

    def __get_start_date(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.START)

    def __get_end_date(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.END)

    def __get_weekdays(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.DAYS)

    def __get_time(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.TIME)

    def __get_enrolled(self, row: list[Dict[str, Any]]) -> Union[str, int]:
        temp = self.get_column(row, Column.ENR)
        if temp.isnumeric():
            return int(temp)

        return temp

    def __get_course_capacity(self, row: list[Dict[str, Any]]) -> Union[str, int]:
        temp = self.get_column(row, Column.CAP)
        if temp.isnumeric():
            return int(temp)

        return temp

    def __get_faculty(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.FACULTY)

    def __get_room(self, row: list[Dict[str, Any]]) -> str:
        return self.get_column(row, Column.ROOM)

    @staticmethod
    def get_column(row: list[Dict[str, Any]], column: Column) -> str:
        cid = column.value
        try:
            temp = row[cid]['text'].replace('\r', ' ')
        except Exception as e:
            print(e)
            temp = "-"
        return temp
