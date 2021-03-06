from client_tallier import ClientTallier
from client_registrar import ClientRegistrar
from client_authority import ClientAuthority
import entity_locations
from voter import Voter
import json

import random
import json
import sys
from hashlib import sha256
from string import ascii_lowercase
from flask import Flask, render_template, request, session, redirect
from flaskext.xmlrpc import XMLRPCHandler, Fault

app = Flask(__name__)

r_endpoint = entity_locations.get_registrar_endpoint()
r = ClientRegistrar(r_endpoint)
owner = 'kevinzhu'
voter_ids = ['rsridhar', 'kevinzhu', 'vmohan', 'sunl', 'akshayr']
candidates = ['clinton', 'sanders', 'trump']
eid = r.register_election(voter_ids, candidates, owner)
e, tallier_endpoints = r.get_election(eid)
config = None

@app.route('/api/submit_vote', methods=['POST'])
def submit_vote():
    message = 'Success!'
    try:
        t = ClientTallier(random.choice(tallier_endpoints))
        voter = Voter(session['username'], r, t, e)
        success = voter.vote(request.form['evote'], json.loads(request.form['proof']))
        if not success:
            message = "Something went wrong, please try again"

    except Exception:
        message = 'Something went wrong, please try again'

    return message

@app.route('/api/verify_election', methods=['POST'])
def verify_election():
    an, z =  r.verify_election(eid, int(request.form['e_chall']))
    arr = [str(an), str(z)]
    print("RETURN: ", arr)
    sys.stdout.flush()
    return json.JSONEncoder().encode(arr)

@app.route('/api/end_election', methods=['POST'])
def end_election():
    if session['username'] != owner:
        return 'You are not the election owner.'

    message = 'Success!'
    try:
        success = r.end_election(eid)
        if not success:
            message = 'Invalid Election ID'
    except ValueError:
        message = 'Election ID must be an integer'
    except Exception:
        message = 'Something went wrong, please try again'

    return message


@app.route('/login')
def login():
    # coming back from auth.php (we think)
    email = request.args['email']
    token = request.args['token']
    name = request.args['name']

    key = session['key']
    secret = config['authSecret']
    to_hash = (email + key + secret).encode('utf-8')
    correct_token = sha256(to_hash).hexdigest()

    if token == correct_token:
        message = 'Success!'
        session['username'] = email[:-len('@mit.edu')]
    else:
        message = 'Authentication Failed'

    return '<script>window.location.href = "../"</script>'


@app.route('/')
def hello_world():

    if 'username' in session:
        if not r.is_election_running(eid):
            results = json.JSONEncoder().encode(e.decode_result(r.get_result(eid)))
            result_msg = r.get_result(eid)
            election_votes = json.JSONEncoder().encode(list(map(str, r.get_election_votes(eid))))
            return render_template('demo_results.html', username = session['username'], results = results, election_votes = election_votes, result_msg = result_msg, pkg = e.pk.g, pkn = e.pk.n)
        else:
            owner_flag = (session['username'] == owner)
            
            return render_template('demo_interface.html', username = session['username'], owner = owner_flag, num_candidates = len(candidates), num_voters = len(voter_ids), pkg = e.pk.g, pkn = e.pk.n)
    else:
        authURL = config['authURL']
        key = ''.join(random.choice(ascii_lowercase) for i in range(10))
        linkURL = authURL + '?key=' + key
        session['key'] = key
        return redirect(linkURL)

@app.route('/about')
def about():
    return render_template('demo_about.html')

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    app.secret_key = config['cookieSecret']
    app.run(host="localhost", port=8192, debug=False)
