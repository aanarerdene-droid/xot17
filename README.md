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
