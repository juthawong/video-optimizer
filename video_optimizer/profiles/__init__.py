# encoding: utf-8
import logging
import abc


log = logging.getLogger(__name__)
PROFILES = {}


def register(profile_class):
    PROFILES[profile_class.get_prefix()] = profile_class
    return profile_class


def select_profile(name, options):
    profile = PROFILES.get(name, None)
    if not profile:
        raise ValueError("Unknown profile %s" % name)

    log.info('Select "%s" profile', name)

    return profile(options).arguments


def profile_options(parser):
    for prefix, profile in PROFILES.items():
        group = parser.add_argument_group('Profile settings "{}"'.format(prefix))

        for option in profile.expose_options():
            name = option.pop('name')
            group.add_argument(
                "--profile-{0}-{1}".format(prefix, name.replace("_", "-")),
                dest="{0}_{1}".format(prefix, name.replace("-", "_")),
                metavar=option.get('default') or name.upper(),
                **option
            )


class BaseProfile(object):
    def __init__(self, options):
        prefix = self.get_prefix()
        for option in self.expose_options():
            name = option['name'].replace("-", "_")
            setattr(
                self,
                name,
                getattr(
                    options,
                    "{0}_{1}".format(
                        prefix,
                        name,
                    ),
                    None
                )
            )

        pass

    @classmethod
    @abc.abstractmethod
    def get_prefix(cls):
        pass

    @classmethod
    @abc.abstractmethod
    def expose_options(cls):
        pass

    @abc.abstractmethod
    def arguments(self, streams):
        pass


import apple_optimized
