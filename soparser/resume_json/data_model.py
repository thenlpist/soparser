import abc
import copy
import operator
import datetime
import json
import random
from collections import Counter, defaultdict
from datetime import date
from typing import Optional


from pydantic import BaseModel, ConfigDict, ValidationError


# WIP
# TODO
# - need a custom date object that only has year and month (for most cases) ... OR plan to throw away the day


class ResumeSection(BaseModel, abc.ABC):
    @abc.abstractmethod
    def render(self):
        pass


# ----------------------------------------------------------------------------------------------------------------------
# Awards
# ----------------------------------------------------------------------------------------------------------------------
class Award(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str
    date: Optional[date]
    awarder: Optional[str]
    summary: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Basics
# ----------------------------------------------------------------------------------------------------------------------
class Profile(BaseModel):
    model_config = ConfigDict(strict=True)

    url: str
    username: Optional[str]
    network: Optional[str]


class Location(BaseModel):
    model_config = ConfigDict(strict=True)

    city: str
    address: Optional[str]
    region: Optional[str]
    countrycode: Optional[str]
    postalcode: Optional[str]


class Basics(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    label: Optional[str]
    website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    summary: Optional[str]
    url: Optional[str]
    profiles: Optional[list[Profile]]
    location: Optional[Location]


# ----------------------------------------------------------------------------------------------------------------------
# Certificates
# ----------------------------------------------------------------------------------------------------------------------
class Certificate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    date: Optional[date]
    url: Optional[str]
    issuer: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Education
# ----------------------------------------------------------------------------------------------------------------------
class Education(BaseModel):
    model_config = ConfigDict(strict=True)

    institution: str
    area: Optional[str]
    studytype: Optional[str]
    startdate: Optional[date]
    enddate: Optional[date]
    url: Optional[str]
    score: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Interests
# ----------------------------------------------------------------------------------------------------------------------
class Interest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str

    def prerender(self):
        return self.name


# ----------------------------------------------------------------------------------------------------------------------
# Languages
# ----------------------------------------------------------------------------------------------------------------------
class Language(BaseModel):
    model_config = ConfigDict(strict=True)

    language: str
    fluency: Optional[str]

    def prerender(self, key_order):
        result = []
        for k in key_order:
            result.append(self.__getattribute__(k))
        return f": ".join(result)


# ----------------------------------------------------------------------------------------------------------------------
# Projects
# ----------------------------------------------------------------------------------------------------------------------
class Project(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    enddate: Optional[date]
    startdate: Optional[date]
    description: Optional[str]
    highlights: Optional[list[str]]
    url: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Publications
# ----------------------------------------------------------------------------------------------------------------------
class Publication(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    publisher: Optional[str]
    summary: Optional[str]
    releasedate: Optional[date]
    url: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# References
# ----------------------------------------------------------------------------------------------------------------------
class Reference(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    reference: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Skills
# ----------------------------------------------------------------------------------------------------------------------
class Skill(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    level: Optional[str]
    keywords: Optional[list[str]]


# ----------------------------------------------------------------------------------------------------------------------
# Volunteer
# ----------------------------------------------------------------------------------------------------------------------
class Volunteer(BaseModel):
    model_config = ConfigDict(strict=True)

    organization: str
    enddate: Optional[date]
    startdate: Optional[date]
    position: Optional[str]
    summary: Optional[str]
    highlights: Optional[list[str]]
    url: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Work
# ----------------------------------------------------------------------------------------------------------------------
class Work(BaseModel):
    model_config = ConfigDict(strict=False)

    position: str
    name: str
    location: Optional[str]
    description: Optional[str]
    enddate: Optional[date]
    startdate: Optional[date]
    summary: Optional[str]
    highlights: Optional[list[str]]
    url: Optional[str]


# ----------------------------------------------------------------------------------------------------------------------
# Resume
# ----------------------------------------------------------------------------------------------------------------------
class Resume(BaseModel):
    model_config = ConfigDict(strict=True)

    basics: Optional[Basics]
    education: list[Optional[Education]]
    work: list[Optional[Work]]
    projects: list[Optional[Project]]
    skills: list[Optional[Skill]]
    publications: list[Optional[Publication]]
    awards: list[Optional[Award]]
    certificates: list[Optional[Certificate]]
    volunteer: list[Optional[Volunteer]]
    languages: list[Optional[Language]]
    interests: list[Optional[Interest]]
    references: list[Optional[Reference]]




# ----------------------------------------------------------------------------------------------------------------------
# Resume Deserializer
# ----------------------------------------------------------------------------------------------------------------------
class ResumeSerializer:

    def to_json_resume(self, resume0):
        resume = copy.deepcopy(resume0)
        basics = resume.basics
        j_basics = basics.__dict__
        if basics.location:
            j_basics["location"] = basics.location.__dict__
        else:
            j_basics["location"] = Location(city='', address='', region='', countrycode='', postalcode='').__dict__
        j_basics["profiles"] = []

        j_resume = {
            "basics": j_basics,
            "work": [self._dictize(x) for x in resume.work],
            "education": [self._dictize(x) for x in resume.education],
            "projects": [self._dictize(x) for x in resume.projects],
            "volunteer": [self._dictize(x) for x in resume.volunteer],
            "skills": [self._dictize(x) for x in resume.skills],
            "publications": [self._dictize(x) for x in resume.publications],
            "languages": [self._dictize(x) for x in resume.languages],
            "awards": [self._dictize(x) for x in resume.awards],
            "certificates": [self._dictize(x) for x in resume.certificates],
            "references": [self._dictize(x) for x in resume.references],
            "interests": [self._dictize(x) for x in resume.interests]
        }
        return j_resume


    def _dt_to_str(self, dt: datetime.date):
        return dt.strftime("%Y-%m")


    def _dictize(self, obj):
        d = obj.__dict__
        date_keys = ["startdate", "enddate", "date", "releasedate"]
        for k in date_keys:
            # print(k)
            if k in d:
                dt = d[k]
                if dt:
                    dt_str = self._dt_to_str(dt)
                    d[k] = dt_str
        for k, v in d.items():
            if v == None:
                d[k] = ""
        return d

