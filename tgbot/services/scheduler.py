import logging

from infrastructure.models.section import Section


def check_clash(sections: list[Section]) -> bool:
    # do preliminary check for two courses occupying the same time slot. not time-consuming as intersection check
    if not _hash_check(sections):
        # there are possibility that two courses may occupy different time slots, but intersect with each other.
        return _intersection_check(sections)


def _hash_check(sections: list[Section]) -> bool:
    time_hashes = []
    for section in sections:
        time_hashes.extend(map(hash, section.weektimes))  # add hashes of course times into list
    if len(time_hashes) != len(set(time_hashes)):
        # if there is same time occupied by two courses, then there is a duplicate. set(list) will remove them.
        return True

    return False


def _intersection_check(sections: list[Section]) -> bool:
    # todo: !
    logging.warning('Todo: intersection check')
    return False
