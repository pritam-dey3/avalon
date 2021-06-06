from unittest import TestCase, main
import unittest
from unittest.mock import patch, call

from avalon import Player, Game, get_id_name
from characters_and_quests import morgana, merlin


class SinglePlayerTest(TestCase):

    player = Player(name="Bob")
    player_list = [player] + [Player(id=i, name=str(i)) for i in range(1, 5)]

    def get_calls(self):
        players = get_id_name(self.player_list)
        player_id_msg = ""
        options = []
        for id, name in players:
            player_id_msg += str(id) + ":\t" + name + "\n"
            options.append(id)
        msg = "Select players for the quest..." + "\n" + player_id_msg
        calls = [call(f"Private message to {self.player.name}..."), call(msg)]

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

        calls += [call("You have to select 3 players for this quest.")]
        mocked_print.assert_has_calls(calls, any_order=True)

    @patch("builtins.input", return_value="gh\n")
    @patch(
        "builtins.print",
        side_effect=[None] * (2 + 2) + [Exception("To Break the Loop!")],
    )
    def test_select_players_for_quest_garbage_value(self, mocked_print, mocked_input):
        calls = self.get_calls()
        with self.assertRaises(Exception):
            self.player.select_players_for_quest(3, self.player_list)

        calls += [call("invalid literal for int() with base 10: 'gh'")]
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

        calls += [call("Invalid ids.")]
        mocked_print.assert_has_calls(calls, any_order=True)

    @patch("builtins.input", return_value="2 3 0\n")
    def test_select_players_for_quest_valid(self, mocked_input):
        result = self.player.select_players_for_quest(3, self.player_list)
        self.assertEqual(result, [2, 3, 0], "Wrong output for selected ids")

    def test_vote(self):
        self.player.set_character(morgana)
        self.assertEqual(
            self.player.voting_options,
            ["Approve", "approve", "A", "a", "Reject", "reject", "R", "r"],
            "Wrong voting options for Morgana",
        )


class GameTest(TestCase):
    game = Game([Player(id=i, name=str(i)) for i in range(5)])

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

            self.game = Game([Player(id=i, name=str(i)) for i in range(n + 1)])
        self.game = Game([Player(id=i, name=str(i)) for i in range(5)])


if __name__ == "__main__":
    main()