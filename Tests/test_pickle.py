from tester import *

from PIL import Image


def helper_test_pickle_file(pickle, protocol=0):
    im = Image.open('Images/lena.jpg')
    filename = tempfile('temp.pkl')

    # Act
    with open(filename, 'wb') as f:
        pickle.dump(im, f, protocol)
    with open(filename, 'rb') as f:
        loaded_im = pickle.load(f)

    # Assert
    assert_image_completely_equal(im, loaded_im)


def helper_test_pickle_string(pickle, protocol=0, file='Images/lena.jpg'):
    im = Image.open(file)

    # Act
    dumped_string = pickle.dumps(im, protocol)
    loaded_im = pickle.loads(dumped_string)

    # Assert
    assert_image_completely_equal(im, loaded_im)


def test_pickle_image():
    # Arrange
    import pickle

    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_test_pickle_string(pickle, protocol)
        helper_test_pickle_file(pickle, protocol)


def test_cpickle_image():
    # Arrange
    try:
        import cPickle
    except ImportError:
        skip()

    # Act / Assert
    for protocol in range(0, cPickle.HIGHEST_PROTOCOL + 1):
        helper_test_pickle_string(cPickle, protocol)
        helper_test_pickle_file(cPickle, protocol)


def test_pickle_p_mode():
    # Arrange
    import pickle

    # Act / Assert
    for file in [
            "Tests/images/test-card.png",
            "Tests/images/zero_bb.png",
            "Tests/images/zero_bb_scale2.png",
            "Tests/images/non_zero_bb.png",
            "Tests/images/non_zero_bb_scale2.png",
            "Tests/images/p_trns_single.png",
            "Tests/images/pil123p.png"
    ]:
        helper_test_pickle_string(pickle, file=file)

# End of file
