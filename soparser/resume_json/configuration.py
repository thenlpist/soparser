import random
from dataclasses import dataclass

import jinja2
from data_model import *

@dataclass
class ConfigVar:
    name: str
    population: list[str]
    weights: list[float]


@dataclass
class Config:
    env: Optional[jinja2.environment.Environment]
    date_fmt: str
    date_delimiter: str
    skill_delimiter: str
    work_delimiter: str
    bullet_prefix: str
    current_str: str
    education_section_name: str
    work_section_name: str
    interests_section_name: str
    references_section_name: str
    languages_section_name: str
    volunteer_section_name: str
    certificates_section_name: str
    awards_section_name: str
    publications_section_name: str
    project_section_name: str
    skills_section_name: str
    resume_template: str
    section_template: str
    basics_template: str
    work_template: str
    education_template: str
    skills_template: str
    projects_template: str
    publications_template: str
    awards_template: str
    certificates_template: str
    volunteer_template: str
    language_template: str
    interests_template: str
    references_template: str

    # def print(self):
    #     d = copy.deepcopy(self.__dict__)
    #     d.pop("env")
    #     print(json.dumps(d, indent=2))

    def to_json(self):
        # json = copy.deepcopy(self.__dict__)
        d = dict()
        for key in self.__dataclass_fields__.keys():
            if key != "env":
                d[key] = self.__getattribute__(key)
        # ajson = dataclasses.asdict(self)
        # ajson.pop("env")
        ajson = d
        return ajson


class ConfigFactory:

    def __init__(self, template_dir):
        templateLoader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.templateEnv = jinja2.Environment(
            loader=templateLoader, trim_blocks=False, lstrip_blocks=False, keep_trailing_newline=True
        )

    def build_random_config(self) -> Config:
        config_var = self.get_config_variables()
        return Config(
            env=self.templateEnv,
            date_fmt=self.get_random_var(config_var["date_fmt"]),
            date_delimiter=self.get_random_var(config_var["date_delimiter"]),
            work_delimiter=self.get_random_var(config_var["work_delimiter"]),
            skill_delimiter=self.get_random_var(config_var["skill_delimiter"]),
            bullet_prefix=self.get_random_var(config_var["bullet_prefix"]),
            current_str=self.get_random_var(config_var["current_str"]),
            education_section_name=self.get_random_var(config_var["education_section_name"]),
            work_section_name=self.get_random_var(config_var["work_section_name"]),
            interests_section_name=self.get_random_var(config_var["interests_section_name"]),
            references_section_name=self.get_random_var(config_var["references_section_name"]),
            languages_section_name=self.get_random_var(config_var["languages_section_name"]),
            volunteer_section_name=self.get_random_var(config_var["volunteer_section_name"]),
            certificates_section_name=self.get_random_var(config_var["certificates_section_name"]),
            awards_section_name=self.get_random_var(config_var["awards_section_name"]),
            publications_section_name=self.get_random_var(config_var["publications_section_name"]),
            project_section_name=self.get_random_var(config_var["project_section_name"]),
            skills_section_name=self.get_random_var(config_var["skills_section_name"]),
            awards_template=self.get_random_var(config_var["awards_template"]),
            basics_template=self.get_random_var(config_var["basics_template"]),
            certificates_template=self.get_random_var(config_var["certificates_template"]),
            education_template=self.get_random_var(config_var["education_template"]),
            interests_template=self.get_random_var(config_var["interests_template"]),
            language_template=self.get_random_var(config_var["language_template"]),
            projects_template=self.get_random_var(config_var["projects_template"]),
            publications_template=self.get_random_var(config_var["publications_template"]),
            references_template=self.get_random_var(config_var["references_template"]),
            resume_template=self.get_random_var(config_var["resume_template"]),
            section_template=self.get_random_var(config_var["section_template"]),
            skills_template=self.get_random_var(config_var["skills_template"]),
            volunteer_template=self.get_random_var(config_var["volunteer_template"]),
            work_template=self.get_random_var(config_var["work_template"]),
        )

    def config_from_dict(self, d):
        return Config(
            env=self.templateEnv,
            date_fmt=d["date_fmt"],
            date_delimiter=d["date_delimiter"],
            work_delimiter=d["work_delimiter"],
            skill_delimiter=d["skill_delimiter"],
            bullet_prefix=d["bullet_prefix"],
            current_str=d["current_str"],
            education_section_name=d["education_section_name"],
            work_section_name=d["work_section_name"],
            interests_section_name=d["interests_section_name"],
            references_section_name=d["references_section_name"],
            languages_section_name=d["languages_section_name"],
            volunteer_section_name=d["volunteer_section_name"],
            certificates_section_name=d["certificates_section_name"],
            awards_section_name=d["awards_section_name"],
            publications_section_name=d["publications_section_name"],
            project_section_name=d["project_section_name"],
            skills_section_name=d["skills_section_name"],
            awards_template=d["awards_template"],
            basics_template=d["basics_template"],
            certificates_template=d["certificates_template"],
            education_template=d["education_template"],
            interests_template=d["interests_template"],
            language_template=d["language_template"],
            projects_template=d["projects_template"],
            publications_template=d["publications_template"],
            references_template=d["references_template"],
            resume_template=d["resume_template"],
            section_template=d["section_template"],
            skills_template=d["skills_template"],
            volunteer_template=d["volunteer_template"],
            work_template=d["work_template"],
        )

    def get_config_variables(self):
        return {
            "date_fmt": ConfigVar(
                name="date_fmt",
                population=["%Y", "%Y-%m", "%b %Y", "%B %Y", "%Y/%m", "%Y.%m", "%Y-%m", "%Y•%m"],
                weights=[0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1],
            ),
            "date_delimiter": ConfigVar(name="date_delimiter", population=["-", "~"], weights=[0.7, 0.3]),
            "work_delimiter": ConfigVar(name="work_delimiter", population=["|", "•", " "], weights=[0.6, 0.1, 0.3]),
            "skill_delimiter": ConfigVar(
                name="skill_delimiter", population=[", ", " • ", " | "], weights=[0.4, 0.2, 0.4]
            ),
            "duration_delimiter": ConfigVar(name="duration_delimiter", population=["-", "~"], weights=[0.7, 0.3]),
            "bullet_prefix": ConfigVar(
                name="bullet_prefix", population=["", "  ", "- ", "• ", "> "], weights=[0.1, 0.3, 0.4, 0.1, 0.1]
            ),
            "current_str": ConfigVar(name="current_str", population=["Present", "Current"], weights=[0.8, 0.2]),
            "education_section_name": ConfigVar(
                name="education_section_name", population=["Education", "Educational Background"], weights=[0.7, 0.3]
            ),
            "work_section_name": ConfigVar(
                name="work_section_name",
                population=[
                    "Work Experience",
                    "Work History",
                    "Professional Experience",
                    "Professional Background",
                    "Career Summary",
                ],
                weights=[0.4, 0.1, 0.3, 0.1, 0.1],
            ),
            "interests_section_name": ConfigVar(
                name="interests_section_name",
                population=["Interests", "Hobbies", "Hobbies and Interests"],
                weights=[0.5, 0.3, 0.2],
            ),
            "references_section_name": ConfigVar(
                name="references_section_name", population=["References", "Referees"], weights=[0.7, 0.3]
            ),
            "languages_section_name": ConfigVar(
                name="languages_section_name",
                population=["Languages", "Language Proficiency", "Foreign Language Skills", "Linguistic Skills"],
                weights=[0.5, 0.2, 0.2, 0.1],
            ),
            "volunteer_section_name": ConfigVar(
                name="volunteer_section_name",
                population=[
                    "Volunteer Experience",
                    "Volunteering",
                    "Community Involvement",
                    "Pro Bono Service",
                    "Unpaid Experience",
                ],
                weights=[0.4, 0.1, 0.2, 0.1, 0.2],
            ),
            "certificates_section_name": ConfigVar(
                name="certificates_section_name",
                population=["Certificates", "Credentials", "Professional Certificates"],
                weights=[0.4, 0.2, 0.4],
            ),
            "awards_section_name": ConfigVar(
                name="awards_section_name",
                population=["Awards", "Recognition", "Honors", "Honours", "Achievements"],
                weights=[0.4, 0.1, 0.2, 0.1, 0.2],
            ),
            "publications_section_name": ConfigVar(
                name="publications_section_name",
                population=["Publications", "Academic Publications", "Articles"],
                weights=[0.5, 0.2, 0.3],
            ),
            "project_section_name": ConfigVar(
                name="project_section_name",
                population=["Projects", "Key Projects", "Portfolio", "Relevant Projects", "Key Initiatives"],
                weights=[0.5, 0.1, 0.2, 0.1, 0.1],
            ),
            "skills_section_name": ConfigVar(
                name="skills_section_name",
                population=["Core Skills", "Skills", "Competencies", "Expertise", "Technical Skills"],
                weights=[0.2, 0.5, 0.1, 0.1, 0.1],
            ),
            "awards_template": ConfigVar(name="awards_template", population=["award.txt"], weights=[1.0]),
            "basics_template": ConfigVar(
                name="basics_template",
                population=["basics_1.txt", "basics_2.txt", "basics_3.txt", "basics_4.txt"],
                weights=[0.25, 0.25, 0.25, 0.25],
            ),
            "certificates_template": ConfigVar(
                name="certificates_template", population=["certificate_1.txt", "certificate_2.txt"], weights=[0.5, 0.5]
            ),
            "education_template": ConfigVar(
                name="education_template", population=["education_2.txt", "education_2.txt"], weights=[0.5, 0.5]
            ),
            "interests_template": ConfigVar(name="interests_template", population=["interests.txt"], weights=[1.0]),
            "language_template": ConfigVar(
                name="language_template",
                population=["language_1.txt", "language_2.txt", "language_3.txt"],
                weights=[0.4, 0.3, 0.3],
            ),
            "projects_template": ConfigVar(
                name="projects_template", population=["project_1.txt", "project_2.txt"], weights=[0.5, 0.5]
            ),
            "publications_template": ConfigVar(
                name="publications_template", population=["publication_1.txt", "publication_2.txt"], weights=[0.5, 0.5]
            ),
            "references_template": ConfigVar(name="references_template", population=["references.txt"], weights=[1.0]),
            "resume_template": ConfigVar(name="resume_template",
                                         population=["resume_1.txt", "resume_2.txt", "resume_3.txt", "resume_4.txt"],
                                         weights=[0.25, 0.25, 0.25, 0.25]),
            "section_template": ConfigVar(name="section_template", population=["section.txt"], weights=[1.0]),
            "skills_template": ConfigVar(name="skills_template", population=["skills_1.txt"], weights=[1.0]),
            "volunteer_template": ConfigVar(
                name="volunteer_template",
                population=["volunteer_1.txt", "volunteer_3.txt", "volunteer_3.txt"],
                weights=[0.4, 0.3, 0.3],
            ),
            "work_template": ConfigVar(
                name="work_template",
                population=["work_1.txt", "work_2.txt", "work_3.txt", "work_4.txt"],
                weights=[0.25, 0.25, 0.25, 0.25],
            ),
        }

    def get_random_var(self, cv: ConfigVar):
        return random.choices(population=cv.population, weights=cv.weights, k=1)[0]


def main():
    factory = ConfigFactory()
    config = factory.build_random_config()
    # print(config)
    config.print()


if __name__ == "__main__":
    # main()
    pass
