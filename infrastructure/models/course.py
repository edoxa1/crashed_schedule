from typing import List, Dict

from infrastructure.models.types import BaseType, Laboratory, Lecture, Seminar, Tutorial, Recitation, Other
from infrastructure.models.section import Section


class Course:
    def __init__(self, abbr: str, title: str):
        self.abbr = abbr
        self.title = title
        self.section_types: List[str] = []
        self.sections: Dict[str, BaseType] = {}

    def add_section(self, section: Section):
        for key, item in section_types.items():
            if key in section.course_type:
                if item not in self.section_types:
                    self.section_types.append(item)
                    match item:
                        case "Laboratory":
                            self.sections[item] = Laboratory(abbr=self.abbr)
                        case "Lecture":
                            self.sections[item] = Lecture(abbr=self.abbr)
                        case "Seminar":
                            self.sections[item] = Seminar(abbr=self.abbr)
                        case "Tutorial":
                            self.sections[item] = Tutorial(abbr=self.abbr)
                        case "Recitation":
                            self.sections[item] = Recitation(abbr=self.abbr)

                self.sections[item].add_section(section)
                return

        new_type = section.course_type[1:len(section.course_type)]
        if new_type not in self.sections.keys():
            self.sections[new_type] = Other(abbr=self.abbr)
        self.sections[new_type].replace_type_by_course_type(new_type)
        self.sections[new_type].add_section(section)

    def get_section(self) -> Dict[str, BaseType]:
        return self.sections

    def get_info(self) -> str:
        text = f'{self.abbr} - {self.title}'
        return text


section_types = {
    "Lb": "Laboratory",
    "L": "Lecture",
    "S": "Seminar",
    "T": "Tutorial",
    "R": "Recitation"
}
