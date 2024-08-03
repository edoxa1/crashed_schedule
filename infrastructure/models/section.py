from collections import namedtuple
from dataclasses import dataclass, field
from json import loads, dumps

from typing import Generator
from datetime import datetime


weekdays_dict = {
    'M': 'Monday',
    'T': 'Tuesday',
    'W': 'Wednesday',
    'R': 'Thursday',
    'F': 'Friday',
    'S': 'Saturday'
}

Weektime = namedtuple('Weektime', ('day', 'start', 'end'))


@dataclass
class Section:
    school: str = 'N/A'
    level: str = 'N/A'
    abbr: str = 'N/A'
    name: str = 'N/A'
    title: str = 'N/A'
    credits_us: str = 'N/A'
    credits_eu: str = 'N/A'
    start_date: str = 'N/A'
    end_date: str = 'N/A'
    weekdays: str = ''
    times: str = ''
    weektimes: list[Weektime] = field(default_factory=list)
    multiple_times: bool = False
    enrolled: int = 0
    course_capacity: int = 0
    faculty: str = 'N/A'
    room: str = 'Online/Distant'

    def __post_init__(self):
        try:
            self.room = self.room.split('-')[0].strip() if self.room else 'N/A'
        except ValueError:
            self.room = 'N/A'
        self.weektimes = self._parse_weektimes([weekdays_dict[day] for day in self.weekdays.split()], self.times)

    def __eq__(self, other):
        if not isinstance(other, Section):
            raise ValueError("other is not an instance of `Section`")

        return self.abbr == other.abbr and self.name == other.name

    def __hash__(self):
        return hash(f'{self.abbr}{self.name}')

    def __lt__(self, other):
        return sum(map(ord, self.name)) + len(self.name) < sum(map(ord, other.name)) + len(other.name)

    def get_short_info(self) -> str:
        text = f'{self.abbr} [{self.name}]\n' \
               f'{self.room}'

        return text

    def get_info(self) -> str:
        text = f'{self.abbr} [{self.name}] - {self.title}\n' \
               f'<code>' \
               f'{self.faculty}\n' \
               f'{self._pretty_times()}\n' \
               f'</code>' \

        return text

    def get_day_info(self, time: tuple[str, str]) -> str:
        name = f'[{self.name}]'
        title = f'{self.abbr:<8}{name:>6}'
        text = f'{title:<15}|' \
               f'{time[0]:^5}-{time[1]:^5}| ' \
               f'{self.room:>5}' \

        return text

    def get_course_overall_info(self) -> str:
        text = f'{self.abbr} - {self.title} | [{self.name}]'

        return text

    def add_time(self, weekdays: str, times: str):
        start_end_times = times.split('-')
        for weekday in weekdays:
            start = datetime.strptime(start_end_times[0], '%I:%M %p')
            end = datetime.strptime(start_end_times[1], '%I:%M %p')
            time_block = Weektime(
                weekday,
                start.strftime('%H:%M'),
                end.strftime('%H:%M')
            )
            self.weektimes.append(time_block)
            self.multiple_times = True

    def to_dict(self) -> dict[str, str]:
        return vars(self)

    def to_json(self) -> str:
        return dumps(self.to_dict())

    @classmethod
    def from_json(cls, datum: str):
        datum: dict = loads(datum)
        return cls(**datum)

    @classmethod
    def from_json_to_generator(cls, datum: list[str]) -> Generator:
        for data in datum:
            section: dict = loads(data)
            yield cls(**section)

    @classmethod
    def from_json_to_list(cls, datum: list[str]) -> list:
        sections = []
        for data in datum:
            sections.append(cls.from_json(data))

        return sections

    @staticmethod
    def _parse_weektimes(weekdays: list[str], times: str) -> list[dict[str, datetime]]:
        weektimes: list[tuple[str, str, str]] = []
        start_end_times = times.split('-')
        for weekday in weekdays:
            weekday_letter = 'N/A'
            for key, value in weekdays_dict.items():
                if value == weekday:
                    weekday_letter = key

            start = datetime.strptime(start_end_times[0], '%I:%M %p')
            end = datetime.strptime(start_end_times[1], '%I:%M %p')
            time_block = Weektime(
                weekday_letter,
                start.strftime('%H:%M'),
                end.strftime('%H:%M')
            )

            weektimes.append(time_block)
        if len(weektimes) == 0:
            weektimes.append((
                'S', '08:00 PM', '08:50 PM'
            ))
        return weektimes

    def _pretty_times(self) -> str:
        text = ''
        hashes = set(map(lambda time: hash(time[1] + time[2]), self.weektimes))
        if len(hashes) == 1:
            text = ' '.join(map(lambda time: time[0], self.weektimes))
            text = f'{text}: {self.weektimes[0][1]} - {self.weektimes[0][2]}'
            return text.rstrip()

        for weektime in self.weektimes:
            start = weektime[1]  # .strftime('%I:%M %p')
            end = weektime[2]  # .strftime('%I:%M %p')
            text += f'{weektime[0]}: {start} - {end}\n'
        if text == '':
            text = 'Online/Distant'

        return text.rstrip()
