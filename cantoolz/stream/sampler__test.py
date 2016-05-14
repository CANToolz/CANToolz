import unittest

from cantoolz.stream.sampler import Sampler


class SamplerTest(unittest.TestCase):

    def testProcess(self):
        sampler = Sampler()
        sampler.bind(('1', ), lambda x: x)
        sampler.bind(('2',), lambda x: x)

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

    def testBind(self):
        sampler = Sampler()
        sampler.bind(('1', '2'), lambda x, y: (x, y))

        list(sampler('1'))
        list(sampler('2'))

        effects_count = 0

        for m in sampler():
            self.assertEqual(m, ('1', '2'))
            effects_count += 1

        self.assertEqual(effects_count, 1)