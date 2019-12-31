from .helper import PillowTestCase, hopper


class TestImageEntropy(PillowTestCase):
    def test_entropy(self):
        def entropy(mode):
            return hopper(mode).entropy()

        self.assertAlmostEqual(entropy("1"), 0.9138803254693582)
        self.assertAlmostEqual(entropy("L"), 7.063008716585465)
        self.assertAlmostEqual(entropy("I"), 7.063008716585465)
        self.assertAlmostEqual(entropy("F"), 7.063008716585465)
        self.assertAlmostEqual(entropy("P"), 5.0530452472519745)
        self.assertAlmostEqual(entropy("RGB"), 8.821286587714319)
        self.assertAlmostEqual(entropy("RGBA"), 7.42724306524488)
        self.assertAlmostEqual(entropy("CMYK"), 7.4272430652448795)
        self.assertAlmostEqual(entropy("YCbCr"), 7.698360534903628)
