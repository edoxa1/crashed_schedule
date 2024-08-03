from typing import List

from infrastructure.models.course import Course
from infrastructure.models.section import Section
from infrastructure.models.types import SectionType


def found_courses_text(courses: List[Course]) -> str:
    text = ''
    for course in courses:
        text += f'{course.get_info()}\n\n'

    return text


def course_type_sections_text(sections: list[Section]) -> str:
    text = ''
    for section in sections:
        print(section.get_short_info())
        text += f'{section.get_info()}\n'
    print(': ', text)

    return text
