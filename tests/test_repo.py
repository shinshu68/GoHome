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
        self.assertEqual(r._path, self.path)

        r = repo(path=self.path, pre=self.pre)
        self.assertEqual(r._path, self.path)
        self.assertEqual(r._pre, self.pre)

        r = repo(path=self.path, post=self.post)
        self.assertEqual(r._path, self.path)
        self.assertEqual(r._post, self.post)

        with self.assertRaises(TypeError):
            r = repo(pre=self.pre, post=self.post)

        r = repo(self.path, self.pre, self.post)
        self.assertEqual(r._path, self.path)
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

    def test_get_path(self):
        r = repo(self.path, self.pre, self.post)
        self.assertEqual(self.path, r.get_path())

    def test_get_pre(self):
        r = repo(self.path, self.pre, self.post)
        self.assertDictEqual(self.pre, r.get_pre())

    def test_get_post(self):
        r = repo(self.path, self.pre, self.post)
        self.assertDictEqual(self.post, r.get_post())

    def test_is_valid_data(self):
        r = repo(self.path)
        bad_data = [
            {},
            {'remote': {'name': 'origin', 'branch': 'master'}, 'check': []},
            {'remote': {}, 'check': ['pull']},
        ]
        for d in bad_data:
            self.assertFalse(r.is_valid_data(d))

        ok_data = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': ['push']}
        self.assertTrue(r.is_valid_data(ok_data))

    def test_pre(self):
        bad_data = [
            {},
            {'remote': {'name': 'origin', 'branch': 'master'}, 'check': []},
            {'remote': {}, 'check': ['pull']},
        ]
        for d in bad_data:
            r = repo(self.path, pre=d)
            self.assertFalse(r.pre())

        ok_data = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': ['push']}
        r = repo(self.path, pre=ok_data)
        self.assertTrue(r.pre())

    def test_post(self):
        bad_data = [
            {},
            {'remote': {'name': 'origin', 'branch': 'master'}, 'check': []},
            {'remote': {}, 'check': ['push']},
        ]
        for d in bad_data:
            r = repo(self.path, post=d)
            self.assertFalse(r.post())

        ok_data = {'remote': {'name': 'origin', 'branch': 'master'}, 'check': ['push']}
        r = repo(self.path, post=ok_data)
        self.assertTrue(r.post())

    def test_is_inside_work_tree(self):
        path = self.path
        r = repo(path)
        self.assertTrue(r.is_inside_work_tree(r._path))

        path = '~/'
        r = repo(path)
        self.assertFalse(r.is_inside_work_tree(r._path))

    def test_is_valid_path(self):
        path = self.path
        r = repo(path)
        self.assertTrue(r.is_valid_path(path))

        path = '~/'
        r = repo(path)
        self.assertFalse(r.is_valid_path(path))

    def test_is_pushed(self):
        r = repo(self.path, pre=self.remote)
        self.assertTrue(r.is_pushed(self.remote))

    def test_is_pulled(self):
        r = repo(self.path, pre=self.remote)
        self.assertFalse(r.is_pulled(self.remote))

    def test_git_commit_distance(self):
        r = repo(self.path)
        self.assertEqual(r.git_commit_distance('ac676ec', 'e02e693'), 4)


if __name__ == '__main__':
    unittest.main()

