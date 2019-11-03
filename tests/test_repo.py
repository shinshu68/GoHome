import unittest
from repo import repo


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.path = '~/prepost'
        self.pre = {'pull': True}
        self.post = {'push': True}

    def test_repo_init(self):
        with self.assertRaises(TypeError):
            r = repo()

        r = repo(path=self.path)
        self.assertEqual(r.path, self.path)

        r = repo(path=self.path, pre=self.pre)
        self.assertEqual(r.path, self.path)
        self.assertEqual(r._pre, self.pre)

        r = repo(path=self.path, post=self.post)
        self.assertEqual(r.path, self.path)
        self.assertEqual(r._post, self.post)

        with self.assertRaises(TypeError):
            r = repo(pre=self.pre, post=self.post)

        r = repo(self.path, self.pre, self.post)
        self.assertEqual(r.path, self.path)
        self.assertEqual(r._pre, self.pre)
        self.assertEqual(r._post, self.post)


if __name__ == '__main__':
    unittest.main()

