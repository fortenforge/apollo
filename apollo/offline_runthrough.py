from client_registrar import ClientRegistrar
from client_tallier import ClientTallier
from election import Election
from voter import Voter
import entity_locations

import random
import pickle
import sys


if __name__ == '__main__':
    voter_ids = ['rsridhar', 'kevinzhu', 'vmohan', 'sunl', 'akshayr']
    candidates = ['bernie', 'shillary']

    NUM_VOTERS = len(voter_ids)
    NUM_CANDIDATES = len(candidates)
    FREQUENCY = 1


    r_endpoint = entity_locations.get_registrar_endpoint()
    r = ClientRegistrar(r_endpoint)
    eid = r.register_election(voter_ids, candidates)
    print("Got Election ID", eid)
    if eid == False:
        print("Could not get an election")
        sys.exit(0)

    e, tallier_endpoints = r.get_election(eid)

    print("Connected to Talliers:")
    for endpoint in tallier_endpoints:
        print(endpoint.hostname, str(endpoint.port))

    voters = [Voter(voter_ids[i], r, ClientTallier(tallier_endpoints[i%len(tallier_endpoints)]), e) for i in range(NUM_VOTERS)]
    expected_vote_totals = {candidates[i]:0 for i in range(NUM_CANDIDATES)}

    current_votes = 0
    for voter in voters:
        candidate = candidates[random.randint(0, NUM_CANDIDATES - 1)]
        expected_vote_totals[candidate] += 1

        voter.vote(candidate)
        if current_votes % FREQUENCY == 0:
            print("Completed Processing Vote:", current_votes)
        current_votes += 1

    r.end_election(eid)
    result = r.get_result(eid)
    real_vote_totals = e.decode_result(result)

    print('Expected: {}'.format(expected_vote_totals))
    print('Actual:   {}'.format(real_vote_totals))
    for i in range(NUM_CANDIDATES):
        assert expected_vote_totals[candidates[i]] == real_vote_totals[candidates[i]]

    print("Everything is going swimmingly")

