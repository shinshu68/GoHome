import unittest
from repo import repo


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.path = '/home/shinshu/dotfiles'
        self.pre = {'pull': True}
        self.post = {'push': True}
        self.remote = {'remote': {'branch': 'master', 'name': 'origin'}}

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
        d = {}
        r = repo(self.path, pre=d)
        with self.assertRaises(ValueError):
            r.pre()

        d = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': []}
        r = repo(self.path, pre=d)
        with self.assertRaises(ValueError):
            r.pre()

        d = {'remote': {}, 'check': ['pull']}
        r = repo(self.path, pre=d)
        with self.assertRaises(ValueError):
            r.pre()

        d = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': ['push']}
        r = repo(self.path, pre=d)
        r.pre()

    def test_post(self):
        d = {}
        r = repo(self.path, post=d)
        with self.assertRaises(ValueError):
            r.post()

        d = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': []}
        r = repo(self.path, post=d)
        with self.assertRaises(ValueError):
            r.post()

        d = {'remote': {}, 'check': ['push']}
        r = repo(self.path, post=d)
        with self.assertRaises(ValueError):
            r.post()

        d = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': ['push']}
        r = repo(self.path, post=d)
        r.post()

    def test_is_inside_work_tree(self):
        path = self.path
        r = repo(path)
        self.assertTrue(r.is_inside_work_tree(path))

    def test_is_valid_path(self):
        path = self.path
        r = repo(path)
        self.assertTrue(r.is_valid_path(path))

        path = '~/'
        with self.assertRaises(ValueError):
            r = repo(path)
            r.is_valid_path(path)

    def test_check_push(self):
        r = repo(self.path, pre=self.remote)
        self.assertTrue(r.check_push())

        r = repo('~/workspace/prepost', pre=self.remote)
        self.assertFalse(r.check_push())


if __name__ == '__main__':
    unittest.main()

