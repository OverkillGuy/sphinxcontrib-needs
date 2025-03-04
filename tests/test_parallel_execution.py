from pathlib import Path

from sphinx_testing import with_app


@with_app(buildername="html", srcdir="doc_test/parallel_doc", parallel=4, warningiserror=True)
def test_doc_build_html(app, status, warning):
    # app.builder.build_all()
    app.build()
    html = Path(app.outdir, "index.html").read_text()
    assert app.statuscode == 0
    assert "<h1>PARALLEL TEST DOCUMENT" in html
    assert "SP_TOO_001" in html
