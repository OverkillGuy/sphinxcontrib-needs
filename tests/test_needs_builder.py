import json
from pathlib import Path

from sphinx_testing import with_app


@with_app(buildername="needs", srcdir="doc_test/doc_needs_builder")
def test_doc_needs_builder(app, status, warning):
    app.build()

    needs_json = Path(app.outdir, "needs.json")
    with open(needs_json) as needs_file:
        needs_file_content = needs_file.read()

    needs_list = json.loads(needs_file_content)
    assert needs_list["versions"]["1.0"]
    assert needs_list["versions"]["1.0"]["needs"]["TC_NEG_001"]

    # needs builder added new version needs from needs_files
    assert needs_list["versions"]["2.0"]
    assert needs_list["versions"]["2.0"]["needs"]["TEST_01"]


@with_app(buildername="needs", srcdir="doc_test/doc_needs_builder_negative_tests")
def test_doc_needs_build_without_needs_file(app, status, warning):
    import os
    import subprocess

    srcdir = "doc_test/doc_needs_builder_negative_tests"
    out_dir = os.path.join(srcdir, "_build")

    out = subprocess.run(["sphinx-build", "-b", "needs", srcdir, out_dir], capture_output=True)
    assert not out.stderr
    assert "needs.json found, but will not be used because needs_file not configured." in out.stdout.decode("utf-8")


@with_app(buildername="needs", srcdir="../docs")
def test_needs_official_doc(app, status, warning):
    app.build()


@with_app(buildername="html", srcdir="doc_test/doc_needs_builder_parallel")
def test_needs_html_and_json(app, status, warning):
    """
    Build html output and needs.json in one sphinx-build
    """
    import json
    import os
    import subprocess

    app.build()

    needs_json_path = os.path.join(app.outdir, "needs.json")
    assert os.path.exists(needs_json_path)

    srcdir = "doc_test/doc_needs_builder_parallel"
    build_dir = os.path.join(app.outdir, "../needs")
    subprocess.run(["sphinx-build", "-b", "needs", srcdir, build_dir], capture_output=True)
    needs_json_path_2 = os.path.join(build_dir, "needs.json")
    assert os.path.exists(needs_json_path_2)

    # Check if the needs.json files from html/parallel build and builder are the same
    with open(needs_json_path) as f1:
        needs_1 = json.load(f1)
        with open(needs_json_path_2) as f2:
            needs_2 = json.load(f2)

            # Just check need-data, as the rest contains not matching timestamps
            need_data_1 = needs_1["versions"]["1.0"]["needs"]
            need_data_2 = needs_2["versions"]["1.0"]["needs"]
            assert need_data_1 == need_data_2
