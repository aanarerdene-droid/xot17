# Loopwise admin prototype

Open `index.html` in a browser, or serve this folder locally with:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

The customer rewards app prototype is available at `http://localhost:8000/rewards.html` (or open `rewards.html` directly). The operations dashboard sidebar also links to the user app preview.

The CU, GS25, and MGL directory is generated from `cu_mongolia_642_branch_locations.csv`, `gs25_mongolia_branch_locations.csv`, `mglstore_food_organization_locations.csv`, and `data/store_locations.js`. The location map is drawn locally from supplied coordinates, so it works without external map tiles. CU and GS25 entries have coordinates; MGL has 535 address-only listings with Google Maps search links and cannot appear as map pins until coordinates are added. Machine placements, fill levels, bottle counts, rewards activity, and dashboard totals are illustrative prototype data; they are not live machine or user records.
