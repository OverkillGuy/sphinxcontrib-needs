from pathlib import Path

from sphinx_testing import with_app

from sphinxcontrib.needs.services.base import BaseService
from sphinxcontrib.needs.services.manager import ServiceManager


class TestService(BaseService):

    options = ["custom_option", "exists"]

    def __init__(self, app, name, config, **kwargs):
        self.custom_option = config.get("custom_option", False)

        super().__init__()

    def request(self, options):
        data = [
            {
                "title": "service_test_title",
                "id": "TEST_001",
                "exists": options.get("exists", "False"),
                "not_exists": options.get("not_exists", "False"),
                "custom_option": self.custom_option,
                # 'content': 'test_content'
            }
        ]
        return data

    def debug(self, options):
        debug_data = {
            "request": {
                "url": "http://dummy.company.com/my/service",
                "user": "my_user",
            },
            "answer": {"status_code": 200, "body": {"item_amount": 2, "items": ["item_1", "item_2"]}},
        }

        return debug_data


class NoDebugService(BaseService):

    options = []

    def __init__(self, app, name, config, **kwargs):
        super().__init__()

    def request(self, options):
        return []


@with_app(buildername="html", srcdir="doc_test/service_doc")
def test_service_creation(app, status, warning):
    app.build()
    assert isinstance(app.needs_services, ServiceManager)

    manager = app.needs_services
    service = manager.get("testservice")
    assert hasattr(service, "custom_option")

    assert service.custom_option

    html = Path(app.outdir, "index.html").read_text()

    assert "service_test_title" in html
    assert "TEST_001" in html

    assert "custom_option_True" in html

    assert "exists_True" in html
    assert "not_exists" not in html

    # Debug mode checks
    # JS got not executed, so we can not test for generated HTML nodes.
    assert "http://dummy.company.com/my/service" in html
    assert '"items": ["item_1", "item_2"]' in html
