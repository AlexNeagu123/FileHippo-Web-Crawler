class RegexFail(Exception):
    msg = "Regex Error"


class RequestLimit(Exception):
    msg = "Request limit of 20 achieved"
