import io
import os

from cryptography.fernet import Fernet

from PIL import Image


class ImageEncryption:
    def __init__(self, image_path, key_path=None):
        """
        클래스를 초기화합니다.

        Parameters:
        - image_path (str): 암호화할 이미지 파일의 경로
        - key_path (str, optional): 사용자가 제공하는 암호화 키 파일의 경로. 기본값은 None.

        초기화 메서드는 이미지 파일 경로와 키 파일 여부에 따라 동적으로 작동합니다.
        키 파일이 없으면 새로운 암호화 키를 생성하고, 이미지 파일을 엽니다.
        키 파일이 제공되면 파일에서 키를 읽어와 사용합니다.
        암호화에 사용될 Fernet 암호화 스위트도 초기화됩니다.

        Initializes the class.

        Parameters:
        - image_path (str): Path to the image file to be encrypted.
        - key_path (str, optional): Path to the user-provided encryption key file. Default is None.

        The initialization method dynamically operates based on the image file path and the presence of a key file.
        If no key file is provided, it generates a new encryption key and opens the image file.
        If a key file is provided, it reads the key from the file and uses it.
        The Fernet encryption suite to be used for encryption is also initialized.
        """
        self.image_path = image_path
        if key_path is None:
            self.key = Fernet.generate_key()
            self.image = Image.open(image_path)
        else:
            with open(key_path) as key_file:
                self.key = key_file.read().encode()
                print(self.key)
        self.cipher_suite = Fernet(self.key)
        print(self.cipher_suite)

    def encrypt_image(self, savePath):
        """
        이미지를 암호화하는 메서드입니다.

        Parameters:
        - savePath (str): 암호화된 이미지를 저장할 경로

        이미지 파일을 바이트로 읽어와서 Fernet을 사용하여 암호화한 후,
        암호화된 데이터를 주어진 경로에 바이너리 형식으로 저장합니다.

        Encrypts the image.

        Parameters:
        - savePath (str): Path to save the encrypted image.

        Reads the image file as bytes and encrypts the data using Fernet.
        Saves the encrypted data in binary format at the specified path.
        """
        with open(self.image_path, "rb") as image_file:
            original_image_data = image_file.read()
        encrypted_data = self.cipher_suite.encrypt(original_image_data)
        with open(savePath, "wb") as encrypted_image_file:
            encrypted_image_file.write(encrypted_data)

        # Get the directory of the image file
        directory = os.path.dirname(savePath)
        # Create the path for the key file
        key_path = os.path.join(directory, "key.txt")

        with open(key_path, "w") as key_file:
            key_file.write(self.key.decode())

    # 이미지를 복호화 (암호화 해제)하는 경우 savePath에 복호화된 이미지를 저장할 경로를 넣어주면 된다.
    def decrypt_image(self, savePath):
        """
        이미지를 복호화합니다.

        Parameters:
        - savePath (str): 복호화된 이미지를 저장할 경로

        암호화된 이미지 파일을 바이너리 모드로 읽어와서 Fernet을 사용하여 데이터를 복호화하고,
        복호화된 이미지를 지정된 경로에 저장합니다.

        Decrypts the image. Provide the path to save the decrypted image.

        Parameters:
        - savePath (str): Path to save the decrypted image.

        Reads the encrypted image file as bytes, decrypts the data using Fernet,
        and saves the decrypted image at the specified path.
        """
        with open(self.image_path, "rb") as encrypted_image_file:
            encrypted_data = encrypted_image_file.read()
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        decrypted_image = Image.open(io.BytesIO(decrypted_data))
        if decrypted_image.mode == "RGBA":
            decrypted_image = decrypted_image.convert("RGB")
        decrypted_image.save(savePath)

    # to be deleted
    def decrypt_show_image(self, savePath):
        """
        이미지를 복호화하고 복호화된 이미지 파일을 보여줍니다.

        Parameters:
        - savePath (str): 복호화된 이미지를 저장할 경로

        암호화된 이미지 파일을 바이너리 모드로 읽어와서 Fernet을 사용하여 데이터를 복호화하고,
        복호화된 이미지를 지정된 경로에 저장합니다.

        Decrypts the image. And shows the decrypted image.

        Parameters:
        - savePath (str): Path to save the decrypted image.

        Reads the encrypted image file as bytes, decrypts the data using Fernet,
        and saves the decrypted image at the specified path.
        """
        with open(self.image_path, "rb") as encrypted_image_file:
            encrypted_data = encrypted_image_file.read()
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        decrypted_image = Image.open(io.BytesIO(decrypted_data))
        if decrypted_image.mode == "RGBA":
            decrypted_image = decrypted_image.convert("RGB")
        decrypted_image.save(savePath)
        Image.open(savePath).show()
