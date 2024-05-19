from typing import List

from infrastructure.models.course import Course
from infrastructure.models.types import BaseType


def found_courses_text(courses: List[Course]) -> str:
    text = ''
    for course in courses:
        text += f'{course.get_info()}\n\n'

    return text


def course_type_sections_text(stype: BaseType) -> str:
    text = ''
    for section in stype.sections:
        text += f'{section.get_info_short()}\n'

    return text
