'''

Creates a Custom Logging Object with 5 tiers

    0       CYAN        TRACE       Step-By-Step Operation Processing Logging
    1       GREEN       DEBUG       Operations Logging
    2       BLUE        INFO        Process Logging
    3       MAGENTA     WARNING     Operation Processing Failure
    4       YELLOW      ERROR       Total Operation Failure
    5       RED         CRITICAL    Total Process Failure

Format:
    [LEVEL] MM-DD-YYYY HH:MM:SS.SSS (LOCATION) --> "ERROR MESSAGE"

Important Notes:
    All events should be recorded in "logger/data/events.log"
    If the level index surpasses the logging threshold it should be output to the console
    All errors (level 3+) should be recorded in "logger/data/errors.log"
    Critical Errors should trigger a Developer Notification (via Email/SMS)

Bonus Feature:
    Statistic Recall
        - Pull statistics for a specified time period

        Format:
            Since MM/DD/YYYY, there have been -->
                - 14,287 Steps Taken
                - 394 Operations
                - 76 Processes
                - 92 Warnings
                - 28 Errors
                - 11 Critical Failures

'''


from colorama import init
from colorama import Fore
from colorama import Style

from os import getenv
from os.path import abspath
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from twilio.rest import Client


levels = {
    'TRACE': 0,
    'DEBUG': 1,
    'INFO': 2,
    'WARNING': 3,
    'ERROR': 4,
    'CRITICAL': 5
}

names = {
    'TRACE': 'Steps Taken',
    'DEBUG': 'Operations',
    'INFO': 'Processes',
    'WARNING': 'Warnings',
    'ERROR': 'Errors',
    'CRITICAL': 'Critical Failures'
}

parser_config = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400
}


class StatEngine():
    ''' Timelapse Statistical Analyzation of Recorded Events '''

    @staticmethod
    def get_timestamp(duration: str) -> datetime:
        seconds = 0
        increments = duration.split()

        for increment in increments:
            seconds += int(increment[:-1]) * parser_config[increment[-1].lower()]

        delta = timedelta(seconds=seconds)
        now = datetime.now()

        return now - delta

    @staticmethod
    def sort_events(recent: list) -> dict:
        sorted = { key : 0 for key in config }
        for event in recent:
            type = event[:11].strip().replace('[', '').replace(']', '')
            sorted[type] += 1

        return { names[key] : value for key, value in sorted.items() }


    @classmethod
    def retrieve_events(cls, timestamp: datetime) -> dict:
        recent_events = []

        with open('/home/savant/ava/apps/api/logger/data/events.log', 'r+') as log:
            events = [line.replace('\n', '') for line in log.readlines()]
            events.reverse()

        for event in events:
            raw_stamp = event[12:29]
            stamp = datetime.strptime(raw_stamp, '%m-%d-%y %H:%M:%S')
            if stamp >= timestamp:
                recent_events.append(event)

        return cls.sort_events(recent_events)

    @classmethod
    def send_report(cls, duration: str) -> None:
        load_dotenv()

        earliest = cls.get_timestamp(duration)
        statistics = cls.retrieve_events(earliest)

        report = f'In the past {duration}, there have been: \n\t- '
        report += '\n\t- '.join([f'{value} {key}' for key, value in statistics.items()])

        client = Client(getenv('TWILIO_SID'), getenv('TWILIO_KEY'))

        client.messages.create(
            to = getenv('SMS_RECEIVING'),
            from_ = getenv('SMS_SENDING'),
            body = report
        )

        return


class LoggerModule():
    ''' Customized Console Output and Filesystem Recording '''

    def __init__(self, level: int):
        ''' Initializes Colored Output and sets Logger Config '''

        init()

        self.level = level

        dir = abspath(__file__).replace('__init__.py', 'data/')
        self.logs = { key: dir + key + '.log' for key in ['events', 'errors'] }

    def _write(self, message: str, *, error: bool = False) -> None:
        with open(self.logs['events'], 'a+') as log:
            log.write(message)

        if error:
            with open(self.logs['errors'], 'a+') as log:
                log.write(message)

    def _output(self, level: int, *, message: str) -> None:
        if level >= self.level:
            print(message)

    def _notify(self, *, message: str) -> None:
        load_dotenv()
        '''
        report = (
            'Oh No! A Critical Failure has been detected in my API! \n'
            f'Here are the notes from my error handler: \n\n{message}'
        )
        '''

        report = message


        client = Client(getenv('TWILIO_SID'), getenv('TWILIO_KEY'))

        client.messages.create(
            to = getenv('SMS_RECEIVING'),
            from_ = getenv('SMS_SENDING'),
            body = report
        )

        return

    @staticmethod
    def _getTimeStamp() -> str:
        now = datetime.now()
        stamp = now.strftime('%m-%d-%y %H:%M:%S:%f')[:-3]

        return stamp

    @staticmethod
    def _start(level: str) -> str:
        output = level
        while len(output) < 12:
            output += ' '

        return output

    def trace(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()
        output = self._start('[TRACE]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.CYAN}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        self._write(file_output)
        self._output(0, message=color_output)

    def debug(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()

        output = self._start('[DEBUG]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.GREEN}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        self._write(file_output)
        self._output(1, message=color_output)

    def info(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()

        output = self._start('[INFO]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.BLUE}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        self._write(file_output)
        self._output(2, message=color_output)

    def warn(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()

        output = self._start('[WARNING]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.MAGENTA}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        self._write(file_output, error=True)
        self._output(3, message=color_output)

    def error(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()

        output = self._start('[ERROR]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.YELLOW}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        self._write(file_output, error=True)
        self._output(4, message=color_output)

    def critical(self, locale: str, message: str) -> None:
        timestamp = self._getTimeStamp()

        output = self._start('[CRITICAL]')
        file_output = output + f"{timestamp}\t({locale})\t\t{message} \n"
        color_output = f"{Fore.RED}" + output + f"{Style.RESET_ALL}{timestamp}\t({locale})\t{message}"

        notification = (
            f'[CRITICAL] \nLocation: {locale} \n'
            f'Occurred At: {timestamp} \n'
            f'Error Details: {message}'
        )

        self._write(file_output, error=True)
        self._output(5, message=color_output)
        self._notify(message=notification)


def getLogger(level: str) -> LoggerModule:
    try:
        log_level = levels[level]
    except KeyError:
        log_level = levels['TRACE']

    return LoggerModule(log_level)
