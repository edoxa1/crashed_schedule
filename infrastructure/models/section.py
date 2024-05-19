from typing import List, Dict
from datetime import datetime
from dateutil import parser

weekdays_dict = {
    'M': 'Monday',
    'T': 'Tuesday',
    'W': 'Wednesday',
    'R': 'Thursday',
    'F': 'Friday',
    'S': 'Saturday'
}


class Section:
    def __init__(self, section_id: int, abbr: str, course_type: str, title: str,
                 credits_us: str, credits_eu: str,
                 start_date: str, end_date: str, weekdays: str, times: str,
                 enrolled: int, course_capacity: int,
                 faculty: str, room: str):
        self.section_id: int = section_id
        self.abbr: str = abbr if abbr else 'N/A'
        self.course_type: str = course_type if course_type else 'N/A'
        self.title: str = title if title else 'N/A'
        self.credits_us: str = credits_us if credits_us else 'N/A'
        self.credits_eu: str = credits_eu if credits_eu else 'N/A'
        self.start_date: str = start_date if start_date else 'N/A'
        self.end_date: str = end_date if end_date else 'N/A'
        self.weektimes: List[Dict[str, datetime]] = \
            self.__parse_weektimes([weekdays_dict[day] for day in weekdays.split()], times)
        self.multiple_times = False
        self.enrolled: str = enrolled
        self.course_capacity: str = course_capacity if course_capacity else 'N/A'
        self.faculty: str = faculty if faculty else 'N/A'
        try:
            self.room: str = room.split('-')[0].strip() if room else 'N/A'
        except ValueError:
            self.room = room if room else 'N/A'

    def get_info(self) -> str:
        text = f'{self.abbr} [{self.course_type}] - {self.title} \n{self.credits_eu} ECTS\n' \
               f'{self.start_date} - {self.end_date}\n' \
               f'{self.__pretty_times()}\n' \
               f'{self.enrolled}/{self.course_capacity}\n' \
               f'{self.faculty}\n' \
               f'{self.room}\n\n'

        return text

    def get_info_short(self) -> str:
        text = f'{self.abbr} [{self.course_type}] - {self.title}\n' \
               f'{self.faculty}\n' \
               f'<code>{self.__pretty_times()}\n' \
               f'Cap: {self.enrolled}/{self.course_capacity}\n</code>' \

        return text

    def get_course_overall_info(self) -> str:
        text = f'{self.abbr} - {self.title} | ' \
               f'{self.credits_eu} ECTS\n\n'

        return text

    def add_time(self, weekdays: str, times: str):
        start_end_times = times.split('-')
        for weekday in weekdays:
            start_time = parser.parse(f'{start_end_times[0]}')
            end_time = parser.parse(f'{start_end_times[1]}')
            time_block = {
                'weekday': weekday,
                'start': start_time,
                'end': end_time
            }
            self.weektimes.append(time_block)
            self.multiple_times = True

    def __parse_weektimes(self, weekdays: List[str], times: str) -> List[Dict[str, datetime]]:
        weektimes: List[Dict[str, datetime]] = []
        start_end_times = times.split('-')
        for weekday in weekdays:
            weekday_letter = 'N/A'
            for key, value in weekdays_dict.items():
                if value == weekday:
                    weekday_letter = key

            start_time = parser.parse(f'{start_end_times[0]}')
            end_time = parser.parse(f'{start_end_times[1]}')

            time_block = {
                'weekday': weekday_letter,
                'start': start_time,
                'end': end_time
            }

            weektimes.append(time_block)

        return weektimes

    def __pretty_times(self) -> str:
        text = ''
        for weektime in self.weektimes:
            start = weektime['start'].strftime('%I:%M %p')
            end = weektime['end'].strftime('%I:%M %p')
            text += f'{weektime["weekday"]}: {start} - {end}\n'
        if text == '':
            text = 'Online/Distant'

        return text.rstrip()

    def __eq__(self, other):
        if not isinstance(other, Section):
            return False

        return self.abbr == other.abbr and self.course_type == other.course_type
