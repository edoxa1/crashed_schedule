from typing import List

from infrastructure.models.course import Course


class CoursesRepo:
    def __init__(self, courses: List[Course]):
        self.courses = courses
        self.course_abbrs = [course.abbr for course in self.courses]

    def search_course(self, query: str) -> List[Course]:
        search_abbr = query.lower().replace(' ', '')
        courses: List[Course] = []
        for abbr in self.course_abbrs:
            if len(courses) > 4:
                break

            if search_abbr in abbr.lower().replace(' ', ''):
                course = self.get_course_by_abbr(abbr)
                courses.append(course)

        return courses if len(courses) > 0 else None

    def get_course_by_abbr(self, search_abbr: str) -> Course:
        search_abbr = search_abbr.lower().replace(' ', '')
        for index, course in enumerate(self.courses):
            if course.abbr.lower().replace(' ', '') == search_abbr:
                return course

        return None

    def get_course_with_index_by_abbr(self, search_abbr: str) -> tuple[int, Course]:
        search_abbr = search_abbr.lower().replace(' ', '')
        for index, course in enumerate(self.courses):
            if course.abbr.lower().replace(' ', '') == search_abbr:
                return index, course

        return None

    def get_course_by_index(self, index: int) -> Course:
        return self.courses[index]

