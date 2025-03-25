from dateutil.parser import ParserError
from dateutil.parser import parse

from data_model import *
from renderer import *

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


def main_deserialize(inpath, outpath):
    filter_for_en = False
    logger.info("loading data...")
    data = [json.loads(x) for x in open(inpath)]
    logger.info(f"Loaded {len(data)} records")
    data = copy.deepcopy(data)
    logger.info("dedupping data...")
    data = dedup_data(data)
    logger.info("preprocessing data...")
    data = [prepare(d, filter_for_en=filter_for_en) for d in data]
    data = [d for d in data if d]
    logger.info("running execute...")
    data = execute(data)
    logger.info("filtering out data with None resume objects...")
    data = [d for d in data if d["resume"]]
    logger.info("post processing...")
    # logger.info(f"type(data): {type(data)},   type(data[0]): {type(data[0])}")
    data = [post_process(d, i) for i, d in enumerate(data)]
    logger.info(f"Post-processed data count: {len(data)}")
    data = [d for d in data if d]
    logger.info(f"Filtered data count: {len(data)}")
    rser = ResumeSerializer()
    data = [serialize_anew(rser, d) for d in data]
    logger.info(f"Persisting {len(data)} records of data to {outpath}")
    with open(outpath, "wb") as fo:
        pickle.dump(data, fo)
    logger.info("Done")


def serialize_anew(rser, d):
    resume = d["resume"]
    d["resume_json"] = rser.to_json_resume(resume)
    return d


def prepare(d, filter_for_en=False):
    if not "data" in d or is_empty(d["data"]):
        return None

    language = _get_language(d)
    if filter_for_en:
        if not language or language != "en":
            return None

    d["original_data"] = copy.deepcopy(d["data"])
    tmp = d["data"]
    if not tmp:
        return None
    tmp = clean_schema(flatten(tmp))
    d["data"] = deserialize_dates(tmp)
    return d


def _get_language(d):
    if "language" in d:
        return d["language"]
    pod = d["parser_original_data"]
    if pod and "language" in pod:
        return pod["language"]
    return None


def is_empty(d):
    if not d:
        return None
    work = d.get("work", None)
    education = d.get("education", None)
    projects = d.get("projects", None)

    if not work and not education and not projects:
        return True
    return False


def execute(data):
    data_cnt = len(data)
    cnts = Counter(
        {
            "publications": 0,
            "education": 0,
            "work": 0,
            "skills": 0,
            "references": 0,
            "awards": 0,
            "certificates": 0,
            "volunteer": 0,
            "languages": 0,
            "interests": 0,
            "projects": 0,
        }
    )
    result = [enrich_w_resume_obj(i, d) for i, d in enumerate(data)]
    data2 = []
    for d, e in result:
        data2.append(d)
        cnts.update(Counter(e))

    logger.info(f"original data count: {data_cnt}, processed data count: {len(data2)}")
    logger.info(f"Error Counts:\n{json.dumps(cnts, indent=2)}")
    return data2


def enrich_w_resume_obj(i, d: dict):
    resume, errs = deserialize_structured_resume(d["data"], i)
    d["resume"] = resume
    return d, errs


def to_title_case(s):
    if not s:
        return None
    return s.title()


def post_process(d, i=None):
    """post process including: normalize name, normalize bullets, remove bullets from list of highlights"""
    logger.debug(f"Post processing index: {i}")
    resume = d["resume"]
    resume.basics = post_process_basics(resume.basics)
    resume.skills = post_process_skills(resume.skills)
    resume.projects = post_process_highlights(resume.projects)
    resume.work = post_process_highlights(resume.work)
    resume.education = post_process_education(resume.education)
    resume.interests = post_process_interests(resume.interests)

    if not resume.basics:
        return None
    d["resume"] = resume

    for section in d.keys():
        if section == []:
            d[section] = None

    if not assess_validity(resume):
        return None
    return d


def post_process_basics(basics: Basics):
    if not basics.name:
        return None
    basics.name = to_title_case(basics.name)
    basics.label = to_title_case(basics.label)
    if basics.summary:
        basics.summary = clean_up_stray_bullets(basics.summary)
    if basics.email and not valid_email(basics.email):
        basics.email = None
    if basics.phone:
        basics.phone = phone_format(basics.phone)
    basics.profiles = post_process_profiles(basics.profiles)
    return basics


def post_process_highlights(obj_list, highlight_newline_strategy: str = "bullet"):
    def process(obj, highlight_newline_strategy: str = "bullet"):
        highlights = obj.highlights
        highlights = [bullet_to_char(x.strip(), "") for x in highlights]
        highlights = [x for x in highlights if x]
        if not highlights:
            return obj
        match highlight_newline_strategy:
            case "space":
                obj.highlights = [x.replace("\n", " ") for x in highlights]
            case "bullet":
                highlights = [x.split("\n") for x in highlights]
                obj.highlights = [x for item in highlights for x in item if x]
            case _:
                pass
        return obj

    for obj in obj_list:
        try:
            process(obj, highlight_newline_strategy)
        except:
            logger.info("ERROR")
            logger.info(obj)
            logger.info("highlights:")
            logger.info(obj.highlights)
    return [process(obj, highlight_newline_strategy) for obj in obj_list]


def post_process_work(works: list[Work]):
    # return [x for x in works if x.institution != "" and x.institution != None]
    def validate(work: Work):
        if not work.position or work.position == "":
            return False

    return [x for x in works if validate(x)]


def post_process_education(education: list[Education]):
    return [x for x in education if x.institution != "" and x.institution != None]


def post_process_interests(interests: list[Interest]):
    for interest in interests:
        interest.name = bullet_to_char(interest.name, "")
    return interests


def assess_validity(resume):
    """ see if resume has at minumum some basics info, work/projects/volunteer and education """
    has_work = not (resume.work == None or resume.work == [])
    has_projects = not (resume.projects == None or resume.projects == [])
    has_volunteer = not (resume.volunteer == None or resume.volunteer == [])
    return any([has_work, has_projects, has_volunteer])


def valid_email(email):
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return True
    return False


def phone_format(s):
    digits = []
    for char in s:
        if char.isdigit():
            digits.append(char)
    # n = re.sub("[\+\.\(\)-•]", "", s)
    n = "".join(digits)
    if n == "" or len(n) < 5:
        logger.info(f"unparseable phone number: {s}")
        return None
    # if len(n) == 9:
    #     return format(int(n), ",").replace(",", "-")
    # if len(n) == 7 or len(n) == 10 or len(n) = 11:
    return format(int(n[:-1]), ",").replace(",", "-") + n[-1]


def post_process_profiles(profiles):
    if not profiles:
        return None

    def cleanup(p: Profile):
        if (p.url == "" or p.url == None) and (p.username == "" or p.username == None):
            return None

    return [cleanup(p) for p in profiles]


def post_process_skills(skills):
    skills = [x for x in skills if x.name != ""]

    delimiter_pattern = re.compile(r" [-\|] ")
    newskills = []

    for skill in skills:
        name = bullet_to_char(skill.name, "")
        skill.name = name
        if delimiter_pattern.search(name):
            terms = delimiter_pattern.sub("\n", name).split("\n")
            terms = [clean_up_stray_bullets(t) for t in terms]
            newskills.extend(
                [Skill(name=t, level=skill.level, keywords=skill.keywords) for t in terms]
            )
        else:
            newskills.append(skill)

    return newskills


def deserialize_structured_resume(d, idx):
    logger.debug(idx)
    section_to_model = {
        "education": Education,
        "work": Work,
        "skills": Skill,
        "publications": Publication,
        "references": Reference,
        "awards": Award,
        "certificates": Certificate,
        "volunteer": Volunteer,
        "languages": Language,
        "interests": Interest,
        "projects": Project,
    }

    dd = defaultdict(list)
    for name, model in section_to_model.items():
        v = deserialize_list_sections(d, name, model, idx)
        # logger.info(f"{name}\t{len(v)}")
        dd[name] = v

    sections = {k: v[0] for k, v in dd.items()}
    err_cnt = {k: v[1] for k, v in dd.items()}

    basics = deserialize_basics_section(d)
    if not basics:
        return None, err_cnt

    basics_section = {"basics": basics}
    obj = basics_section | sections
    return Resume.model_validate(obj), err_cnt


def deserialize_list_sections(d, name, model: BaseModel, idx: Optional[int] = None):
    # logger.info(idx)
    items = d[name]
    objs = []
    err_cnt = 0
    for i, item in enumerate(items):
        try:
            objs.append(model.model_validate(item))
        except ValidationError as e:
            logger.info(f"{idx}\tValidationError for {name} item #{i} ")
            err_cnt += 1
    return (objs, err_cnt)


def deserialize_basics_section(d):
    basics = copy.deepcopy(d["basics"])
    if not basics:
        return None
    profiles = [x for x in basics["profiles"] if x]

    profiles2 = []
    for prof in profiles:
        try:
            obj = Profile.model_validate(prof)
            profiles2.append(obj)
        except:
            pass
    basics["profiles"] = profiles2 if profiles2 else None

    try:
        city = basics["location"]["city"]
        city = city if city else None
        basics["location"]["city"] = city
        location = Location.model_validate(basics["location"])
    except:
        location = None

    basics["location"] = location
    try:
        obj = Basics.model_validate(basics)
    except:
        obj = None
    # return Basics.model_validate(basics)
    return obj


# ----------------------------------------------------------------------------------------------------------------------
# Date manipulation
# ----------------------------------------------------------------------------------------------------------------------
def deserialize_dates(d: dict):
    if not d:
        return None

    def _deserialize(d2: dict):
        if not d2:
            return None
        date_keys = ["startdate", "enddate", "date", "releasedate"]
        for k in date_keys:
            if k in d2:
                d2[k] = _parse_date(d2, k)
        return d2

    section_names = ["awards", "certificates", "education", "projects", "publications", "volunteer", "work"]
    for name in section_names:
        sections = [_deserialize(item) for item in d[name]]
        sections = [x for x in sections if x]
        d[name] = sections
    return d


def _parse_date(d, name):
    date_string = d[name]
    if isinstance(date_string, datetime.date):
        return date_string
    if not date_string:
        return None
    try:
        dt = parse(date_string).date()
        # manually set the day of the month to the first since datetime tends to infer 15th by default and results often don't use day anyway
        return dt.replace(day=1)
    except ParserError:
        return None
    except OverflowError:
        return None


# ----------------------------------------------------------------------------------------------------------------------
# Data Prep
# ----------------------------------------------------------------------------------------------------------------------
def flatten(obj):
    """Recursive function to remove outer 'value' from dicts"""
    if isinstance(obj, list):
        return [flatten(v) for v in obj]
    elif isinstance(obj, dict):
        if list(obj.keys()) == ["value"]:
            return flatten(obj["value"])
        return {k.lower(): flatten(v) for k, v in obj.items()}
    else:
        return obj


def clean_schema(d):
    keys_to_filter = ["meta", "fileinfo", "formatting", "sectionheadings", "additional"]
    for k in keys_to_filter:
        d.pop(k, None)
    return d


def dedup_data(data):
    # Deduplicate
    data.sort(key=operator.itemgetter("updated_ts"), reverse=True)
    logger.info(f"len(data): {len(data)}")
    user_ids = set([])
    data2 = []
    for d in data:
        uid = d["user_id"]
        if uid not in user_ids:
            data2.append(d)
        user_ids.add(uid)

    logger.info(f"original number of records {len(data)}")
    logger.info(f"dedupped number of records {len(data2)}")
    return data2


def clean_up_stray_bullets(text):
    # unicode and plain text used as bullets
    bullets = re.compile(
        "[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
        re.UNICODE,
    )
    # unicode codes from above as plain text (which sometimes happens)
    non_unicode = re.compile(
        "(u2022 t|u002D|u058A|u05BE|u1400|u1806|u2010|u2011|u2012|u2013|u2014|u2015|u2022|u2023|u2043|u204C|u204D|u2219|u25CB|u25CF|u25D8|u25E6|u261A|u261B|u261C|u261E|u2E17|u2E1A|u301C|u3030|u30A0|uFE31|uFE32|uFE58|uFE63|uFF0D)"
    )
    t = bullets.sub("", text)
    t = non_unicode.sub("", t)
    return t.strip()


def bullet_to_char(text, replacement):
    bullets = re.compile(
        "^[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
        re.UNICODE,
    )
    return bullets.sub(replacement, text).strip()


# ----------------------------------------------------------------------------------------------------------------------
# Dev helper methods
# ----------------------------------------------------------------------------------------------------------------------
def printer(d):
    logger.info(f"id:	        {d['id']}")
    logger.info(f"user_id:	{d['user_id']}")
    logger.info(f"updated_ts:	{d['updated_ts']}")
    logger.info(f"name:	    {d['name']}")
    logger.info(f"file_type:	{d['file_type']}")
    logger.info(f"doc_path:	{d['document_path']}")
    logger.info(f"txt_path:	{d['txt_path']}")
    logger.info(f"txt_success:	{d['txt_success']}")
    logger.info(f"doc_extraction:	{d['doc_extraction']}")
    logger.info(f"num_chars:	{d['num_chars']}")
    logger.info(f"language:	{d['language']}")


def filter_for_section(data, name):
    return [d for d in data if d["data"][name] != []]


def create_sample_dev_data(path, sample_data_path):
    """Extract a smallish sample of data that contains all sections in at least some records
    n.b. This is for dev purposes only. Comment out / delete later
    """
    logger.info("Creating sample dev data...")
    data = [json.loads(x) for x in open(path)]
    data2 = dedup_data(data)

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
        filtered = filter_for_section(data2, k)
        sample_size = min(len(filtered), 100)
        logger.info(f"Sampling {sample_size} from {k} ...")
        sample.extend(random.sample(filtered, sample_size))

    logger.info(f"Saving sample data to {sample_data_path}...")
    with open(sample_data_path, "w") as fo:
        fo.write("\n".join([json.dumps(x) for x in sample]))
    logger.info("done")
    # raw = copy.deepcopy(sample)
    # run(sample)


if __name__ == "__main__":
    home = Path.home()
    inpath = home.joinpath(
        "Data/Jobscan/Resumes/0_Raw/InternalParser/BigQuery/jobscan_20241201-20250127/2024-12/7.20241201-20250127.jsonl"
    )
    sample_data_path = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/sample_resume_data.jsonl")

    outpath = home.joinpath("Work/ResumeParser_RnD/Projects/ResumeParser_v2/data/structured_data.pkl")

    # create_sample_dev_data(path, sample_data_path)
    # main(sample_data_path)
    main_deserialize(inpath, outpath)
