import os
import unittest
from repo import repo


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.path = '~/workspace/prepost'
        self.expand_path = f'{os.getenv("HOME")}/workspace/prepost'
        self.data = {
            'local': 'master',
            'remote': {'branch': 'master', 'name': 'origin'},
            'check': ['push', 'pull']
        }
        self.bad_data = [
            {
                # 'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                'check': ['push', 'pull']
            },
            {
                # 'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                'check': ['push', 'pull']
            },
            {
                'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                # 'check': ['push', 'pull']
            },
        ]

    def test_repo_init(self):
        with self.assertRaises(TypeError):
            r = repo()

        with self.assertRaises(TypeError):
            r = repo(path=self.path)

        with self.assertRaises(TypeError):
            r = repo(data=self.data)

        r = repo(path=self.path, data=self.data)
        self.assertEqual(r._path, self.path)
        self.assertEqual(r._data, self.data)

    def test_repo_str(self):
        r = repo(self.path, self.data)
        d = {
            'path': self.path,
            'expand_path': self.expand_path,
            'data': self.data
        }
        self.assertEqual(str(r), str(d))

    def test_get_path(self):
        r = repo(self.path, self.data)
        self.assertEqual(self.path, r.get_path())

    def test_get_data(self):
        r = repo(self.path, self.data)
        self.assertDictEqual(self.data, r.get_data())

    def test_get_expand_path(self):
        r = repo(self.path, self.data)
        self.assertDictEqual(self.expand_path, r.get_expand_path())

    def test_is_valid_data(self):
        for bad_data in self.bad_data:
            with self.assertRaises(TypeError):
                r = repo(self.path, bad_data)

        ok_data = {
            'local': 'master',
            'remote': {'branch': 'master', 'name': 'origin'},
            'check': ['push', 'pull']
        }
        r = repo(self.path, ok_data)
        self.assertTrue(r.is_valid_data(ok_data))

    def test_execute(self):
        for bad_data in self.bad_data:
            with self.assertRaises(TypeError):
                r = repo(self.path, bad_data)

        ok_data = {
            'local': 'master',
            'remote': {'branch': 'master', 'name': 'origin'},
            'check': ['push', 'pull']
        }
        r = repo(self.path, data=ok_data)
        self.assertTrue(r.execute())

    def test_is_inside_work_tree(self):
        path = '~/workspace/prepost'
        r = repo(path, self.data)
        self.assertTrue(r.is_inside_work_tree(r.get_expand_path()))

        path = '~/'
        r = repo(path, self.data)
        self.assertFalse(r.is_inside_work_tree(r.get_expand_path()))

    def test_is_valid_path(self):
        path = '~/workspace/prepost'
        r = repo(path, self.data)
        self.assertTrue(r.is_valid_path(r.get_expand_path()))

        path = '~/'
        r = repo(path, self.data)
        self.assertFalse(r.is_valid_path(r.get_expand_path()))

    def test_is_pushed(self):
        r = repo(self.path, self.data)
        self.assertTrue(r.is_pushed(self.data))

    def test_is_pulled(self):
        r = repo(self.path, pre=self.remote)
        self.assertTrue(r.is_pulled(self.data))

    def test_git_commit_distance(self):
        r = repo('~/workspace/prepost')
        self.assertEqual(r.git_commit_distance('ac676ec', 'e02e693'), 4)
        self.assertEqual(r.git_commit_distance('e02e693', 'ac676ec'), -4)
        self.assertEqual(r.git_commit_distance('e02e693', 'e02e693'), 0)


if __name__ == '__main__':
    unittest.main()

