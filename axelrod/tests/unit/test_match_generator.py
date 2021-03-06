import unittest

from hypothesis import given, example
from hypothesis.strategies import floats, integers

import axelrod
from axelrod.match_generator import graph_is_connected


test_strategies = [axelrod.Cooperator, axelrod.TitForTat, axelrod.Defector,
                   axelrod.Grudger, axelrod.GoByMajority]
test_turns = 100
test_repetitions = 20
test_game = axelrod.Game()


class TestMatchGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.players = [s() for s in test_strategies]

    def test_build_single_match_params(self):
        rr = axelrod.MatchGenerator(players=self.players,
                                    turns=test_turns,
                                    game=test_game,
                                    repetitions=test_repetitions)
        match_params = rr.build_single_match_params()
        self.assertIsInstance(match_params, dict)
        self.assertEqual(match_params["turns"], test_turns)
        self.assertEqual(match_params["game"], test_game)
        self.assertEqual(match_params["noise"], 0)
        self.assertIsNone(match_params["prob_end"])

        # Check that can build a match
        players = [axelrod.Cooperator(), axelrod.Defector()]
        match_params["players"] = players
        match = axelrod.Match(**match_params)
        self.assertIsInstance(match, axelrod.Match)
        self.assertEqual(len(match), test_turns)

    def test_build_single_match_params_with_noise(self):
        rr = axelrod.MatchGenerator(players=self.players,
                                    turns=test_turns,
                                    game=test_game,
                                    repetitions=test_repetitions,
                                    noise=0.5)
        match_params = rr.build_single_match_params()
        self.assertIsInstance(match_params, dict)
        self.assertEqual(match_params["turns"], test_turns)
        self.assertEqual(match_params["game"], test_game)
        self.assertEqual(match_params["noise"], .5)
        self.assertIsNone(match_params["prob_end"])

        # Check that can build a match
        players = [axelrod.Cooperator(), axelrod.Defector()]
        match_params["players"] = players
        match = axelrod.Match(**match_params)
        self.assertIsInstance(match, axelrod.Match)
        self.assertEqual(len(match), test_turns)

    def test_build_single_match_params_with_prob_end(self):
        rr = axelrod.MatchGenerator(players=self.players,
                                    game=test_game,
                                    repetitions=test_repetitions,
                                    prob_end=0.5)
        match_params = rr.build_single_match_params()
        self.assertIsInstance(match_params, dict)
        self.assertIsNone(match_params["turns"])
        self.assertEqual(match_params["game"], test_game)
        self.assertEqual(match_params["noise"], 0)
        self.assertEqual(match_params["prob_end"], 0.5)

        # Check that can build a match
        players = [axelrod.Cooperator(), axelrod.Defector()]
        match_params["players"] = players
        match = axelrod.Match(**match_params)
        self.assertIsInstance(match, axelrod.Match)
        with self.assertRaises(TypeError):
            len(match)

    def test_build_single_match_params_with_prob_end_and_noise(self):
        rr = axelrod.MatchGenerator(players=self.players,
                                    game=test_game,
                                    repetitions=test_repetitions,
                                    noise=0.5,
                                    prob_end=0.5)
        match_params = rr.build_single_match_params()
        self.assertIsInstance(match_params, dict)
        self.assertIsNone(match_params["turns"])
        self.assertEqual(match_params["game"], rr.game)
        self.assertEqual(match_params["prob_end"], .5)
        self.assertEqual(match_params["noise"], .5)

        # Check that can build a match
        players = [axelrod.Cooperator(), axelrod.Defector()]
        match_params["players"] = players
        match = axelrod.Match(**match_params)
        self.assertIsInstance(match, axelrod.Match)
        with self.assertRaises(TypeError):
            len(match)

    def test_build_single_match_params_with_prob_end_and_turns(self):
        rr = axelrod.MatchGenerator(players=self.players,
                                    game=test_game,
                                    repetitions=test_repetitions,
                                    turns=5,
                                    prob_end=0.5)
        match_params = rr.build_single_match_params()
        self.assertIsInstance(match_params, dict)
        self.assertEqual(match_params["turns"], 5)
        self.assertEqual(match_params["game"], test_game)
        self.assertEqual(match_params["prob_end"], .5)
        self.assertEqual(match_params["noise"], 0)

        # Check that can build a match
        players = [axelrod.Cooperator(), axelrod.Defector()]
        match_params["players"] = players
        match = axelrod.Match(**match_params)
        self.assertIsInstance(match, axelrod.Match)
        self.assertIsInstance(len(match), int)
        self.assertGreater(len(match), 0)
        self.assertLessEqual(len(match), 10)

    @given(repetitions=integers(min_value=1, max_value=test_repetitions))
    @example(repetitions=test_repetitions)
    def test_build_match_chunks(self, repetitions):
        rr = axelrod.MatchGenerator(players=self.players,
                                    turns=test_turns,
                                    game=test_game,
                                    repetitions=repetitions)
        chunks = list(rr.build_match_chunks())
        match_definitions = [tuple(list(index_pair) + [repetitions])
                             for (index_pair, match_params, repetitions) in chunks]
        expected_match_definitions = [(i, j, repetitions) for i in range(5)
                                      for j in range(i, 5)]

        self.assertEqual(sorted(match_definitions),
                         sorted(expected_match_definitions))

    @given(repetitions=integers(min_value=1, max_value=test_repetitions))
    @example(repetitions=test_repetitions)
    def test_spatial_build_match_chunks(self, repetitions):
        cycle = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 1)]
        rr = axelrod.MatchGenerator(players=self.players,
                                    turns=test_turns,
                                    game=test_game,
                                    edges=cycle,
                                    repetitions=repetitions)
        chunks = list(rr.build_match_chunks())
        match_definitions = [tuple(list(index_pair) + [repetitions])
                             for (index_pair, match_params, repetitions) in chunks]
        expected_match_definitions = [(i, j, repetitions) for i, j in cycle]

        self.assertEqual(sorted(match_definitions),
                         sorted(expected_match_definitions))

    def test_len(self):
        turns = 5
        repetitions = 10
        rr = axelrod.MatchGenerator(players=self.players,
                                    turns=test_turns,
                                    game=test_game,
                                    repetitions=test_repetitions)
        self.assertEqual(len(rr), len(list(rr.build_match_chunks())))

    def test_init_with_graph_edges_not_including_all_players(self):
        edges = [(0, 1), (1, 2)]
        with self.assertRaises(ValueError):
            axelrod.MatchGenerator(players=self.players,
                                   repetitions=3, game=test_game,
                                   turns=5, edges=edges, noise=0)


class TestUtilityFunctions(unittest.TestCase):
    def test_connected_graph(self):
        edges = [(0, 0), (0, 1), (1, 1)]
        players = ["Cooperator", "Defector"]
        self.assertTrue(graph_is_connected(edges, players))

    def test_unconnected_graph(self):
        edges = [(0, 0), (0, 1), (1, 1)]
        players = ["Cooperator", "Defector", "Alternator"]
        self.assertFalse(graph_is_connected(edges, players))
