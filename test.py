from unittest import TestCase, main
import unittest
from unittest.mock import patch, call

from avalon.avalon import Player, Game, Message
from avalon.characters_and_quests import morgana, merlin


class SinglePlayerTest(TestCase):
    def setUp(self):
        msg = Message()
        self.player = Player(msg, id=0, name="Bob")
        self.player_list = [self.player] + [Player(msg, id=i, name=str(i)) for i in range(1, 5)]
        self.game = Game(self.player_list, msg)

    def get_calls(self):
        player_id_msg = ""
        options = []
        for option, player in enumerate(self.player_list):
            player_id_msg += str(option + 1) + ":\t" + player.name + "\n"
            options.append(id)
        msg = "Select players for the quest...(3)"
        calls = [call(f"Private message to {self.player.name}..."), call(msg), call(player_id_msg)]

        return calls

    @patch("builtins.input", return_value="\n")
    @patch(
        "builtins.print",
        side_effect=[None] * (2 + 2) + [Exception("To Break the Loop!")],
    )
    def test_select_players_for_quest_no_value(self, mocked_print, mocked_input):
        calls = self.get_calls()
        with self.assertRaises(Exception):
            self.player.select_players_for_quest(3, self.player_list)

        calls += [call('You have to enter 3 valid answers separated by spaces.')]
        mocked_print.assert_has_calls(calls, any_order=True)

    @patch("builtins.input", return_value="gh 3 2\n")
    @patch(
        "builtins.print",
        side_effect=[None] * (2 + 2) + [Exception("To Break the Loop!")],
    )
    def test_select_players_for_quest_garbage_value(self, mocked_print, mocked_input):
        calls = self.get_calls()
        with self.assertRaises(Exception):
            self.player.select_players_for_quest(3, self.player_list)

        calls += [call('Incorrect entries.')]
        mocked_print.assert_has_calls(calls, any_order=True)

    @patch("builtins.input", return_value="2 5 0\n")
    @patch(
        "builtins.print",
        side_effect=[None] * (2 + 2) + [Exception("To Break the Loop!")],
    )
    def test_select_players_for_quest_invalid_id(self, mocked_print, mocked_input):
        calls = self.get_calls()
        with self.assertRaises(Exception):
            self.player.select_players_for_quest(3, self.player_list)

        calls += [call("Incorrect entries.")]
        mocked_print.assert_has_calls(calls, any_order=True)

    @patch("builtins.input", return_value="2 3 1\n")
    def test_select_players_for_quest_valid(self, mocked_input):
        result = self.player.select_players_for_quest(3, self.player_list)
        expected = [self.player_list[i] for i in [1,2,0]]
        self.assertEqual(result, expected, "Wrong output for selected ids")

    


class GameTest(TestCase):
    def setUp(self):
        self.msg = Message()
        self.player_list = [Player(self.msg, id=i, name=str(i)) for i in range(5)]
        self.game = Game(self.player_list, self.msg)

    def test_player_distribution(self):
        player_distribution = {
            5: (3, 2),
            6: (4, 2),
            7: (4, 3),
            8: (5, 3),
            9: (6, 3),
            10: (6, 4),
        }
        for n in range(5, 10):
            self.game.assign_characters()
            player_types = [player.type for player in self.game.players]
            player_characters = [player.character for player in self.game.players]

            self.assertEqual(
                player_characters.count("merlin"), 1, "merlin count is not 1"
            )
            self.assertEqual(
                player_characters.count("percival"), 1, "percival count is not 1"
            )
            self.assertTrue("loyal_servant" in player_characters, "no loyal_servants")
            self.assertEqual(
                player_characters.count("assassin"), 1, "assassin count is not 1"
            )
            self.assertEqual(
                player_characters.count("morgana"), 1, "morgana count is not 1"
            )
            if n > 6:
                self.assertTrue(
                    ("minion" in player_characters) or ("oberon" in player_characters),
                    f"no minions or oberons for {n} players",
                )

            good_count = player_types.count("good")
            self.assertEqual(
                good_count,
                player_distribution[n][0],
                f"For {n} players, good player count is not {player_distribution[n][0]}",
            )

            self.game = Game([Player(self.msg, id=i, name=str(i)) for i in range(n + 1)], self.msg)
        self.game = Game([Player(self.msg, id=i, name=str(i)) for i in range(5)], self.msg)


if __name__ == "__main__":
    main()