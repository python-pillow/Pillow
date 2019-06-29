from .helper import PillowTestCase, hopper


class TestUploader(PillowTestCase):
    def check_upload_equal(self):
        result = hopper("P").convert("RGB")
        target = hopper("RGB")
        self.assert_image_equal(result, target)

    def check_upload_similar(self):
        result = hopper("P").convert("RGB")
        target = hopper("RGB")
        self.assert_image_similar(result, target, 0)
