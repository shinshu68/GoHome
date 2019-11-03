import unittest
from repo import repo


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.path = '/home/shinshu/dotfiles'
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

    def test_repo_str(self):
        r = repo(self.path, self.pre, self.post)
        d = {
            'path': self.path,
            'pre': self.pre,
            'post': self.post
        }
        self.assertEqual(str(r), str(d))

    def test_get_pre(self):
        r = repo(self.path, self.pre, self.post)
        self.assertDictEqual(self.pre, r.get_pre())

    def test_get_post(self):
        r = repo(self.path, self.pre, self.post)
        self.assertDictEqual(self.post, r.get_post())

    def test_pre(self):
        r = repo(self.path, pre={})
        with self.assertRaises(ValueError):
            r.pre()

        r = repo(self.path, pre={'branch': 'master'})
        with self.assertRaises(ValueError):
            r.pre()

        r = repo(self.path, pre={'branch': 'master', 'check': []})
        with self.assertRaises(ValueError):
            r.pre()

        r = repo(self.path, pre={'branch': 'master', 'check': ['pull']})
        r.pre()

    def test_post(self):
        r = repo(self.path, pre={})
        with self.assertRaises(ValueError):
            r.pre()

        r = repo(self.path, post={'branch': 'master'})
        with self.assertRaises(ValueError):
            r.post()

        r = repo(self.path, post={'branch': 'master', 'check': []})
        with self.assertRaises(ValueError):
            r.post()

        r = repo(self.path, post={'branch': 'master', 'check': ['push']})
        r.post()

    def test_is_inside_work_tree(self):
        r = repo(self.path)
        self.assertTrue(r.is_inside_work_tree())

        r = repo(self.path + '/config')
        self.assertTrue(r.is_inside_work_tree())

        r = repo('~/')
        self.assertFalse(r.is_inside_work_tree())


if __name__ == '__main__':
    unittest.main()

