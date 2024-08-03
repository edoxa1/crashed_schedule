from infrastructure.models.section import Section


class SectionType:
    _type = ''

    def __init__(self, abbr: str):
        self.abbr = abbr
        self.sections = []

    def add_section(self, section: Section):
        self.sections.append(section)

    def check_section(self, other: Section):
        raise 'Override!'

    def sort_sections(self):
        self.sections.sort(key=lambda section: section.name)

    def get_type(self) -> str:
        return self._type

    def replace_type_by_course_type(self, course_type: str):
        self._type = course_type

    def __call__(self):
        return self.sections

    def __iter__(self):
        yield from self.sections


class Laboratory(SectionType):
    _type = 'Laboratory'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'Lb' in other.name


class Lecture(SectionType):
    _type = 'Lecture'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'L' == other.name[-1]


class Recitation(SectionType):
    _type = 'Recitation'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'R' == other.name[-1]


class Seminar(SectionType):
    _type = 'Seminar'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'S' == other.name[-1]


class Tutorial(SectionType):
    _type = 'Tutorial'

    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        return 'T' == other.name[-1]


class Other(SectionType):
    def __init__(self, abbr: str):
        super().__init__(abbr)

    def check_section(self, other: Section):
        pass
