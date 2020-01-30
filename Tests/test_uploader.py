from .helper import PillowTestCase, assert_image_equal, assert_image_similar, hopper


class TestUploader(PillowTestCase):
    def check_upload_equal(self):
        result = hopper("P").convert("RGB")
        target = hopper("RGB")
        assert_image_equal(result, target)

    def check_upload_similar(self):
        result = hopper("P").convert("RGB")
        target = hopper("RGB")
        assert_image_similar(result, target, 0)
