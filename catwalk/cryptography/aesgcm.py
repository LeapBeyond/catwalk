##############################################################################
#
# Copyright 2019 Leap Beyond Emerging Technologies B.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
"""Standard encryption protocol"""
import os
from base64 import standard_b64encode, standard_b64decode

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESGCMB64Cipher(object):
    """Uses AES-GCM encryption and base64 encoding to encrypt/decrypt messages"""

    nonce_length = 12

    def __init__(self, key):
        self._cipher = AESGCM(bytes.fromhex(key))

    @classmethod
    def generate_key(cls, bit_length=256):
        """Generates an encryption key, then coverts it into a hex string.

        :param int bit_length: must be 128, 192, or 256.
        :return str: the generated key.
        """
        key = AESGCM.generate_key(bit_length)
        return key.hex().upper()

    @classmethod
    def encrypt_with_key(cls, key, message, additional_data=None):
        """Convenience class method for encrypting a message with a key.

        :param str key: The encryption key as a hex string.
        :param bytes message: the message to encrypt.
        :param additional_data: optional additional data to append.
        :return bytes: the encrypted message.
        """
        cipher = cls(key)
        return cipher.encrypt(message, additional_data)

    @classmethod
    def decrypt_with_key(cls, key, message, additional_data=None):
        """Convenience class method for decrypting a message with a key.

        :param str key: The encryption key as a hex string.
        :param bytes message: the message to decrypt.
        :param additional_data: optional additional data to append.
        :return bytes: the decrypted message.
        """
        cipher = cls(key)
        return cipher.decrypt(message, additional_data)

    def encrypt(self, data, additional_data=None):
        """Encrypts a message.

        :param bytes data: the message to encrypt.
        :param additional_data: optional additional data to append.
        :return bytes: the encrypted message.
        """
        nonce = os.urandom(self.nonce_length)
        encrypted = self._cipher.encrypt(nonce, data, additional_data)
        return standard_b64encode(nonce + encrypted)

    def decrypt(self, data, additional_data=None):
        """Decrypts a message.

        :param bytes data: the message to decrypt.
        :param additional_data: optional additional data to append.
        :return bytes: the decrypted message.
        """
        data = standard_b64decode(data)
        nonce = data[:self.nonce_length]
        data = data[self.nonce_length:]
        return self._cipher.decrypt(nonce, data, additional_data)
