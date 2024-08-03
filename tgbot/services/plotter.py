import io
import logging
from datetime import datetime
from typing import List

from matplotlib import set_loglevel
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from infrastructure.models.section import Section

set_loglevel('warning')
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

DAYS = ['M', 'T', 'W', 'R', 'F', 'S']
DAY_NAMES = ['Monday',
             'Tuesday',
             'Wednesday',
             'Thursday',
             'Friday',
             'Saturday']

_DAY_LIMIT = 5
_START_TIME = 7
_END_TIME = 21
_SPACINGS = [  # two different SPACINGS for 5 days and 6 days. Kostyl' master
    # 5 days:
    ['         ',
     '        ',
     '     ',
     '       ',
     '          '],
    # 6 days:
    ['     ',
     '     ',
     '   ',
     '    ',
     '       ',
     '    ']
]


def create_plot(sections: List[Section], colour: str, text_colour: str = 'white'):
    (fig, ax) = plt.subplots(figsize=(7, 14))
    fig: Figure = fig
    ax: Axes = ax

    plt.setp(ax.xaxis.get_majorticklabels(), ha='left')
    plt.gca().invert_yaxis()  # Invert y-axis to have 7 AM at the top

    # Add sections to the calendar
    limit = _DAY_LIMIT
    for section in sections:
        for time_slot in section.weektimes:
            day = time_slot[0]
            start_time, end_time = time_slot[1], time_slot[2]
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            start = _END_TIME + _START_TIME - (start_hour + start_minute / 60)
            end = _END_TIME + _START_TIME - (end_hour + end_minute / 60)
            time = f'{start_time} - {end_time}'
            day_index = DAYS.index(day)
            if day == 'S':
                limit = _DAY_LIMIT + 1
            setup_plot(ax, limit)

            rect = patches.Rectangle((day_index, start), 1, end-start,
                                     edgecolor='gray', facecolor=colour, alpha=1, zorder=2)
            ax.add_patch(rect)
            ax.text(day_index + 0.5, (start + end) / 2,
                    f'{section.get_short_info()}\n{time}',
                    ha='center', va='center', color=text_colour, fontsize=8, wrap=True)

    fig.patch.set_facecolor('black')  # Figure background color
    ax.set_facecolor('black')  # Axes background color

    plt.title('Weekly Schedule')
    plt.tight_layout()
    plt.show()
    # buffer: io.BytesIO = io.BytesIO()
    # plt.savefig(buffer, dpi=100, format='jpg')
    # plt.close(plt.gcf())
    # plt.clf()
    # return buffer


def setup_plot(ax, limit: int = 5):
    # Set the major and minor ticks
    ax.set_xticks(range(limit))
    ax.set_xticklabels([i for i in _iter_days(limit != 5)], rotation=0, minor=False, position=(2, 0))

    ax.set_yticks(range(_END_TIME, _START_TIME, -1))  # From 9 AM to 9 PM
    ax.set_yticklabels([f'{hour}:00' for hour in range(_START_TIME, _END_TIME)])

    # Draw grid
    ax.grid(True, which='both', linestyle='-', linewidth=0.5, color='gray')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.title.set_color('white')

    ax.set_xlim(0, limit)
    ax.set_ylim(_START_TIME, _END_TIME)



def _to_24h(time: str) -> str:
    temp = datetime.strptime(time, '%I:%M %p')
    return temp.strftime('%H:%M')


def _iter_days(longer: bool):
    spacings = _SPACINGS[1 if longer else 0]
    for i in range(len(spacings)):
        yield spacings[i] + DAY_NAMES[i]
