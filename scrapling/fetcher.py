from scrapling._types import Any, Dict, Optional, Union

from scrapling.engines import CamoufoxEngine, StaticEngine, check_if_engine_usable
from scrapling.parser import Adaptor, SQLiteStorageSystem


class Fetcher:
    def __init__(
            self,
            browser_engine: Optional[object] = None,
            # Adaptor class parameters
            response_encoding: str = "utf8",
            huge_tree: bool = True,
            keep_comments: Optional[bool] = False,
            auto_match: Optional[bool] = False,
            storage: Any = SQLiteStorageSystem,
            storage_args: Optional[Dict] = None,
            debug: Optional[bool] = True,
    ):
        if browser_engine is not None:
            self.engine = check_if_engine_usable(browser_engine)
        else:
            self.engine = CamoufoxEngine()
        # I won't validate Adaptor's class parameters here again, I will leave it to be validated later
        self.__encoding = response_encoding
        self.__huge_tree = huge_tree
        self.__keep_comments = keep_comments
        self.__auto_match = auto_match
        self.__storage = storage
        self.__storage_args = storage_args
        self.__debug = debug

    def __generate_adaptor(self, url, html_content):
        """To make the code less repetitive and manage return result from one function"""
        return Adaptor(
            text=html_content,
            url=url,
            encoding=self.__encoding,
            huge_tree=self.__huge_tree,
            keep_comments=self.__keep_comments,
            auto_match=self.__auto_match,
            storage=self.__storage,
            storage_args=self.__storage_args,
            debug=self.__debug,
        )

    def fetch(self, url: str) -> Adaptor:
        html_content = self.engine.fetch(url)
        return self.__generate_adaptor(url, html_content)

    def get(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Adaptor:
        html_content = StaticEngine(follow_redirects, timeout).get(url, stealthy_headers, **kwargs)
        return self.__generate_adaptor(url, html_content)

    def post(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Adaptor:
        html_content = StaticEngine(follow_redirects, timeout).post(url, stealthy_headers, **kwargs)
        return self.__generate_adaptor(url, html_content)

    def put(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Adaptor:
        html_content = StaticEngine(follow_redirects, timeout).put(url, stealthy_headers, **kwargs)
        return self.__generate_adaptor(url, html_content)

    def delete(self, url: str, follow_redirects: bool = True, timeout: Optional[Union[int, float]] = None, stealthy_headers: Optional[bool] = True, **kwargs: Dict) -> Adaptor:
        html_content = StaticEngine(follow_redirects, timeout).delete(url, stealthy_headers, **kwargs)
        return self.__generate_adaptor(url, html_content)
