from typing import Dict, Optional, Set

from pydantic import BaseModel


class FieldsExtension(BaseModel):
    """
    https://github.com/radiantearth/stac-api-spec/tree/master/extensions/fields#fields-api-extension
    """

    includes: Optional[Set[str]]
    excludes: Optional[Set[str]]

    def _get_field_dict(self, fields: Set[str]) -> Dict:
        """Internal method to create a dictionary for advanced include or exclude of pydantic fields on model export

        Ref: https://pydantic-docs.helpmanual.io/usage/exporting_models/#advanced-include-and-exclude
        """
        field_dict = {}
        for field in fields:
            if "." in field:
                parent, key = field.split(".")
                if parent not in field_dict:
                    field_dict[parent] = {key}
                else:
                    field_dict[parent].add(key)
            else:
                field_dict[field] = ...  # type:ignore
        return field_dict

    @property
    def filter(self) -> Dict:
        """
        Create dictionary of fields to include/exclude on model export based on the included and excluded fields passed
        to the API.  The output of this property may be passed to pydantic's serialization methods to include or exclude
        certain keys.

        Ref: https://pydantic-docs.helpmanual.io/usage/exporting_models/#advanced-include-and-exclude
        """
        include = set()
        # If only include is specified, add fields to the set
        if self.includes and not self.excludes:
            include = include.union(self.includes)
        # If both include + exclude specified, find the difference between sets
        elif self.includes and self.excludes:
            include = include.union(self.includes) - self.excludes
        return {
            "include": self._get_field_dict(include),
            "exclude": self._get_field_dict(self.excludes),
        }
