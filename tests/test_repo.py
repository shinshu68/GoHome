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

        d = {'remote': {'branch': 'master', 'name': 'origin'}}
        r = repo(self.path, pre=d)
        with self.assertRaises(ValueError):
            r.pre()

        d['check'] = []
        r = repo(self.path, pre=d)
        with self.assertRaises(ValueError):
            r.pre()

        d['check'] = ['pull']
        r = repo(self.path, pre=d)
        r.pre()

    def test_post(self):
        r = repo(self.path, pre={})
        with self.assertRaises(ValueError):
            r.pre()

        d = {'remote': {'branch': 'master', 'name': 'origin'}}
        r = repo(self.path, post=d)
        with self.assertRaises(ValueError):
            r.post()

        d['check'] = []
        r = repo(self.path, post=d)
        with self.assertRaises(ValueError):
            r.post()

        d['check'] = ['push']
        r = repo(self.path, post=d)
        r.post()

    def test_is_inside_work_tree(self):
        path = self.path
        r = repo(path)
        self.assertTrue(r.is_inside_work_tree(path))

    def test_is_valid_path(self):
        path = self.path
        r = repo(path)

        path = '~/'
        with self.assertRaises(ValueError):
            r = repo(path)
            r.is_inside_work_tree(path)


if __name__ == '__main__':
    unittest.main()

