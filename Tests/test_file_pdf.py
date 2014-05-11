from tester import *
import os.path


def test_to_pdf():
    # Arrange
    im = lena()
    outfile = tempfile("temp.pdf")

    # Act
    im.save(outfile)

    # Assert
    assert_true(os.path.isfile(outfile))
    assert_greater(os.path.getsize(outfile), 0)

# End of file
