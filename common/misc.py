# coding=utf-8
import validators
import logging

from common.strings import StaticAnswers
from typing import Optional, Dict, List
from slixmpp import JID
from slixmpp_omemo import EncryptionPrepareException
from omemo.exceptions import MissingBundleException, KeyExchangeException

staticAnswers: StaticAnswers


def deduplicate(reply):
    """
    list deduplication method
    :param list reply: list containing non unique items
    :return: list containing unique items
    """
    reply_dedup = list()
    for item in reply:
        if item not in reply_dedup:
            reply_dedup.append(item)

    return reply_dedup


def validate(keyword, target):
    """
    validation method to reduce malformed query's and unnecessary connection attempts
    :param keyword: used keyword
    :param target: provided target
    :return: true if valid
    """

    # Maximum length for String arguments
    max_arg_string_length = 256

    # if keyword in domain_keywords list
    if keyword in staticAnswers.keys('domain_keywords'):
        # if target is a domain / email return True
        return (
                target is not None
                and target.strip() is not None
                and len(target) <= max_arg_string_length
                and (validators.domain(target) or validators.email(target))
        )
    # check if keyword is in number_keyword list
    elif keyword in staticAnswers.keys('number_keywords'):
        # prevent AttributeError if target is NoneType
        return (
                target is not None
                and target.strip() is not None
                and len(target) <= max_arg_string_length
                # if target only consists of digits return True
                and target.isdigit()
        )

    # if keyword is in no_arg_keywords list return True
    elif keyword in staticAnswers.keys("no_arg_keywords"):
        return True

    # check if keyword is in string_keyword list
    elif keyword in staticAnswers.keys("string_keywords"):
        return (
                target is not None
                and target.strip() is not None
                and len(target) <= max_arg_string_length
        )

    # if the target could not be validated until this return False
    return False


class HandleError:
    """
    simple XMPP error / exception class formatting the error condition
    """

    def __init__(self, error, key, target):
        # init all necessary variables
        self.text = error.text
        self.condition = error.condition
        self.key = key
        self.target = target

    def report(self):
        # return the formatted result string to the user
        text = "%s. %s %s resulted in: %s" % (self.text, self.key, self.target, self.condition)
        return text


class HandleSkipOmemoError:
    """
    handle Omemo errors that should be skipped (mark
    """

    def __init__(self, error: EncryptionPrepareException):
        # This exception is being raised when the library has tried
        # all it could and doesn't know what to do anymore. It
        # contains a list of exceptions that the user must resolve, or
        # explicitly ignore via `expect_problems`.
        # TODO: We might need to bail out here if errors are the same?

        # noinspection PyTypeChecker
        self.expect_problems = {}  # type: Optional[Dict[JID, List[int]]]
        self.exception = error
        self.retry = self.__process()

    def __process(self) -> bool:
        retry = True
        for error in self.exception.errors:
            # We choose to ignore
            # - MissingBundleException
            # - KeyExchangeException
            # It seems to be somewhat accepted that it's better not to
            # encrypt for a device if it has problems and encrypt
            # for the rest, rather than error out. The "faulty"
            # device won't be able to decrypt and should display a
            # generic message. The receiving end-user at this
            # point can bring up the issue if it happens.

            if isinstance(error, MissingBundleException):
                logging.warning(
                    "Could not find keys for device >%s< of recipient >%s<. Skipping"
                    % (error.device, error.bare_jid)
                )
                jid = JID(error.bare_jid)
                device_list = self.expect_problems.setdefault(jid, [])
                device_list.append(error.device)
            elif isinstance(error, KeyExchangeException):
                logging.warning(
                    "Could not exchange keys for device >%s< of recipient >%s<. Skipping"
                    % (error.device, error.bare_jid)
                )
                jid = JID(error.bare_jid)
                device_list = self.expect_problems.setdefault(jid, [])
                device_list.append(error.device)
            else:
                logging.error('An error occurred while fetching information on a recipient.\n%r' % error)
                retry = False
                break
        return retry

