from .base import Model, ReadModel, NamedModel
from datetime import datetime
import uuid
from typing import List, Optional
from dateutil.relativedelta import relativedelta

from enum import Enum

from pydantic import EmailStr, Field, root_validator, validator, ConfigDict, StringConstraints



class SubjectCreate(NamedModel):
    pass

class SubjectUpdate(NamedModel):
    pass

class SubjectRead(NamedModel, ReadModel):
    model_config = ConfigDict(from_attributes=True)
    pass