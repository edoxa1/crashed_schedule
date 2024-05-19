from infrastructure.models.section import Section


class BaseType:
    _type = ''

    def __init__(self, abbr: str):
        self.abbr = abbr
        self.sections = []

    def add_section(self, section: Section):
        self.sections.append(section)

    def check_section(self, other: Section):
        raise 'Override!'

    def sort_sections(self):
        self.sections.sort(key=lambda section: section.course_type)

    def get_type(self) -> str:
        return self._type

    def replace_type_by_course_type(self, course_type: str):
        self._type = course_type


class Laboratory(BaseType):
    _type = 'Laboratory'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'Lb' in other.course_type


class Lecture(BaseType):
    _type = 'Lecture'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'L' == other.course_type[-1]


class Recitation(BaseType):
    _type = 'Recitation'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'R' == other.course_type[-1]


class Seminar(BaseType):
    _type = 'Seminar'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'S' == other.course_type[-1]


class Tutorial(BaseType):
    _type = 'Tutorial'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'T' == other.course_type[-1]


class Other(BaseType):
    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        pass
