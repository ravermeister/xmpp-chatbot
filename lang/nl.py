# coding=utf-8

language = "dutch"

help_file = {
    'help': '!help -- Laat deze tekst zien',
    'version': '!version domain.tld  -- Vraag XMPP server versie op',
    'uptime': '!uptime domain.tld -- Bekijk de runtime van de XMPP-server',
    'contact': '!contact domain.tld -- Toon de contactgegevens van de XMPP server',
    'info': '!info domain.tld -- Toon een samenvatting van de informatie hierboven',
    'user': '!user domain.tld -- Toon het aantal geregistreerde/online gebruikers',
    'xep': '!xep XEP Number -- Toon informatie over een specifieke XEP',
    'man': '!man manpage -- Toon informatie over de opgevraagde man-page',
    'chuck': '!chuck en -- Vertel een Chuck Norris grap'
}
possible_answers = {
    '1': 'Ik heb dat begrepen, %s.',
    '2': 'Het spijt me voor %s.',
    '3': '%s heb je geprobeerd om het opnieuw aan en uit te zetten?',
    '4': '%s fijne dag nog',
    '5': 'Hallo %s',
    '6': '%s may the force be with you'
}
error_messages = {
    '1': 'niet bereikbaar',
    '2': 'onjuist doelwit',
    '3': 'je bent niet gemachtigd om deze command uit te voeren %s'
}
command_messages = {
    'uptime.running': "%s staat aan voor %s",
    'uptime.year': "Jaar",
    'uptime.years': "Jaren",
    'uptime.week': "Week",
    'uptime.weeks': "Weken",
    'uptime.day': "Dag",
    'uptime.days': "Dagen",
    'uptime.hour': "Uur",
    'uptime.hours': "Uren",
    'uptime.minute': "Minuut",
    'uptime.minutes': "Minuten",
    'uptime.second': "Seconde",
    'uptime.seconds': "Seconden",

    'contact.addresses': "contact adressen voor %s zijn\n",
    'contact.for': "%s voor %s is\n",
    'contact.not-configured': "%s heeft geen contact adres geconfigureerd.",
    'contact.not-defined': "%s for %s are not defined.",

    'users.registered': "Geregistreerde Gebruikers: %s",
    'users.invalid-data': "Ongeldige gegevens ontvangen als reactie",
    'users.online': "Online Gebruikers: %s",
    'users.using': "%s gebruiken %s",

    'version.unknown-os': "een onbekend platform",
    'version.running-on': "%s draait %s versie %s op %s",

    'xep.no-tag': "%s heeft geen %s tag.",
    'xep.unavailable': "XEP-%s : is niet beschikbaar."
}
