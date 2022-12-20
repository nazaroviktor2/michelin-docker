import datetime


def replace_all(text, lst):
    for i in lst:
        text = text.replace(i, '')
    return text


def reading_speed(text:str, average_speed:int=120, average_error:datetime.timedelta=datetime.timedelta(seconds=10)):
    arr = [i for i in '!@#$%^&()_-,./;:|\~`']
    number_of_words = len(replace_all(text, arr).split())
    result_speed = number_of_words/(average_speed/60)
    min_time = datetime.timedelta(seconds=result_speed) - average_error
    min_time = min_time - datetime.timedelta(microseconds=min_time.microseconds)
    max_time = datetime.timedelta(seconds=result_speed) + average_error
    max_time = max_time-datetime.timedelta(microseconds=max_time.microseconds)
    if min_time < datetime.timedelta():
        min_time = datetime.timedelta()
    return min_time, max_time
