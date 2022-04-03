# coding=utf-8

language = "english"

help_file = {
    'help': '!help -- display this text',
    'version': '!version domain.tld  -- receive XMPP server version',
    'uptime': '!uptime domain.tld -- receive XMPP server uptime',
    'contact': '!contact domain.tld -- receive XMPP server contact address info',
    'info': '!info domain.tld -- receive a summary of the informations mentioned above',
    'user': '!user domain.tld -- display amount of registered/online user',
    'xep': '!xep XEP Number -- receive information about the specified XEP',
    'man': '!man manpage -- receive information about the specified man page',
    'chuck': '!chuck en -- tell a Chuck Norris Joke'
}
possible_answers = {
    '1': 'I heard that, %s.',
    '2': 'I am sorry for that %s.',
    '3': '%s did you try turning it off and on again?',
    '4': '%s have a nice day',
    '5': 'howdy %s',
    '6': '%s may the force be with you'
}
error_messages = {
    '1': 'not reachable',
    '2': 'not a valid target',
    '3': 'you are not allowed to execute the command %s'
}
command_messages = {
    'uptime.running': "%s is running for %s",
    'uptime.year': "Year",
    'uptime.years': "Years",
    'uptime.week': "Week",
    'uptime.weeks': "Weeks",
    'uptime.day': "Day",
    'uptime.days': "Days",
    'uptime.hour': "Hour",
    'uptime.hours': "Hours",
    'uptime.minute': "Minute",
    'uptime.minutes': "Minutes",
    'uptime.second': "Second",
    'uptime.seconds': "Seconds"
}
