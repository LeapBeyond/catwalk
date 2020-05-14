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
"""Module to check encryption and decryption process"""
import unittest

from catwalk.cryptography import AESGCMB64Cipher


class TestAESGCM(unittest.TestCase):

    def test_keygen(self):
        print("Testing keygen")

        bit_length = 256
        key = AESGCMB64Cipher.generate_key(bit_length)
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), bit_length / 4)

    def test_encryption(self):
        print("Testing encryption")

        key = "01234567890123456789012345678901"
        message = "Test message"

        encrypted = AESGCMB64Cipher.encrypt_with_key(key, message.encode("utf-8"))
        self.assertIsInstance(encrypted, bytes)

        print("Testing decryption")

        decrypted = AESGCMB64Cipher.decrypt_with_key(key, encrypted)
        self.assertEqual(decrypted.decode("utf-8"), message)


if __name__ == '__main__':
    unittest.main()
