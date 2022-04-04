# coding=utf-8

language = "deutsch"

help_file = {
    'help': '!help -- diese Hilfe Anzeigen',
    'version': '!version domain.tld  -- die XMPP Server Version anzeigen',
    'uptime': '!uptime domain.tld -- die XMPP Server Laufzeit anzeigen',
    'contact': '!contact domain.tld -- die XMPP Server Kontakt Informationen anzeigen',
    'info': '!info domain.tld -- eine zusammenfassung der oberen Funktionen',
    'user': '!user domain.tld -- die anzahl der registrierten/online Benutzer auflisten',
    'xep': '!xep XEP Number -- die Informationen über eine XMPP XEP Spezifikation anzeigen',
    'man': '!man manpage -- einen Link zu der Man Page des angegeben Programms anzeigen',
    'chuck': '!chuck de -- einen ChuckNorris Witz erzählen'
}
possible_answers = {
    '1': '%s möge die Macht mit dir sein',
    '2': '%s es würde gegen meine Programmierung verstoßen, eine Gottheit zu personifizieren.',
    '3': 'Ich bin Luke Skywalker. %s Ich bin hier, um Sie zu retten.',
    '4': '%s vergiss nicht, die Macht wird mit dir sein, immer.',
    '5': '%s die Macht ist stark in meiner Familie. Mein Vater hat sie, ich habe sie, sogar meine Schwester '
         'hat sie.',
    '6': '%s ich liebe es, wenn ein Plan funktioniert.',
    '7': '%s Es steht ihnen Frei, zu schreien und zu brüllen. Aber es wird sie niemand hören.',
    '8': '%s ich steig nicht in ein Flugzeug.'
}
error_messages = {
    '1': 'nicht erreichbar',
    '2': 'kein gültiges Ziel',
    '3': 'Sie dürfen den Befehl %s nicht ausführen'
}
command_messages = {
    'uptime.running': "%s läuft seit %s",
    'uptime.year': "Jahr",
    'uptime.years': "Jahre",
    'uptime.week': "Woche",
    'uptime.weeks': "Wochen",
    'uptime.day': "Tagen",
    'uptime.days': "Tagen",
    'uptime.hour': "Stunde",
    'uptime.hours': "Stunden",
    'uptime.minute': "Minute",
    'uptime.minutes': "Minuten",
    'uptime.second': "Sekunde",
    'uptime.seconds': "Sekunden",

    'contact.addresses': "Kontakt Adressen für %s sind\n",
    'contact.for': "%s für %s sind\n",
    'contact.not-configured': "%s hat keine Kontakt Adresse konfiguriert.",
    'contact.not-defined': "%s für %s sind nicht definiert.",

    'users.registered': "Registered Users: %s",
    'users.invalid-data': "ungültige Daten in der Antwort erhalten",
    'users.online': "Online Benutzer: %s",
    'users.using': "%s verwendet %s",

    'version.unknown-os': "einem unbekannten System",
    'version.running-on': "%s läuft mit %s Version %s auf %s",

    'xep.no-tag': "%s hat keinen %s tag.",
    'xep.unavailable': "XEP-%s : ist nicht verfügbar."
}
