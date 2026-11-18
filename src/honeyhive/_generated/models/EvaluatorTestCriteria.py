from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .BooleanIsFalseTestCriteria import BooleanIsFalseTestCriteria
from .BooleanIsTrueTestCriteria import BooleanIsTrueTestCriteria
from .CategoricalCategoryEqTestCriteria import CategoricalCategoryEqTestCriteria
from .CategoricalCategoryNeqTestCriteria import CategoricalCategoryNeqTestCriteria
from .CategoricalCategoryNotOneOfTestCriteria import (
    CategoricalCategoryNotOneOfTestCriteria,
)
from .CategoricalCategoryOneOfTestCriteria import CategoricalCategoryOneOfTestCriteria
from .CategoricalNumericBetweenTestCriteria import CategoricalNumericBetweenTestCriteria
from .CategoricalNumericEqTestCriteria import CategoricalNumericEqTestCriteria
from .CategoricalNumericGteTestCriteria import CategoricalNumericGteTestCriteria
from .CategoricalNumericGtTestCriteria import CategoricalNumericGtTestCriteria
from .CategoricalNumericLteTestCriteria import CategoricalNumericLteTestCriteria
from .CategoricalNumericLtTestCriteria import CategoricalNumericLtTestCriteria
from .CategoricalNumericNeqTestCriteria import CategoricalNumericNeqTestCriteria
from .CategoricalNumericNotBetweenTestCriteria import (
    CategoricalNumericNotBetweenTestCriteria,
)
from .NumericBetweenTestCriteria import NumericBetweenTestCriteria
from .NumericEqTestCriteria import NumericEqTestCriteria
from .NumericGteTestCriteria import NumericGteTestCriteria
from .NumericGtTestCriteria import NumericGtTestCriteria
from .NumericLteTestCriteria import NumericLteTestCriteria
from .NumericLtTestCriteria import NumericLtTestCriteria
from .NumericNeqTestCriteria import NumericNeqTestCriteria
from .NumericNotBetweenTestCriteria import NumericNotBetweenTestCriteria
from .NumericNotOneOfTestCriteria import NumericNotOneOfTestCriteria
from .NumericOneOfTestCriteria import NumericOneOfTestCriteria
from .StringContainsTestCriteria import StringContainsTestCriteria
from .StringEqTestCriteria import StringEqTestCriteria
from .StringNeqTestCriteria import StringNeqTestCriteria
from .StringNotOneOfTestCriteria import StringNotOneOfTestCriteria
from .StringOneOfTestCriteria import StringOneOfTestCriteria

__all__ = ["EvaluatorTestCriteria"]


class EvaluatorTestCriteria(BaseModel):
    """
    EvaluatorTestCriteria model
    """

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "allow",
        "protected_namespaces": (),
    }

    field: str = Field(validation_alias="field")

    criteria: Union[
        NumericGtTestCriteria,
        NumericGteTestCriteria,
        NumericLtTestCriteria,
        NumericLteTestCriteria,
        NumericEqTestCriteria,
        NumericNeqTestCriteria,
        NumericBetweenTestCriteria,
        NumericNotBetweenTestCriteria,
        NumericOneOfTestCriteria,
        NumericNotOneOfTestCriteria,
        BooleanIsTrueTestCriteria,
        BooleanIsFalseTestCriteria,
        StringEqTestCriteria,
        StringNeqTestCriteria,
        StringContainsTestCriteria,
        StringOneOfTestCriteria,
        StringNotOneOfTestCriteria,
        CategoricalNumericGtTestCriteria,
        CategoricalNumericGteTestCriteria,
        CategoricalNumericLtTestCriteria,
        CategoricalNumericLteTestCriteria,
        CategoricalNumericEqTestCriteria,
        CategoricalNumericNeqTestCriteria,
        CategoricalNumericBetweenTestCriteria,
        CategoricalNumericNotBetweenTestCriteria,
        CategoricalCategoryEqTestCriteria,
        CategoricalCategoryNeqTestCriteria,
        CategoricalCategoryOneOfTestCriteria,
        CategoricalCategoryNotOneOfTestCriteria,
    ] = Field(validation_alias="criteria")
