from common import log
from common.log import InterceptTimedRotatingFileHandler


def test_handler_adds_each_file_sink_only_once(tmp_path):
    filename = tmp_path / "auth" / "auth.log"
    InterceptTimedRotatingFileHandler(str(filename), when="H")
    sinks_after_first = len(log._SINKS)
    InterceptTimedRotatingFileHandler(str(filename), when="H")  # Django may configure logging twice
    assert len(log._SINKS) == sinks_after_first
    assert sum(str(tmp_path) in sink for sink in log._SINKS) == 4  # debug, info, warning, error
