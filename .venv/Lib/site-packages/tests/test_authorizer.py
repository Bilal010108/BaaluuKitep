import unittest

from authorizer import Signer

incorrect_sign_text = 'VimpClSJ04gqskSmDOFpUsmKWl8NpP9bcV3188Yc1B8UqBrFDAYJZy5lQUry2MMOqNPBbj5JEWEcAu32Kfnn2q8ImyPYSQWEP45UUhnw4hyvS+B+DasQzqitmXuGA7fWJ7qlzDbX3MI1JcalprI0QKpHKIIwPATE8/scjhO+d94vlqF7lDOpsxD4NEmrkHyl6r/NvfQ7+wmYDsY6T3NbrYWAErig9iUprsTZO/MaBJvFW82z+ejZ2qUt4Zl5eYaoKBcd/7KwzlvnNfwRF7bh0dlHsCJ81vTFUegsqDl+39nLx9bCmewbmm3w9MiYVPBfzJjZ0r9xzvon6Zcu2PWP5w==';

private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAoq/3UxpzgfXOLrJEZd39TJ7Fc4iRLMcK1Hj563O+sNcP4BnA\neNnRXfCCJCLs+UZxPLxV7f1Zj7zHmgUOsB6rPS3TJwbIIbclDrhoySzPAnTNg+jU\n9lpPS99vvT8tJpUb0zAA6sAwFxHUQk43mzgLou04eMlSHZmZ4MFVGzWGakIwDRlP\nMQbQCOiU+N/0Kl7qBDwDkn6USwc16MTa2Xm6BAhcwaug0jlhN5NIu7hyK2gk8In1\nS0OrxBEK3Z1zShRhixGEhA8Z7NREJCMuqHke09dVK1nVXz6CGTQMafjDKDwgmiBR\n7cJo25Icb/OqFs4TzE7XPfU/3gK0+1YdqF4J/wIDAQABAoIBADY3DeTT28pjb+J/\n5etMnyz5fDOUP0z8x88mwaKFX/butIuqCUo8zFjR3YzNVst7fiEPYlN9KmuMLbhW\nFx76GXa53rQSvn792YueSM1B8XqQEizzWoT+c46FV2dptlI1PqCSTrvscBpABsxR\n5JYFh1s0Uq1t6b+TgIQ16Xa3z6N5AyLVw7MbXEx2iB/bVdivmWNIjLWarr4yJDwA\nMgB/dOYtZp80ut8yOYYvaTmUVBUEp4ZHjBN+MgNlMD0zDZR/y+5mr1r3TfuPUsw9\neIDpD6tYwHvDgoneSGi1LtQpuEXTKhwEFezJkLZZnVCtFCdRaKkS607fT37fJOML\nDfNOgYECgYEAzpzgjzCz3+2qHJl+ejRtw2cUxCOIvVBAzvbqVk8R/NqZVF2WteUh\nx/0lM+FK0/AHpcnpZu79ruvra3yaB/AZuaPOnrsjzLQ2xsJfLpEu0Caoho3jWP7J\nFDGhX1CQeRXEQ9VM6l+PbjoKZ4bRO6ktVMuq/D7gBNvh/mNglCziLLsCgYEAyZMw\nO91zk+4DJucflLuNKiS56J8Sq71v6j+iFwF6zimYJJAFm7xdQ2vWXSP5jf5SeKVr\nQ/aA0ACSi0iYBEzhtQ19cCydjYQKSRvO0olMvRbcJfVgABCN+JtFIaSnWLS/sXST\nzcH3vm4FgccRHtt27HQIVCFHgwwVapymAYfnRY0CgYAPKTHNMAyy7NSjvpuqSfiX\n8xNyBQ1+nsnypemyJaEzRbMknq11cXfWHfxB31FHVgCpqLRIylaxJDylKYJ//J1W\nou+BdEf/OGYglZi4aQzfV0bcgMLi/+cvZSjrPpUrXW6Gb7tyI0r6EqY6zIjD8PkT\nlNJaKh70HFJsAUzP8q8yCwKBgQCFyFJy6P8UZxtgbnTfWbrPBaD9atYRdaEZbzI8\n4paGzcRUP+H5AoNDhAa5um6edvR1bhRK/wdvBXI9TujVsdD7QQDHulS237OT4gja\nYpWzycBC0R/t6w7OuP6g3Y7TqOKw/BY8sUej85FkGKKcQDwlor0EWTIFH7f3EhB7\nY59y4QKBgB5K2pRrw3wjQOHlssEO/2FqwE1NTYZalgpghPLRO+4Y8qM8hkKsBjgQ\nAQhd66mWIbIvuvcGErUrz3qFJHtjTIZHqOSVlW3hiiuMVKzZCoPa8nUJ0l6ylTpz\nNIb/T0HUwXgSRJBNhdHNo0yGFisaJpezF/kDUhOCzvTdoNI/M0Zy\n-----END RSA PRIVATE KEY-----\n';

public_key = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoq/3UxpzgfXOLrJEZd39\nTJ7Fc4iRLMcK1Hj563O+sNcP4BnAeNnRXfCCJCLs+UZxPLxV7f1Zj7zHmgUOsB6r\nPS3TJwbIIbclDrhoySzPAnTNg+jU9lpPS99vvT8tJpUb0zAA6sAwFxHUQk43mzgL\nou04eMlSHZmZ4MFVGzWGakIwDRlPMQbQCOiU+N/0Kl7qBDwDkn6USwc16MTa2Xm6\nBAhcwaug0jlhN5NIu7hyK2gk8In1S0OrxBEK3Z1zShRhixGEhA8Z7NREJCMuqHke\n09dVK1nVXz6CGTQMafjDKDwgmiBR7cJo25Icb/OqFs4TzE7XPfU/3gK0+1YdqF4J\n/wIDAQAB\n-----END PUBLIC KEY-----\n';


class TestSigner(Signer):
    def __init__(self, **request_data):
        super(TestSigner, self).__init__(**request_data)

    def get_http_method(self):
        return super(TestSigner, self)._get_http_method()

    def get_path(self):
        return super(TestSigner, self)._get_path()

    def get_headers_data(self):
        return super(TestSigner, self)._get_headers_data()

    def get_query_string_params_data(self):
        return super(TestSigner, self)._get_query_string_params_data()

    def get_json_body(self):
        return super(TestSigner, self)._get_json_body()

    def get_data(self):
        return super(TestSigner, self)._get_data()


class TestAuthorizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request_data = {
            'body': {'payment': 'payment', 'amount': 100, 'cyrillic_data': 'платеж'},
            'headers': {
                'Host': 'api.paymentsgateway.averspay.kg',
                'x-api-timestamp': '1636026186643',
                'x-api-key': 'h8z1TDStxu5YY2YuN8jUa9hpzIVbfkLT7kPiPiYj',
                'x-api-header': 'header value',
                'X-Forwarded-For': '54.187.127.20, 15.158.4.100',
                'X-Forwarded-Port': '443',
                'X-Forwarded-Proto': 'https',
            },
            'http_method': 'POST',
            'path': '/services',
            'query_string_parameters': {
                'from': '0',
                'size': '10',
                'test': None,
                'best': 'тест дата',
            },
        }

    def test_should_successfully_get_http_method(self):
        signer = TestSigner(**self.request_data)

        self.assertEqual('post', signer.get_http_method())

    def test_should_fait_to_get_headers_data_when_empty_headers_provided(self):
        request_data = {**self.request_data, 'headers': {}}

        signer = TestSigner(**request_data)

        self.assertRaises(Exception, signer.get_headers_data)

    def test_should_successfully_get_headers_data_when_normal_header_provided(self):
        signer = TestSigner(**self.request_data)

        self.assertEqual('host:api.paymentsgateway.averspay.kg&x-api-header:header value&x-api-key:h8z1TDStxu5YY2YuN8jUa9hpzIVbfkLT7kPiPiYj&x-api-timestamp:1636026186643', signer.get_headers_data())

    def test_should_successfully_get_query_string_params_data_when_query_string_params_not_provided(self):
        request_data = {**self.request_data, 'query_string_parameters': None}

        signer = TestSigner(**request_data)

        self.assertEqual('', signer.get_query_string_params_data())

    def test_should_successfully_get_query_string_params_data_when_query_string_params_provided(self):
        signer = TestSigner(**self.request_data)

        self.assertEqual('best=%D1%82%D0%B5%D1%81%D1%82%20%D0%B4%D0%B0%D1%82%D0%B0&from=0&size=10&test=', signer.get_query_string_params_data())

    def test_should_successfully_get_encoded_query_string_params_data(self):
        request_data = {**self.request_data, 'query_string_parameters': {
            'from': '0',
            'size': '10',
            'test': None,
            'best': '%D1%82%D0%B5%D1%81%D1%82%20%D0%B4%D0%B0%D1%82%D0%B0',
        }}

        signer = TestSigner(**request_data)

        self.assertEqual('best=%D1%82%D0%B5%D1%81%D1%82%20%D0%B4%D0%B0%D1%82%D0%B0&from=0&size=10&test=', signer.get_query_string_params_data())

    def test_should_successfully_get_simple_path(self):
        request_data = {**self.request_data, 'path': '/services/жаны-cервис'}

        signer = TestSigner(**request_data)

        self.assertEqual('/services/жаны-cервис', signer.get_path())

    def test_should_successfully_get_encoded_path(self):
        request_data = {**self.request_data, 'path': '/services/%D0%B6%D0%B0%D0%BD%D1%8B-c%D0%B5%D1%80%D0%B2%D0%B8%D1%81'}

        signer = TestSigner(**request_data)

        self.assertEqual('/services/жаны-cервис', signer.get_path())

    def test_should_successfully_get_empty_path(self):
        request_data = {**self.request_data, 'path': None}

        signer = TestSigner(**request_data)

        self.assertEqual('', signer.get_path())

    def test_should_successfully_get_json_body(self):
        signer = TestSigner(**self.request_data)

        self.assertEqual('{"amount":100,"cyrillic_data":"платеж","payment":"payment"}', signer.get_json_body())

    def test_should_successfully_get_empty_string_when_there_is_no_body(self):
        request_data = {**self.request_data, 'body': None}

        signer = TestSigner(**request_data)

        self.assertEqual('', signer.get_json_body())

    def test_should_successfully_get_data(self):
        signer = TestSigner(**self.request_data)

        self.assertEqual('post\n/services\nhost:api.paymentsgateway.averspay.kg&x-api-header:header value&x-api-key:h8z1TDStxu5YY2YuN8jUa9hpzIVbfkLT7kPiPiYj&x-api-timestamp:1636026186643\nbest=%D1%82%D0%B5%D1%81%D1%82%20%D0%B4%D0%B0%D1%82%D0%B0&from=0&size=10&test=\n{"amount":100,"cyrillic_data":"платеж","payment":"payment"}', signer.get_data())

    def test_should_successfully_sign(self):
        signer = TestSigner(**self.request_data)

        signature = signer.sign(private_key)

        self.assertEqual('n2nMbkKnyCPrUux+9Vk+uDsxTR2hjqY01NGrd3288x5o5ab2kGphYq8sWw1SjRqzz4IOs+Q3PyeyjvIGoWMA88EoeonaGDrXYOnuJHmydmy5TsSQ6OianFdBgBurcm8wbI6TnZcIG/AeGkMlpF4fLSnelWOfB8apKPI3GMmqSpo25bkhhcdVKbP4IyHUPbRAj77JNDcl7bwD3I/l1slkcjiiweHKjwd2SpvNw/D1SyFV0/U5+s3kyMoAnVp6PHwSHmxVlbyIWCLlcTueMbBtdNFij+xTuarvaS0nQM1K1co2l/ix6jVaKX7S/g1zoUdgq06jd1Q8qGwh7wNR5L0QeQ==', signature)

    def test_should_successfully_verify(self):
        signer = TestSigner(**self.request_data)

        signature = signer.sign(private_key)

        is_valid = signer.verify(public_key, signature)

        self.assertTrue(is_valid)

    def test_should_fail_to_verify_with_incorrect_signature(self):
        signer = TestSigner(**self.request_data)

        is_valid = signer.verify(public_key, incorrect_sign_text)

        self.assertFalse(is_valid)

    def test_should_successfully_match_sign_with_simple_path_and_encoded_path(self):
        encoded_path_data = {
            **self.request_data,
            'path': '/services/%D0%B6%D0%B0%D0%BD%D1%8B-c%D0%B5%D1%80%D0%B2%D0%B8%D1%81'
        }

        signer1 = TestSigner(**encoded_path_data)

        simple_path_data = {
            **self.request_data,
            'path': '/services/жаны-cервис'
        }

        signer2 = TestSigner(**simple_path_data)

        self.assertEqual(signer1.sign(private_key), signer2.sign(private_key))
