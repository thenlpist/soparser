from typing import Optional
import logging
import os
import pickle
import re
import time
from pathlib import Path

from configuration import Config, ConfigFactory
from data_model import *

# create console handler with a higher log level
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
fh = logging.FileHandler(f"{__name__}.log", mode="a")
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)
logger.addHandler(fh)
logger.setLevel(logging.INFO)



class Renderer:

    def __init__(self, template_dir):
        self.factory = ConfigFactory(template_dir)



    def render(self, jresume: dict, resume: Resume, config: Optional[Config]):
        if not config:
            config = self.factory.build_random_config()
        d = dict()
        d["template_config"] = config.to_json()
        date_fmt = config.date_fmt
        d["date_fmt"] = date_fmt
        content = render_resume(resume, config)
        d["text"] = content
        jresume = self._post_process_dates(jresume, date_fmt)
        return d

    def render_resume(self, resume: Resume, config: Config):
        template = config.env.get_template(config.resume_template)

        basics = self._render_basics(resume.basics, config)
        work = self._render_work(resume.work, config)
        education = self._render_education(resume.education, config)
        skills = self._render_skills(resume.skills, config)
        projects = self._render_projects(resume.projects, config)
        publications = self._render_publications(resume.publications, config)
        awards = self._render_awards(resume.awards, config)
        certificates = self._render_certificates(resume.certificates, config)
        volunteer = self._render_volunteer(resume.volunteer, config)
        languages = self._render_languages(resume.languages, config)
        interests = self._render_interests(resume.interests, config)
        references = self._render_references(resume.references, config)

        content = template.render(
            basics=basics,
            work=work,
            education=education,
            skills=skills,
            projects=projects,
            publications=publications,
            awards=awards,
            certificates=certificates,
            volunteer=volunteer,
            languages=languages,
            interests=interests,
            references=references,
        )
        return content


    def _post_process_dates(self, jresume,  date_fmt):
        """ Purpose: Analyse date format used by render. If it is year-only then modify the `resume_json` object
            to match. Otherwise, the training data will be wrong/messy.
        """
        if date_fmt == "%Y":
            # logger.info("Detected YYYY date format...")
            jresume = _reformat_dates(jresume)
        return jresume


    def _reformat_dates(self, obj):
        """Recursive function to reformat date strings """
        date_keys = ["startdate", "enddate", "date", "releasedate"]
        if isinstance(obj, list):
            return [self._reformat_dates(v) for v in obj]
        elif isinstance(obj, dict):
            for k in date_keys:
                if k in obj:
                    date_string = obj[k]
                    if not date_string == "":
                        result = re.search(r"\b([0-9]{4})\b", obj[k])
                        obj[k] = result.group(0) if result else ""
            return {k.lower(): self._reformat_dates(v) for k, v in obj.items()}
        else:
            return obj




    # ----------------------------------------------------------------------------------------------------------------------
    # Basics
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_basics(self, basics: Basics, config: Config):
        template = config.env.get_template(config.basics_template)
        content = template.render(
            name=basics.name,
            label=basics.label,
            phone=basics.phone,
            email=basics.email,
            url=basics.url,
            location=basics.location,
            summary=basics.summary,
            delimiter=config.skill_delimiter,
        )

        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Work Experience
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_work(self, works: list[Work], config: Config):
        if not works:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.work_template)

        items = []
        for work in works:
            date_str = _compute_datestr(work, config)
            item = template.render(
                position=work.position.strip(),
                name=work.name.strip(),
                date_str=date_str,
                work_delimiter=config.work_delimiter,
                location=work.location,
                summary=work.summary,
                highlights=work.highlights,
            )
            items.append(item)
        content = section_template.render(section_name="Work Experience", items=items)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Education
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_education(self, education_exp: list[Education], config: Config):
        template = config.env.get_template(config.education_template)
        section_template = config.env.get_template(config.section_template)

        # items = [render_education_item(exp, config) for exp in education_exp]
        items = []
        for education in education_exp:
            date_str = _compute_datestr(education, config)
            studytype = "" if not education.studytype else education.studytype
            area = "" if not education.area else education.area
            item = template.render(
                institution=education.institution, studytype=studytype, area=area, date_str=date_str
            )
            items.append(item)
        if items:
            content = section_template.render(section_name="Education", items=items)
        else:
            content = ""
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Skills
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_skills(self, skills: list[Skill], config: Config):
        if not skills:
            return ""
        template = config.env.get_template(config.skills_template)
        content = template.render(section_name="Core Skills", skills=skills, delimiter=config.skill_delimiter)
        content = re.sub(f"{config.skill_delimiter}$", "", content)
        if config.skill_delimiter == " | ":
            content = re.sub("\|", " | ", content)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Projects
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_projects(self, projects: list[Project], config: Config):
        if not projects:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.projects_template)

        items = []
        for project in projects:
            date_str = _compute_datestr(project, config)
            item = template.render(
                name=project.name,
                date_str=date_str,
                description=project.description,
                highlights=project.highlights,
                url=project.url,
            )
            items.append(item)

        content = section_template.render(section_name="Projects", items=items)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Publications
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_publications(self, publications: list[Publication], config: Config):
        if not publications:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.publications_template)

        items = []
        for publication in publications:
            date_str = _compute_single_datestr(publication.releasedate, config.date_fmt)
            item = template.render(
                name=publication.name,
                date_str=date_str,
                publisher=publication.publisher,
                url=publication.url,
            )
            items.append(item)

        content = section_template.render(section_name="Publications", items=items)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Awards
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_awards(self, awards: list[Award], config: Config):
        if not awards:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.awards_template)
        items = []
        for award in awards:
            date_str = _compute_single_datestr(award.date, config.date_fmt)
            item = template.render(
                title=award.title,
                bullet_prefix=config.bullet_prefix,
                date_str=date_str,
                awarder=award.awarder,
                summary=award.summary,
            )
            items.append(item)
        content = section_template.render(section_name="Awards", items=items)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Certificates
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_certificates(self, certificates: list[Certificate], config: Config):
        if not certificates:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.certificates_template)
        items = []
        for certificate in certificates:
            date_str = _compute_single_datestr(certificate.date, config.date_fmt)
            item = template.render(
                name=certificate.name,
                date_str=date_str,
                issuer=certificate.issuer,
                url=certificate.url,
            )
            items.append(item)

        content = section_template.render(section_name="Certificates", items=items)
        content = re.sub("\n\n+", "\n\n", content)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Volunteer
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_volunteer(self, volunteers: list[Volunteer], config: Config):
        if not volunteers:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.volunteer_template)
        items = []
        for volunteer in volunteers:
            date_str = _compute_datestr(volunteer, config)
            item = template.render(
                position=volunteer.position,
                organization=volunteer.organization,
                date_str=date_str,
                url=volunteer.url,
                summary=volunteer.summary,
                highlights=volunteer.highlights,
            )
            items.append(item)

        content = section_template.render(section_name="Volunteer Experience", items=items)
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Languages
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_languages(self, languages: list[Language], config: Config):
        if not languages:
            return ""
        section_template = config.env.get_template(config.section_template)
        template = config.env.get_template(config.language_template)
        content = template.render(section_name="Languages", languages=languages, delimiter=config.skill_delimiter)
        # content = re.sub(f"{config.skill_delimiter}$", "", content)
        content = content.strip().strip(config.skill_delimiter.strip()) + "\n"
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # Interests
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_interests(self, interests: list[Interest], config: Config):
        if not interests:
            return ""
        template = config.env.get_template(config.interests_template)
        content = template.render(section_name="Interests", interests=interests, delimiter=config.skill_delimiter)
        content = content.strip().strip(config.skill_delimiter.strip())
        return content


    # ----------------------------------------------------------------------------------------------------------------------
    # References
    # ----------------------------------------------------------------------------------------------------------------------
    def _render_references(self, references: list[Reference], config: Config):
        if not references:
            return ""
        template = config.env.get_template(config.references_template)
        content = template.render(section_name="References", references=references)
        return content





    # ----------------------------------------------------------------------------------------------------------------------
    # Utils
    # ----------------------------------------------------------------------------------------------------------------------
    def _compute_single_datestr(self, dt, date_fmt):
        if not dt:
            return ""
        return dt.strftime(date_fmt)


    def _compute_datestr(self, obj, config: Config):
        current_strs = ["present", "current"]
        date_fmt = config.date_fmt
        start: datetime.date = obj.startdate
        end: datetime.date = obj.enddate
        if not start and not end:
            return ""
        if not start:
            return end.strftime(date_fmt)
        endstr = config.current_str if not end else end.strftime(date_fmt)
        return f"{start.strftime(date_fmt)} {config.date_delimiter} {endstr}"




# #####################################################################################################################

def main_inspect(path):
    data = load_pkl(path)
    count_section_coverage(data, factor=1000)


def main_render(in_path, template_dir, out_path):
    logger.info("-" * 80)
    logger.info(f"Template Directory: {template_dir}")
    min_length_threshold = 1000
    data = load_pkl(in_path)

    execute(data, template_dir, min_length_threshold, out_path)


def execute(data, template_dir, min_length_threshold, out_path):
    t1 = time.time()
    data_cnt = len(data)
    logger.info(f"Number of records in input data {data_cnt}")
    factory = ConfigFactory(template_dir)
    data2 = []
    num_culled = 0
    for i, d in enumerate(data):
        d = process(d, factory)
        if len(d["text"]) > min_length_threshold:
            resume = d["resume"]
            data2.append(d)
            if resume.publications or resume.publications:
                data2.extend(duplicate(d, factory, 4))
            if resume.interests or resume.projects or resume.volunteer or resume.awards:
                data2.extend(duplicate(d, factory, 2))
            if resume.certificates or resume.languages:
                data2.extend(duplicate(d, factory, 1))
        else:
            num_culled += 1

    data2 = [post_process(d) for d in data2]
    outdata_cnt = len(data2)
    t2 = time.time()
    duration = t2 - t1
    logger.info(f"Running time: {duration:.2f} sec -> {(data_cnt / duration):.2f} records/sec")
    logger.info(f"{num_culled} records ignored for being too short")
    count_section_coverage(data2, factor=1000)
    logger.info(f"Persisting {outdata_cnt} to {out_path}")
    with open(out_path, "wb") as fo:
        pickle.dump(data2, fo)


def duplicate(d0, factory, times):
    result = []
    for i in range(times):
        d = copy.deepcopy(d0)
        result.append(process(d, factory))
    return result


def process(d, factory):
    resume = d["resume"]
    config = factory.build_random_config()
    d["template_config"] = config.to_json()
    d["date_fmt"] = config.date_fmt
    content = render_resume(resume, config)
    d["text"] = content
    return d


def post_process(d):
    """ Purpose: Analyse date format used by render. If it is year-only then modify the `resume_json` object
        to match. Otherwise the training data will be wrong/messy.
    """
    date_fmt = d["date_fmt"]
    if date_fmt == "%Y":
        # logger.info("Detected YYYY date format...")
        jsonresume = d["resume_json"]
        d["resume_json"] = _reformat_dates(jsonresume)
    return d


def _reformat_dates(obj):
    """Recursive function to reformat date strings """
    date_keys = ["startdate", "enddate", "date", "releasedate"]
    if isinstance(obj, list):
        return [_reformat_dates(v) for v in obj]
    elif isinstance(obj, dict):
        for k in date_keys:
            if k in obj:
                date_string = obj[k]
                if not date_string == "":
                    result = re.search(r"\b([0-9]{4})\b", obj[k])
                    obj[k] = result.group(0) if result else ""
        return {k.lower(): _reformat_dates(v) for k, v in obj.items()}
    else:
        return obj


def run(d, config):
    logger.info("-" * 80)
    resume = d["resume"]
    content = render_resume(resume, config)
    logger.info(content)


def analyze_lengths(data, config):
    content_lens = []
    for d in data:
        resume = d["resume"]
        content = render_resume(resume, config)
        content_lens.append(int(len(content) / 100))
    c = Counter(content_lens)
    for k, v in sorted(c.items(), key=operator.itemgetter(0)):
        bars = "|" * int(v / 100)
        length = k * 100
        logger.info(f"{length:<10} {v}\t{bars}")


def count_section_coverage(data, factor=10):
    data_cnt = len(data)
    cnts = {
        "awards": 0,
        "basics": 0,
        "certificates": 0,
        "education": 0,
        "interests": 0,
        "languages": 0,
        "projects": 0,
        "publications": 0,
        "references": 0,
        "skills": 0,
        "volunteer": 0,
        "work": 0,
    }
    for d in data:
        resume = d["resume"]
        for cnt in cnts:
            v = resume.__getattribute__(cnt)
            if v != [] and v != None:
                cnts[cnt] += 1

    logger.info("Section\t\tCount  % \tBars")
    for k, v in sorted(cnts.items(), key=operator.itemgetter(1), reverse=True):
        bars = "|" * int(v / factor)
        logger.info(f"{k:<15} {v:<5} {(v / data_cnt):.4f}   {bars}")


def render_resume(resume: Resume, config: Config):
    template = config.env.get_template(config.resume_template)

    basics = render_basics(resume.basics, config)
    work = render_work(resume.work, config)
    education = render_education(resume.education, config)
    skills = render_skills(resume.skills, config)
    projects = render_projects(resume.projects, config)
    publications = render_publications(resume.publications, config)
    awards = render_awards(resume.awards, config)
    certificates = render_certificates(resume.certificates, config)
    volunteer = render_volunteer(resume.volunteer, config)
    languages = render_languages(resume.languages, config)
    interests = render_interests(resume.interests, config)
    references = render_references(resume.references, config)

    content = template.render(
        basics=basics,
        work=work,
        education=education,
        skills=skills,
        projects=projects,
        publications=publications,
        awards=awards,
        certificates=certificates,
        volunteer=volunteer,
        languages=languages,
        interests=interests,
        references=references,
    )
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Basics
# ----------------------------------------------------------------------------------------------------------------------
def render_basics(basics: Basics, config: Config):
    template = config.env.get_template(config.basics_template)
    content = template.render(
        name=basics.name,
        label=basics.label,
        phone=basics.phone,
        email=basics.email,
        url=basics.url,
        location=basics.location,
        summary=basics.summary,
        delimiter=config.skill_delimiter,
    )

    return content


# ----------------------------------------------------------------------------------------------------------------------
# Work Experience
# ----------------------------------------------------------------------------------------------------------------------
def render_work(works: list[Work], config: Config):
    if not works:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.work_template)

    items = []
    for work in works:
        date_str = _compute_datestr(work, config)
        item = template.render(
            position=work.position.strip(),
            name=work.name.strip(),
            date_str=date_str,
            work_delimiter=config.work_delimiter,
            location=work.location,
            summary=work.summary,
            highlights=work.highlights,
        )
        items.append(item)
    content = section_template.render(section_name="Work Experience", items=items)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Education
# ----------------------------------------------------------------------------------------------------------------------
def render_education(education_exp: list[Education], config: Config):
    template = config.env.get_template(config.education_template)
    section_template = config.env.get_template(config.section_template)

    # items = [render_education_item(exp, config) for exp in education_exp]
    items = []
    for education in education_exp:
        date_str = _compute_datestr(education, config)
        studytype = "" if not education.studytype else education.studytype
        area = "" if not education.area else education.area
        item = template.render(
            institution=education.institution, studytype=studytype, area=area, date_str=date_str
        )
        items.append(item)
    if items:
        content = section_template.render(section_name="Education", items=items)
    else:
        content = ""
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Skills
# ----------------------------------------------------------------------------------------------------------------------
def render_skills(skills: list[Skill], config: Config):
    if not skills:
        return ""
    template = config.env.get_template(config.skills_template)
    content = template.render(section_name="Core Skills", skills=skills, delimiter=config.skill_delimiter)
    content = re.sub(f"{config.skill_delimiter}$", "", content)
    if config.skill_delimiter == " | ":
        content = re.sub("\|", " | ", content)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Projects
# ----------------------------------------------------------------------------------------------------------------------
def render_projects(projects: list[Project], config: Config):
    if not projects:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.projects_template)

    items = []
    for project in projects:
        date_str = _compute_datestr(project, config)
        item = template.render(
            name=project.name,
            date_str=date_str,
            description=project.description,
            highlights=project.highlights,
            url=project.url,
        )
        items.append(item)

    content = section_template.render(section_name="Projects", items=items)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Publications
# ----------------------------------------------------------------------------------------------------------------------
def render_publications(publications: list[Publication], config: Config):
    if not publications:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.publications_template)

    items = []
    for publication in publications:
        date_str = _compute_single_datestr(publication.releasedate, config.date_fmt)
        item = template.render(
            name=publication.name,
            date_str=date_str,
            publisher=publication.publisher,
            url=publication.url,
        )
        items.append(item)

    content = section_template.render(section_name="Publications", items=items)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Awards
# ----------------------------------------------------------------------------------------------------------------------
def render_awards(awards: list[Award], config: Config):
    if not awards:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.awards_template)
    items = []
    for award in awards:
        date_str = _compute_single_datestr(award.date, config.date_fmt)
        item = template.render(
            title=award.title,
            bullet_prefix=config.bullet_prefix,
            date_str=date_str,
            awarder=award.awarder,
            summary=award.summary,
        )
        items.append(item)
    content = section_template.render(section_name="Awards", items=items)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Certificates
# ----------------------------------------------------------------------------------------------------------------------
def render_certificates(certificates: list[Certificate], config: Config):
    if not certificates:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.certificates_template)
    items = []
    for certificate in certificates:
        date_str = _compute_single_datestr(certificate.date, config.date_fmt)
        item = template.render(
            name=certificate.name,
            date_str=date_str,
            issuer=certificate.issuer,
            url=certificate.url,
        )
        items.append(item)

    content = section_template.render(section_name="Certificates", items=items)
    content = re.sub("\n\n+", "\n\n", content)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Volunteer
# ----------------------------------------------------------------------------------------------------------------------
def render_volunteer(volunteers: list[Volunteer], config: Config):
    if not volunteers:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.volunteer_template)
    items = []
    for volunteer in volunteers:
        date_str = _compute_datestr(volunteer, config)
        item = template.render(
            position=volunteer.position,
            organization=volunteer.organization,
            date_str=date_str,
            url=volunteer.url,
            summary=volunteer.summary,
            highlights=volunteer.highlights,
        )
        items.append(item)

    content = section_template.render(section_name="Volunteer Experience", items=items)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Languages
# ----------------------------------------------------------------------------------------------------------------------
def render_languages(languages: list[Language], config: Config):
    if not languages:
        return ""
    section_template = config.env.get_template(config.section_template)
    template = config.env.get_template(config.language_template)
    content = template.render(section_name="Languages", languages=languages, delimiter=config.skill_delimiter)
    # content = re.sub(f"{config.skill_delimiter}$", "", content)
    content = content.strip().strip(config.skill_delimiter.strip()) + "\n"
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Interests
# ----------------------------------------------------------------------------------------------------------------------
def render_interests(interests: list[Interest], config: Config):
    if not interests:
        return ""
    template = config.env.get_template(config.interests_template)
    content = template.render(section_name="Interests", interests=interests, delimiter=config.skill_delimiter)
    content = content.strip().strip(config.skill_delimiter.strip())
    return content


# ----------------------------------------------------------------------------------------------------------------------
# References
# ----------------------------------------------------------------------------------------------------------------------
def render_references(references: list[Reference], config: Config):
    if not references:
        return ""
    template = config.env.get_template(config.references_template)
    content = template.render(section_name="References", references=references)
    return content


# ----------------------------------------------------------------------------------------------------------------------
# Utils
# ----------------------------------------------------------------------------------------------------------------------
def _compute_single_datestr(dt, date_fmt):
    if not dt:
        return ""
    return dt.strftime(date_fmt)


def _compute_datestr(obj, config: Config):
    current_strs = ["present", "current"]
    date_fmt = config.date_fmt
    start: datetime.date = obj.startdate
    end: datetime.date = obj.enddate
    if not start and not end:
        return ""
    if not start:
        return end.strftime(date_fmt)
    endstr = config.current_str if not end else end.strftime(date_fmt)
    return f"{start.strftime(date_fmt)} {config.date_delimiter} {endstr}"

#
# def get_bullet_pattern():
#     return re.compile(
#         "^[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
#         re.UNICODE,
#     )
#
#
# def bullet_to_hyphen(text):
#     bullets = re.compile(
#         "\n[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
#         re.UNICODE,
#     )
#     return bullets.sub("\n-", text)
#
#
# def bullet_to_char(text, replacement):
#     bullets = re.compile(
#         "^[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
#         re.UNICODE,
#     )
#     return bullets.sub(replacement, text).strip()
#

# ----------------------------------------------------------------------------------------------------------------------
# I/O
# ----------------------------------------------------------------------------------------------------------------------
def load_pkl(path):
    return pickle.load(open(path, "rb"))


# ----------------------------------------------------------------------------------------------------------------------
# Dev helper methods
# ----------------------------------------------------------------------------------------------------------------------
def extract_sample_dev_data(in_data_path, sample_data_path):
    """Extract a smallish sample of data that contains all sections in at least some records
    n.b. This is for dev purposes only. Comment out / delete later
    """
    logger.info("Creating sample dev data...")
    data = load_pkl(in_data_path)

    def filter_for_section(data, name):
        return [d for d in data if d["resume"].__getattribute__(name) != []]

    sample = []
    for k in [
        "skills",
        "publications",
        "education",
        "references",
        "basics",
        "awards",
        "certificates",
        "volunteer",
        "languages",
        "interests",
        "work",
        "projects",
    ]:
        filtered = filter_for_section(data, k)
        sample_size = min(len(filtered), 10)
        logger.info(f"Sampling {sample_size} from {k} ...")
        sample.extend(random.sample(filtered, sample_size))

    logger.info(f"Saving sample data to {sample_data_path}...")

    with open(sample_data_path, "wb") as fo:
        pickle.dump(sample, fo)

    logger.info("done")


# ----------------------------------------------------------------------------------------------------------------------
# Inspection & logger.infoer Dev functions
# ----------------------------------------------------------------------------------------------------------------------
def inspect_work_dates(data, config):
    """logger.info out company name and dates using given specs. Example:
    inspect_work_dates(data, "%Y/%m", "~", "Current")
    """
    for d in data:
        resume = d["resume"]
        logger.info(f"{resume.basics.name}")
        for work in resume.work:
            s = _compute_datestr(work, config)
            logger.info(f"\t{work.name:<40}  {s}")
        logger.info()


if __name__ == "__main__":
    home = Path.home()

    in_data_path = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/structured_data.pkl")
    sample_data_path = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/structured_data_SAMPLE.pkl")
    out_dir = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/pre-train")
    os.makedirs(out_dir, exist_ok=True)
    template_dir = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/templates")
    out_path = out_dir.joinpath(in_data_path.name)

    # extract_sample_dev_data(in_data_path, sample_data_path)

    # main_render(sample_data_path, template_dir, out_path)
    main_render(in_data_path, template_dir, out_path)
