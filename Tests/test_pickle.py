from tester import *

from PIL import Image


def test_frombytes_tobytes():
    # Arrange
    im = Image.open('Images/lena.jpg')

    # Act
    data = im.tobytes()
    new_im = Image.frombytes(im.mode, im.size, data)

    # Assert
    assert_image_equal(im, new_im)


def helper_test_pickle_file(pickle, protocol=0):
    im = Image.open('Images/lena.jpg')
    filename = tempfile('temp.pkl')

    # Act
    with open(filename, 'wb') as f:
        pickle.dump(im, f, protocol)
    with open(filename, 'rb') as f:
        loaded_im = pickle.load(f)

    # Assert
    assert_image_equal(im, loaded_im)


def helper_test_pickle_string(pickle, protocol=0):
    im = Image.open('Images/lena.jpg')

    # Act
    dumped_string = pickle.dumps(im, protocol)
    loaded_im = pickle.loads(dumped_string)

    # Assert
    assert_image_equal(im, loaded_im)


def test_pickle_image():
    # Arrange
    import pickle

    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_test_pickle_string(pickle, protocol)
        helper_test_pickle_file(pickle, protocol)


def test_cpickle_image():
    # Arrange
    import cPickle

    # Act / Assert
    for protocol in range(0, cPickle.HIGHEST_PROTOCOL + 1):
        helper_test_pickle_string(cPickle, protocol)
        helper_test_pickle_file(cPickle, protocol)


# End of file
