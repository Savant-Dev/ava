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
