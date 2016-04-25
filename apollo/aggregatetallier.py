from clienttallier import ClientTallier
from clientregistrar import ClientRegistrar 
from crypto import paillier
import entitylocations

import pickle
from flask import Flask
from flaskext.xmlrpc import XMLRPCHandler, Fault


class AggregateTallier:
    def __init__(self):
        self.elections = {}

    # coming from registrar
    def register_talliers(self, election_id, tallier_endpoints, registrar_endpoint, pk):
        self.elections[election_id] = (tallier_endpoints, registrar_endpoint, pk)
        return True

    # coming from authority
    def compute_aggregate_tally(self, election_id):
        if election_id not in self.elections:
            return False
        total = 1
        tallier_endpoints, registrar_endpoint, pk = self.elections[election_id]
        print(tallier_endpoints)
        for endpoint in tallier_endpoints:
            t = ClientTallier(endpoint)
            local_tally = t.tally_votes(election_id)
            if (local_tally):
                total = paillier.add(pk, local_tally, total)

        r = ClientRegistrar(registrar_endpoint)
        r.voting_complete()
        # May want to delete entries from table
        return total

app = Flask(__name__)
handler = XMLRPCHandler('api')
handler.connect(app, '/api')
endpoint = entitylocations.get_authority_endpoint()
at = AggregateTallier()

@handler.register
def register_talliers(req):
    args = pickle.loads(req.data)
    return pickle.dumps(at.register_talliers(args['election_id'], args['tallier_endpoints'], args['registrar_endpoint'], args['pk']))

@handler.register
def compute_aggregate_tally(req):
    args = pickle.loads(req.data)
    return pickle.dumps(at.compute_aggregate_tally(args['election_id']))

if __name__ == '__main__':
    endpoint = entitylocations.get_aggregate_tallier_endpoint()
    app.run(host=endpoint.hostname, port=endpoint.port, debug=False)

