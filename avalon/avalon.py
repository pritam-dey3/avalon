from __future__ import annotations
import asyncio
from typing import Dict, List, Type, Literal

from random import shuffle


from avalon.characters_and_quests import quest_table
from avalon.interaction import FindMerlin, Inquisitor, SelectTeam, TeamVote, QuestVote
from avalon.player import Player, PlayerList


QuestRes = Literal["success", "failure", ""]


class Game:
    def __init__(self, players: PlayerList, inq: Type[Inquisitor]):
        self.players = players
        self.vote_track = 0
        self.quest_results: List[QuestRes] = ["" for _ in range(5)]
        self.result = ""
        self.n_players = len(self.players)
        self.quest_no = 0
        self.event_next_round = None
        self.abort_game = False
        self.inq = inq
        self.debug = False

    async def start(self, from_save=False):
        if not from_save:
            self.players.set_characters()
            self.reveal_characters()
        self.event_next_round = asyncio.Event()
        self.players.update_leader()
        await self.loop()
        await self.end()

    def reveal_characters(self):
        for player in self.players:
            player.reveal_characters(self.players)

    async def loop(self):
        while True:
            self.send_msg("Write `next_round` when you are ready")
            await self.wait_for_next_round()
            answers = await self.leader_selects().result()
            quest_members = answers[self.players.leader]
            # print(quest_members)
            await self.quest(quest_members)
            self.players.update_leader()
            if self.game_is_finished():
                break

    async def wait_for_next_round(self):
        await self.event_next_round.wait()
        self.event_next_round.clear()

    async def end(self):
        if self.result == "evil":
            self.send_msg(text="Minions of the Mordred wins!")
            return
        assassin = next(filter(lambda p: p.character.name == "assassin", self.players))
        assassins_choice = await self.inq({assassin: FindMerlin(self.players)}).result()
        merlin_found = assassins_choice[assassin][0] == "merlin"
        if merlin_found:
            self.send_msg(text="Minions of the Mordred wins!")
            return
        else:
            self.send_msg(text="The loyal servants of Arthur wins")
            return

    async def quest(self, members: List[Player]):
        quest_player_names = [player.name for player in members]
        self.send_msg(
            text=f"{self.players.leader.acc.name} has chosen the following players.\n"
            + ", ".join(quest_player_names)
        )

        # Team selection vote
        team_vote_result = await self.team_vote()
        if team_vote_result <= 0:
            self.vote_track += 1
            return

        # Quest vote
        fail_count = await self.quest_vote(members)

        if fail_count >= quest_table[self.quest_no][self.n_players - 5][1]:
            self.quest_results[self.quest_no] = "failure"
            self.send_msg(text="Quest failed.")
        else:
            self.quest_results[self.quest_no] = "success"
            self.send_msg(text="Successful quest!")

        # increment quest count
        self.quest_no += 1
        return

    def leader_selects(self) -> Inquisitor:
        """Ask the leader to select team for next quest

        Returns:
            Inquisitor: Returns inquisitor for this question. `.result()` will
            return leader's selections.
        """
        n_members = quest_table[self.quest_no][self.n_players - 5][0]
        leader = self.players.leader
        q = SelectTeam(options=self.players, n_members=n_members)
        return self.inq({leader: q})

    async def team_vote(self) -> int:
        votes = await self.inq({p: TeamVote() for p in self.players}).result()
        votes = [v[0] for v in votes.values()]
        return 2 * sum(votes) - self.n_players

    async def quest_vote(self, members: List[Player]) -> int:
        # quest_vote(members).result()
        votes = await self.inq({p: QuestVote(p) for p in members}).result()
        votes = [v[0] for v in votes.values()]
        shuffle(votes)
        votes_msg = ["Success" if vote else "Fail" for vote in votes]
        self.send_msg(text="Votes for this quest\n" + ", ".join(votes_msg))
        return len(members) - sum(votes)

    def game_is_finished(self):
        success_count = self.quest_results.count("success")
        failure_count = self.quest_results.count("failure")
        if self.abort_game:
            self.result = "game aborted."
            return True
        elif success_count >= 3:
            self.result = "good"
            return True
        elif failure_count >= 3:
            self.result = "evil"
            return True
        elif self.vote_track == 5:
            self.result = "evil"
            return True
        else:
            return False

    def send_msg(self, text: str = ""):
        print("Announcement...")
        print(text)

    def save(self):
        state = self.__dict__
        state.pop("next_round")
        return state

    @classmethod
    def load(self, state: Dict):
        g = self(players=PlayerList(), inq=None)
        g.__dict__.update(state)
        g.players.set_characters(silent=True)
        # g.next_round = asyncio.Event()
        return g
