import abc
import copy
import datetime
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic import Field


# WIP
# TODO
# - need a custom date object that only has year and month (for most cases) ... OR plan to throw away the day


class ResumeSection(BaseModel, abc.ABC):
    @abc.abstractmethod
    def render(self):
        pass


# class Step(BaseModel):
# 	explanation: str = Field(..., title="Explanation", description="A detailed explanation of the step.")
# 	output: str = Field(..., title="Output", description="The output result of the step.")
#
# class MathResponse(BaseModel):
# 	steps: list[Step] = Field(..., title="Steps", description="A list of steps involved in solving the problem.")
# 	final_answer: str = Field(..., title="Final Answer", description="The final answer to the problem.")

# ----------------------------------------------------------------------------------------------------------------------
# Awards
# ----------------------------------------------------------------------------------------------------------------------
class Award(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str = Field(..., title="Title", description="An award title.")
    date: Optional[date] = Field(title="Date", description="The date on which an award was granted.")
    awarder: Optional[str] = Field(title="Awarder", description="The person or organization who gave an award.")
    summary: Optional[str] = Field(title="Summary", description="A description or summary of an award given.")


# ----------------------------------------------------------------------------------------------------------------------
# Basics
# ----------------------------------------------------------------------------------------------------------------------
class Profile(BaseModel):
    model_config = ConfigDict(strict=True)

    url: str = Field(..., title="URL", description="A URL associated with a person's profile.")
    username: Optional[str] = Field(title="User Name", description="The user name a person uses on a given network.")
    network: Optional[str] = Field(title="Network",
                                   description="The internet website or community on which a person has a profile.")


class Location(BaseModel):
    model_config = ConfigDict(strict=True)

    city: str = Field(..., title="City", description="A city name.")
    address: Optional[str] = Field(title="Address", description="A street address.")
    region: Optional[str] = Field(title="Region",
                                  description="The state, province or region in component of an address.")
    countrycode: Optional[str] = Field(title="Country Code", description="A two letter code for a country.")
    postalcode: Optional[str] = Field(title="Postal Code", description="A postal code, zip code or similar.")


class Basics(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="A person's full name.")
    label: Optional[str] = Field(title="Label",
                                 description="A job title that summarizes or describes an individual's career.")
    website: Optional[str] = Field(title="Website", description="The URL for a personal website.")
    email: Optional[str] = Field(title="Email", description="An email address.")
    phone: Optional[str] = Field(title="Phone", description="A phone number.")
    summary: Optional[str] = Field(title="Summary", description="A career summary found in a resume..")
    url: Optional[str] = Field(title="URL", description="A URL for any additional website.")
    profiles: Optional[list[Profile]]
    location: Optional[Location]


# ----------------------------------------------------------------------------------------------------------------------
# Certificates
# ----------------------------------------------------------------------------------------------------------------------
class Certificate(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="The name of a certificate or certification.")
    date: Optional[date] = Field(title="Date", description="The date on which a certificate was granted.")
    url: Optional[str] = Field(title="URL", description="A URL associated with a certificate.")
    issuer: Optional[str] = Field(title="Issuer",
                                  description="The individual or organization that issues a given certificate.")


# ----------------------------------------------------------------------------------------------------------------------
# Education
# ----------------------------------------------------------------------------------------------------------------------
class Education(BaseModel):
    model_config = ConfigDict(strict=True)

    institution: str = Field(title="Institution",
                             description="The name of a university, college or other educational institution.")
    area: Optional[str] = Field(title="Area", description="A major area of study within a degree program.")
    studytype: Optional[str]
    startdate: Optional[date] = Field(title="Start date", description="The date on which education studies started.")
    enddate: Optional[date] = Field(title="End date", description="The date on which education studies ended.")
    url: Optional[str] = Field(title="URL", description="A URL for a given educational institution.")
    score: Optional[str] = Field(title="Score",
                                 description="A grade point average, letter grade or other score given by an educational institution.")


# ----------------------------------------------------------------------------------------------------------------------
# Interests
# ----------------------------------------------------------------------------------------------------------------------
class Interest(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="The name of a personal interest.")

    def prerender(self):
        return self.name


# ----------------------------------------------------------------------------------------------------------------------
# Languages
# ----------------------------------------------------------------------------------------------------------------------
class Language(BaseModel):
    model_config = ConfigDict(strict=True)

    language: str = Field(..., title="Language", description="The name of a natural language.")
    fluency: Optional[str] = Field(title="Fluency",
                                   description="A term to signify the level of fluency one has in a language.")

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

    name: str = Field(..., title="Name", description="The name of a project.")
    enddate: Optional[date] = Field(title="End date", description="The date on which a project ended.")
    startdate: Optional[date] = Field(title="Start date", description="The date on which a project started.")
    description: Optional[str] = Field(title="Description",
                                       description="A summary or narrative description of a project.")
    highlights: Optional[list[str]] = Field(title="Highlights",
                                            description="A list of bullet points detailing highlights of a project.")
    url: Optional[str] = Field(title="URL", description="A URL for a given project.")


# ----------------------------------------------------------------------------------------------------------------------
# Publications
# ----------------------------------------------------------------------------------------------------------------------
class Publication(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="The name of an article that was published.")
    publisher: Optional[str] = Field(title="Publisher",
                                     description="The name of an organization or institution that published a given article.")
    summary: Optional[str] = Field(title="Summary", description="A summary of a published article.")
    releasedate: Optional[date] = Field(title="Start date", description="The date on which an article was published.")
    url: Optional[str] = Field(title="URL", description="A URL for a given publication.")


# ----------------------------------------------------------------------------------------------------------------------
# References
# ----------------------------------------------------------------------------------------------------------------------
class Reference(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="The full name a person listed as a reference.")
    reference: Optional[str] = Field(title="Reference", description="A quotation of what a referee said about a person")


# ----------------------------------------------------------------------------------------------------------------------
# Skills
# ----------------------------------------------------------------------------------------------------------------------
class Skill(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str = Field(..., title="Name", description="The name of a skill.")
    level: Optional[str] = Field(title="Level", description="A term to signify a skill level.")
    keywords: Optional[list[str]] = Field(title="Keywords",
                                          description="A list of bullet points to expand on a given skill.")


# ----------------------------------------------------------------------------------------------------------------------
# Volunteer
# ----------------------------------------------------------------------------------------------------------------------
class Volunteer(BaseModel):
    model_config = ConfigDict(strict=True)

    organization: str = Field(..., title="Organization",
                              description="The name of an organization one volunteered with.")
    enddate: Optional[date] = Field(title="End date", description="The date on which a volunteer work ended.")
    startdate: Optional[date] = Field(title="Start date", description="The date on which volunteer work started.")
    position: Optional[str] = Field(title="Position", description="The name or title of a volunteer position.")
    summary: Optional[str] = Field(title="Summary", description="A summary or narrative description of volunteer work.")
    highlights: Optional[list[str]] = Field(title="Highlights",
                                            description="A list of bullet points detailing highlights of volunteer work.")
    url: Optional[str] = Field(title="URL", description="A URL for a given volunteer organization.")


# ----------------------------------------------------------------------------------------------------------------------
# Work
# ----------------------------------------------------------------------------------------------------------------------
class Work(BaseModel):
    model_config = ConfigDict(strict=False)

    position: str = Field(..., title="Position", description="The job title or position one held at an organization.")
    name: str = Field(..., title="Name", description="The name of a company or organization one worked for.")
    location: Optional[str] = Field(title="Location", description="The location of a given company or organization.")
    description: Optional[str] = Field(title="Description",
                                       description="A brief description of a company or organization one worked for.")
    enddate: Optional[date] = Field(title="End date", description="The date on which a work experience ended.")
    startdate: Optional[date] = Field(title="Start date", description="The date on which a work experience started.")
    summary: Optional[str] = Field(title="Summary", description="A summary or narrative description of volunteer work.")
    highlights: Optional[list[str]] = Field(title="Highlights",
                                            description="A list of bullet points detailing highlights of a given work experience.")
    url: Optional[str] = Field(title="URL", description="A URL for a given company.")


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
