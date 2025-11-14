"""Custom exception classes for the genoplot library."""


class GenoplotError(Exception):
    """Base exception for all genoplot-related errors."""

    pass


class GedcomParseError(GenoplotError):
    """Error parsing or reading a GEDCOM file."""

    pass


class IndividualNotFoundError(GenoplotError):
    """Individual ID not found in pedigree."""

    def __init__(self, individual_id: int):
        self.individual_id = individual_id
        super().__init__(f"Individual not found in pedigree: {individual_id}")


class FamilyNotFoundError(GenoplotError):
    """Family ID not found in pedigree."""

    def __init__(self, family_id: int):
        self.family_id = family_id
        super().__init__(f"Family not found in pedigree: {family_id}")


class InvalidLayoutError(GenoplotError):
    """Error during graph layout calculation."""

    pass


class InvalidParameterError(GenoplotError):
    """Invalid parameter value provided."""

    def __init__(self, param_name: str, param_value, reason: str = ""):
        self.param_name = param_name
        self.param_value = param_value
        message = f"Invalid value for parameter '{param_name}': {param_value}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class PedigreeNotDefinedError(GenoplotError):
    """Pedigree reference is not defined when required."""

    pass
