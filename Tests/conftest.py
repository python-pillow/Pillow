def pytest_report_header(config):
    import io

    try:
        from PIL import features

        with io.StringIO() as out:
            features.pilinfo(out=out, supported_formats=False)
            return out.getvalue()
    except Exception as e:
        return "pytest_report_header failed: %s" % str(e)
