import re


class ResumeText:
    def __init__(self):
        self.bullet_pattern = re.compile(
            "[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
            re.UNICODE,
        )
        self.start_bullet_pattern = re.compile(
            "^[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+]",
            re.UNICODE)
        self.spacer_bullet_pattern = re.compile(
            " +[\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2022\u2023\u2043\u204C\u204D\u2219\u25CB\u25CF\u25D8\u25E6\u261A\u261B\u261C\u261E\u2E17\u2E1A\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D*•>/+] +",
            re.UNICODE,
        )
        self.all_caps_line = re.compile(r"^[A-Z\d_\W]+$")
        self.bullet_replacement = "-"
        self.spacer_replacement = "|"

    def clean(self, text):
        # replace start bullets with hyphen
        text = self.start_bullet_pattern.sub(f"{self.bullet_replacement} ", text)
        # replace bullets used as a spacer (e.g. between skills) with a pipe
        text = self.spacer_bullet_pattern.sub(f" {self.spacer_replacement} ", text)


