import unittest

from cantoolz.stream.forced_sampler import ForcedSampler


class TestForcedSampler(unittest.TestCase):

    def test_process(self):
        sampler = ForcedSampler(1, lambda x: x)

        effects_count = 0

        for _ in sampler('1'):
            effects_count += 1

        self.assertEqual(effects_count, 0)

        for _ in sampler('2'):
            effects_count += 1

        self.assertEqual(effects_count, 0)

        for message in sampler('2'):
            self.assertIn(message, ['1', '2'])
            effects_count += 1

        self.assertEqual(effects_count, 2)

        for message in sampler():
            self.assertIn(message, ['1', '2'])
            effects_count += 1

        self.assertEqual(effects_count, 4)

    def test_bind(self):
        sampler = ForcedSampler(2, lambda x, y: (x, y))

        list(sampler('2'))
        list(sampler('1'))

        effects_count = 0

        for m in sampler('1'):
            self.assertIn(m, [('1', '1'), ('1', '2'), ('2', '2')])
            effects_count += 1

        self.assertEqual(effects_count, 3)
