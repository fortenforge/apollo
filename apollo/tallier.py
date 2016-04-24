from registrar import Registrar
from crypto import paillier

class Tallier:
    def __init__(self, registrar, election):
        self.registrar = registrar
        self.election = election
        self.vote_tally = 1
        self.tallied = False

    def send_vote(self, voter_id, vote):
        if self.registrar.confirm_vote(voter_id, vote):
            self.vote_tally = paillier.add(self.vote_tally, vote)
            return True
        return False

    def tally_votes(self):
        self.registrar.voting_complete()
        if not self.tallied:
            return self.vote_tally
        else:
            return -1
