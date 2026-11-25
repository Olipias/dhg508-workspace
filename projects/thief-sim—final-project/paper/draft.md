# Playing with Uncertain Provenance
## Evidence Boundaries, Deterministic Rehearsal, and the Design of Thief Simulator

**DHG508 Final Design Paper & Post-Mortem · 25 November 2026**

### Abstract

*Thief Simulator* is a Chinese-language 2D stealth and investigation game built in Godot 4.7 for desktop. You examine museum objects whose identifications are secure while their ownership histories are not, rehearse heist routes in a deterministic simulation, and decide whether to hand a relic to a demon contract or to a national receiver. Every claim carries a label: documented fact (据), scholarly inference (推断), or design invention (设). This paper describes the build and what testing exposed.

## 1. Historical Question and Medium

A museum label can pin down an object while leaving its movement between owners blank. The game asks what a player can conclude when records fix an artifact's form and acquisition date but say nothing about how it left its place of origin. A heist needs a target in a display case; provenance research meets missing transfers and unverified rumors. Both pressures stay visible.

The audience is Chinese-reading players who like short stealth games. You answer four questions about a relic: how it looks, where it came from, how it entered a collection, and which gallery holds it tonight. One answer leaves the rest open. Casting seams identify a Shang bronze; they do not explain its route out of China before the 1930s.

Interactivity turns that distinction into a task. After a six-panel comic and a tutorial heist, you enter a walkable safehouse. At the computer you search catalog numbers, drag source cards into an evidence frame, and pick the claim they support. The phone and door stay locked until you verify one relic's features and exhibition zone. In the museum you scout rooms, lift ordinary loot, and leave without the main relic.

## 2. Sources and Scholarly Conversation

The investigation rests on three real antiquities. The Metropolitan Museum of Art catalogs heart scarab `10.130.1650` as a Late Period (664--332 BCE) dark green stone amulet given in 1910.[^met] That record confirms material and arrival in New York, not an excavation or an export from Egypt. UNESCO lists painted askos `VM-GR-25-012` from the West House at Akrotiri as a Late Cycladic I (1650--1615 BCE) vessel, with no theft date and no current location.[^unesco] The *West House* card tests whether players separate an ancient building from the museum's modern west wing.

Adam Chapman argues that historical games carry meaning through rules and the actions they ask of players, not through text alone.[^chapman] An early build let one button connect clue cards. His argument named the problem, since accurate prose does nothing when the player performs no analysis. I rebuilt the computer board (`investigation_board.gd`) around manual work: confirming the double-ram *zun* takes two cards and a chosen relation between its twin-ram body and pre-cast horns.

Jeremiah McCall treats historical simulations as problem spaces, where goals, resources, and affordances organize what a player can do.[^mccall] That framing exposed a conflict between stealth rewards and historical care. Price every artifact and the economy teaches players to treat antiquities as cargo. I split objects in `game_state.gd` into two classes: ordinary loot passes through a box, a phone reservation, and a front-door sale, while the three principal relics reach only the demon or national-receiver endings.

Quanyu Wang and Sascha Priewe supply the technical basis for British Museum double-ram *zun* `1936,1118.1`. Their metallurgical study shows horns cast separately and locked onto the body, and links the vessel's style to a southern bronze tradition in the middle Yangtze region.[^wang] They record a 1930s Eumorfopoulos entry with no known findspot. The museum's catalog page returned HTTP 403 in November 2026, so I worked from their text and our earlier log, and removed an unverified 1860 looting rumor from `story.gd`.

## 3. Architecture and Boundaries

The game runs at 640 by 360 on Godot 4.7, exporting through `tools/export.sh`. The controller in `src/main.gd` moves between the comic, the tutorial gallery, the safehouse (`safehouse.gd`), and the museum (`museum.gd`). Four stations organize the routine: computer, storage box, phone, and door.

Figure 1 traces data from sources through the controller, saves, simulation, and tests. Fact IDs (`C-001` to `C-003`) live in `investigation.gd` and `story.gd`, apart from `user://save.json`. On a retry, `GameState` keeps discovery (`story_flags`) separate from the physical snapshot, so detection rewinds position and spent items while uncovered rooms stay uncovered.

Rehearsal and execution share one fixed-tick kernel (`sim_preview.gd`, 20 ticks per second). Tab or R freezes player, patrols, cameras, and noise decay together through `_sync_world_freeze`. The kernel simulates a copy of the room for predicted paths and warnings, then Space runs the plan through the same tick function.

Documented history stops at 1936 for the *zun*, 1910 for the scarab, and the Bronze Age eruption at Akrotiri. Contemporary elements are invention: three relics in one museum, exhibition slips, guard routes, and the demon. Citations sit in the title declaration while the board enforces the limits.

## 4. Evidence Table

Table 1 maps seven claims and mechanics from `paper/evidence.csv`, generated by `make_evidence_table.py`. Labels attach to single claims: Wang and Priewe support an observation on page 266 and an attribution on page 273.

## 5. Verification and Playtesting

`tools/verify.sh --visual` runs 25 stages. Build `v0.26.16` passed all 25 and 56 visual comparisons on 25 November 2026.

1. **Logic and history:** `test_logic.gd` (2,552 assertions) and `test_history.py` (11) hold the four evidence tiers and reject the 1860 rumor.
2. **Simulation:** `test_sim_preview.gd` and `test_museum_sim.gd` (133) compare rehearsal and execution tick by tick and confirm a rewind restores coordinates without touching the wallet.
3. **Input and layout:** `test_input_flow.gd` and `test_dialogue_paging.gd` (563) drive key and mouse events through search, dragging, departure gates, and pagination at 640 by 360.
4. **Economy and saves:** `test_safehouse_loop.gd` (33) runs loot through delivery and purchase; `test_save_compat.gd` (135) covers damaged saves.

Playtesting caught four defects unit tests missed: guards frozen while the player moved during takeover (`v0.23.3`), a board with no next step (`v0.26.14`), one contact introduction reused for six people (`v0.26.13`), and labels overflowing the dialogue box (`v0.26.15`). Each fix carries a regression test.

## 6. Post-Mortem

**What worked.** Fact IDs kept dialogue honest, since `test_history.py` catches sentences that turn an inference into a findspot. Separating stock (`smoke_stock`) from carried gear (`smoke_count`) closed a duplication path during rewinds.

**What failed.** Early tests compared the shared prefix of two traces and polled once per frame, so preview ticks that ran past the route's end went unnoticed. `v0.26.9` stops rehearsal at the final waypoint and emits per-tick signals. UI tests that called `open()` and `close()` directly hid input bleed-through; real `InputEvent` dispatches exposed it.

**What changed.** I cut the artifact-spirit dialogues (`v0.20.0`), dropped the closing countdown (`v0.21.4`), limited fog to the minimap (`v0.26.12`), and replaced the three-chain requirement with one verified target.

**Where the build falls short.** This release is a working prototype, not the game I set out to make. Most rooms still carry placeholder pixel art, the dialogue reads as a draft script rather than finished writing, and audio stops at procedurally generated cues with no music or mixing pass. Development halted when the AI tooling budget ran out, which froze the build at this state. The systems, the evidence boundaries, and the tests hold up under review; the presentation does not yet.

**Limits and AI assistance.** Automated suites and the Linux boot pass on `v0.26.16`; Windows and macOS host testing and a player study remain open. I designed the mechanics, set the historical boundaries, wrote the paper, and verified every citation myself. AI tools assisted with implementation: OpenCode, Codex, and Claude Code for GDScript debugging and test scaffolding, Tencent Hunyuan3D for sprite rendering, and `stop-slop` with `Humanizer-zh` for English style.

[^met]: Metropolitan Museum of Art, “Heart Scarab,” object 10.130.1650, “Artwork Details,” accessed November 25, 2026, https://www.metmuseum.org/art/collection/search/548226.
[^unesco]: UNESCO, “Askos with Painted Decoration,” VM-GR-25-012, “About the Object,” accessed November 25, 2026, https://museum.unesco.org/stolen-objects/VM-GR-25-012_Askos_with_painted_decoration/.
[^chapman]: Adam Chapman, “Privileging Form Over Content: Analysing Historical Videogames,” Journal of Digital Humanities 1, no. 2 (Spring 2012), opening discussion, https://journalofdigitalhumanities.org/1-2/privileging-form-over-content-by-adam-chapman/.
[^mccall]: Jeremiah McCall, “Historical Simulations as Problem Spaces: Criticism and Classroom Use,” Journal of Digital Humanities 1, no. 2 (Spring 2012), part I, https://journalofdigitalhumanities.org/1-2/historical-simulations-as-problem-spaces-by-jeremiah-mccall/.
[^wang]: Quanyu Wang and Sascha Priewe, “A Technical Study of the Double-ram Zun Ancient Chinese Bronze Vessel in the British Museum,” in Radiance between Bronze and Jade: Archaeology, Art, and Culture of the Shang and Zhou Dynasties, ed. Kwang-tzuu Chen (Taipei: Institute of History and Philology, Academia Sinica, 2013), 257–58, 266, 273.
