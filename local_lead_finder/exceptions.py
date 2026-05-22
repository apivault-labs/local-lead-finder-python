"""Exception classes for the Local Lead Finder SDK."""


class LocalLeadFinderError(Exception):
    """Base exception for all SDK errors."""


class AuthenticationError(LocalLeadFinderError):
    """Raised when the Apify API token is missing or invalid."""


class ActorRunError(LocalLeadFinderError):
    """Raised when the actor run fails on Apify infrastructure."""


class ActorTimeoutError(LocalLeadFinderError):
    """Raised when the actor run does not finish within the allowed timeout."""
