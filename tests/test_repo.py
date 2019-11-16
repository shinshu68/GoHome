import os
import unittest
from src.repo import repo


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.path = '~/workspace/prepost'
        self.expand_path = f'{os.getenv("HOME")}/workspace/prepost'
        self.data = {
            'local': 'master',
            'remote': {'branch': 'master', 'name': 'origin'},
            'commands': ['push', 'pull']
        }
        self.bad_data = [
            {
                # 'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                'commands': ['push', 'pull']
            },
            {
                # 'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                'commands': ['push', 'pull']
            },
            {
                'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                # 'commands': ['push', 'pull']
            },
            {
                'local': 'master',
                'remote': {'branch': 'master', 'name': 'origin'},
                'commands': ['hoge', 'fuga']
            },
            {
                'local': 'hoge',
                'remote': {'branch': 'master', 'name': 'origin'},
                'commands': ['push', 'pull']
            }
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
        self.assertEqual(self.expand_path, r.get_expand_path())

    def test_execute(self):
        r = repo(self.path, self.data)
        d = {
            'pull': True,
            'push': True
        }
        self.assertDictEqual(r.execute(), d)

    def test_is_pushed(self):
        r = repo(self.path, self.data)
        self.assertTrue(r.is_pushed())

    def test_is_pulled(self):
        r = repo(self.path, self.data)
        self.assertTrue(r.is_pulled())

    def test_is_committed(self):
        r = repo(self.path, self.data)
        self.assertTrue(r.is_committed())

    def test_git_commit_distance(self):
        r = repo('~/workspace/prepost', self.data)
        # git log --oneline
        # e02e693 :hammer: パスが有効かチェックする命令を追加
        # e9468b5 :sparkles: テストを満たす関数を作成
        # fbc1a76 :sparkles: テスト追加
        # 144ec46 :sparkles: テストを満たすように関数を修正
        # ac676ec :bug: 例外を投げるのは微妙に感じたのでtrue/falseに変更
        self.assertEqual(r.git_commit_distance('ac676ec', 'e02e693'), 4)
        self.assertEqual(r.git_commit_distance('e02e693', 'ac676ec'), -4)
        self.assertEqual(r.git_commit_distance('e02e693', 'e02e693'), 0)

    def test_is_exists_commit_hash(self):
        r = repo(self.path, self.data)
        self.assertFalse(r.is_exists_commit_hash(0))
        self.assertTrue(r.is_exists_commit_hash('ac676ec'))


if __name__ == '__main__':
    unittest.main()

