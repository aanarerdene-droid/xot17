# XOT17 admin prototype

Run the XOT17 local preview server from this folder:

```sh
python3 server.py
```

Then visit `http://localhost:8000`.

Open the admin dashboard at `http://localhost:8000/` and the customer app at `http://localhost:8000/rewards.html`. Both pages use the local request API; customer requests are saved in `data/support_requests.json` and the admin inbox refreshes every three seconds. Keep `server.py` running while using the request flow. Opening the HTML files directly bypasses the shared API. This local demo server only accepts connections from this computer; team-wide or phone access needs a deployed backend and access controls.

The deployment planner in `index.html` deliberately leaves branches unassigned until store-traffic data is supplied. Add reviewed recommendations to `data/deployment_plan.js`: high-footfall sites can be marked `rvm`, and lower-volume weekly-pickup sites can be marked `compactor`. The current location data contains branch listings, not visits, bottle volume, or verified machine placement. The ten numbered areas and audience descriptions from the team template are shown as proposed pilot candidates in `data/pilot_candidates.js`; they are not verified branch addresses or measured traffic rankings.

The CU, GS25, and MGL directory is generated from `cu_mongolia_642_branch_locations.csv`, `gs25_mongolia_branch_locations.csv`, `mglstore_food_organization_locations.csv`, and `data/store_locations.js`. The location map is drawn locally from supplied coordinates, so it works without external map tiles. CU and GS25 entries have coordinates; MGL has 535 address-only listings with Google Maps search links and cannot appear as map pins until coordinates are added. Machine placements, fill levels, bottle counts, rewards activity, and dashboard totals are illustrative prototype data; they are not live machine or user records.


For the colored Fusion model, insert `RVM25_reverse_vending_machine_color.3mf`. The older STL file is monochrome. See `RVM25_model_notes.md` for model and QR details.

## Bottle return simulation

Open `simulation.html` to play the illustrative QR pairing → bottle check → compaction → collection → demo points sequence. It is a scripted concept cutaway; the internal conveyor, sensor, and compactor are not physically modeled in the Fusion assembly.

## Player accounts and saved demo progress

Run `python3 server.py` and visit `http://localhost:8000/login` to register or sign in with email and password. The local server stores scrypt password hashes, accounts, and demo progress in `data/private/accounts.sqlite3`. This directory is blocked from the web server; do not publish or commit it. Set `XOT17_DB_PATH` to store the database elsewhere. New accounts start at zero; existing browser-only guest progress is kept separate and is not imported.

A stable secret is created automatically in `data/private/session.secret` (keep it private and back it up with the database). Alternatively, set a strong, persistent `AUTH_SECRET` environment variable before starting the server, for example `export AUTH_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"`. The server binds to loopback by default; cookies use HttpOnly and SameSite=Lax. `XOT17_SECURE_COOKIE=1` adds the Secure flag and should be used only behind properly configured HTTPS. The built-in server is for local use, not a production Internet deployment.

To enable the protected player directory, first register an account, stop the server, then run `python3 server.py --make-admin you@example.com` and restart the server with the same database path and secret. Sign in with that account and open `http://localhost:8000/users.html`. Registration cannot assign admin roles. The directory refreshes every 10 seconds.

Logged-in bottle insertions and completed embedded simulator cycles each save 10 **demo** points and one bottle, and demo reward redemptions deduct their fixed costs. Scan/connect alone does not credit points. The simulator and scanner are not connected to physical machine validation; these values must not be used as verified recycling records or real rewards. Requests and other existing admin pages remain prototype features and are not protected by this player directory's role check.

## Avatar and player card

After registration, the player opens the avatar editor; signed-in players can reopen it using their avatar in the header. Avatar choices are validated and saved to the account. Existing accounts receive the default avatar automatically when the server starts. The player card uses saved demo statistics and can be downloaded as PNG; sharing uses the browser's native share sheet where available, or copies a text summary and app URL when clipboard access is available. Browser sharing and clipboard APIs may require HTTPS or localhost.

## Open the app on a phone

Open the app through the server, never as a `file://` page. For local Wi-Fi testing on a trusted network, run `XOT17_HOST=0.0.0.0 python3 server.py`, find your computer's local IP address, and open `http://<computer-local-IP>:8000/rewards.html` on the phone. Keep the server running. The optional environment settings are shown in `.env.example`; export them in your shell, as the server does not automatically load `.env` files. `PORT` can override 8000.

This opt-in HTTP mode sends passwords and cookies without transport encryption and exposes the existing prototype admin and support pages on the network. Use only a trusted test network and test accounts. For a real deployment, use a production application server with HTTPS, `XOT17_SECURE_COOKIE=1`, a persistent database and secret, and access controls for all admin/support pages; the built-in preview server is not production-ready.
