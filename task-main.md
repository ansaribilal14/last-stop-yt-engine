# task-main.md — AHYEON EDITORIAL OVERHAUL (verbatim user directive, 2026-10-14)

> This file is the word-for-word task brief from the user. It is the master contract
> for this cycle. Every git issue traces back to sections of this file.

---

The video does not match with the audio .
.

 ,making sure you use character edge from https://github.com/ansaribilal14/character-clip-extractor

Smartness from other repos too that I shared throughout our conversation. Or learn things from https://github.com/ansaribilal14/opuscar-studio or from https://github.com/ansaribilal14/vfactory/
Earn only good things.


Also we need to use images too for places description of you say cheoncheon or such things or YG entertainment we need to see what's on screen instead of just randomly puting videos in line for images which you must use for places only part which is not related to the ahyeon (or whatever the documentary is about ) can get with the includeness of bilal140202/imgagent make it in the setup as a permenent agent for this rare typee of image retrieval.

Once you have the narration script ready

Assign a specialist agent which decides what should be the visual on each narration like a director who is plann6tge scenes. This should be a permanent agent on the system who knows what's up , research current GitHub projects you will find multiple projects to learn from which can power this system up


The background music the narration are great but the problem is in syncing.

One more problem I discovered is that you used mv videos just lining them up with the narration that's nota editor way of editing the clips should actually meet so again the director part is missing . Wasly here ,I am gonna say to again generate the same video but be better this time.


### 5\. Reference projects I would actually use for this engine

I inspected the current repository documentation for the following projects. My recommendation is to study their specific capabilities and reuse the existing FFmpeg architecture unless a tested component demonstrably improves it.

[OpenFilm](https://github.com/openfilm/openfilm) — best reference for the editor's visual decision output.

Study its agent-authored shots and editable timeline. It supports footage, pictures, and audio on tracks. Borrow the concept of generating a real edit that humans or agents can inspect; don't replace your engine until a compatibility test succeeds.

[Geneva](https://github.com/geneva-render/geneva) — investigate as an alternative execution layer.

Its JSON-document editing model, trimming, concatenation, and FFmpeg-based rendering make it worth benchmarking against your current Python/FFmpeg assembler. It is MIT-licensed.

[PySceneDetect](https://github.com/Breakthrough/PySceneDetect) — source-footage indexing.

Use it to detect shot boundaries and create candidate segments and contact sheets. The current README lists v0.7.2, released October 11, 2026.

[HyperFrames](https://github.com/heygen-com/hyperframes) — learn its persistent agent-skill conventions.

Its [`AGENTS.md`](https://github.com/heygen-com/hyperframes/blob/main/AGENTS.md) describes reusable skills and workflow routing. Its Node.js requirements also mean the coding agent should account for the engine's existing Python/FFmpeg environment before adding it.

[Motion Canvas](https://github.com/motion-canvas/motion-canvas) — designed explanatory visuals.

It specifically supports animations synchronized with voice-overs. Consider it for maps, timelines, and explanatory diagrams, not as a compulsory replacement for footage assembly.

[WhisperX](https://github.com/m-bain/whisperX) — timing fallback and verification.

Your engine already has Edge TTS word-boundary data, so preserve that as the primary timing source. Evaluate forced alignment for existing audio without valid timestamps or for timing discrepancies.

Two more resources are useful for study rather than wholesale adoption: [brag](https://github.com/latent-spaces/brag) for creative-direction and agent-skill patterns, and the [WhisperX documentation](https://github.com/m-bain/whisperX) for alignment workflows.

The key distinction: OpenFilm/Geneva help with edit execution; PySceneDetect helps find shots; the Director Agent must still decide which shots tell the story.

### 6\. Revised implementation directive for your actual repository

Use this in the coding-agent session that has access to `ansaribilal14/last-stop-yt-engine`. It supersedes the previous generic-engine prompt.

# LAST STOP YT ENGINE — AHYEON DOCUMENTARY EDITORIAL OVERHAUL

## Mission

Improve the existing documentary creator at:

https://github.com/ansaribilal14/last-stop-yt-engine/

The original Ahyeon documentary needs to be regenerated with better visual storytelling, contextual place imagery, meaningful shot selection, and narration-to-picture synchronization.

The current narration and background music are already good. Preserve them unless objective validation demonstrates a defect.

Do not create a separate video engine. Do not start by replacing FFmpeg, rewriting the pipeline, or installing a fleet of unrelated projects.

First map the real repository state, then implement the smallest robust architectural changes that solve the actual problems.

## 1. Start by recovering the real project state

Read these files first:

- `AGENTS.md`
- `HARDENED_RULES.md`
- `README.md`
- `docs/SYSTEM_LOOP.md`
- `memory/CURRENT_STATE.md`
- `memory/SESSION_HANDOFF.md`
- `pipeline/assemble.py`
- The current render workflow and actual QC implementation
- The existing Ahyeon project brief, source map, narration, word timings, clip index, timeline, asset manifest, and release artifacts

Verify all paths against the actual default branch. Do not assume that a documented file exists.

The public branch currently appears inconsistent: the README references `pipeline/build.py`, the workflow references `pipeline/render_final.py` and `pipeline/qc.py`, and the memory records an Ahyeon release that is not present under the expected `projects/ahyeon/` paths.

Locate the real runnable entry points and recover the exact source state of the original Ahyeon documentary before proceeding.

Compare the original release with the source clips, narration assets, and timeline that produced it. Identify the actual failure modes rather than guessing.

## 2. Change the zero-images rule narrowly

The current rules prohibit all still images in the timeline. Amend this policy to allow a controlled exception for researched contextual imagery.

New visual policy:

A. Primary documentary subject, such as Ahyeon:
Prioritize relevant, identifiable video footage using the existing downloader, source catalog, and character-clip-extractor. Do not replace subject footage with random photographs or generic footage.

B. Contextual locations and entities:
Use the permanent `Bilal140202/imgagent` specialist to retrieve relevant still images of places, buildings, studios, offices, venues, geographical locations, and other contextual subjects when appropriate.

C. Mixed scenes:
When the narration links Ahyeon to a place or event, combine relevant footage and contextual imagery deliberately.

D. Other contextual evidence:
For factual explanations, consider verified archival images, maps, documents, charts, or designed motion graphics when they help explain the story.

E. Unavailable assets:
Never silently substitute unrelated footage or imagery. Record the gap and use the best evidence-supported alternative.

Do not use a still image just because a place name occurs in a sentence. The image must add visual information that the narration requires.

Update `HARDENED_RULES.md`, `AGENTS.md`, the editorial documentation, relevant timeline schemas, and all affected QC assertions. Remove the global `image_segments == 0` restriction and replace it with explicit asset-class, routing, provenance, and relevance checks.

Preserve all unrelated hardened rules, particularly the restriction that YouTube source acquisition must not run on GitHub Actions.

## 3. Make imgagent a permanent agent

Inspect the current `Bilal140202/imgagent` repository and the existing agent runtime before deciding how to integrate it.

Make the contextual-image specialist reusable across documentary projects, available through a documented interface, and callable from the main orchestrator.

Its responsibilities:

- Resolve place names, aliases, transliterations, and geographical context.
- Determine exactly what the narration means before searching.
- Retrieve imagery that actually depicts the identified place or entity.
- Verify visual relevance using available visual inspection or metadata.
- Distinguish archival images from present-day images.
- Record source URL, publisher, retrieval date, attribution, usage rights, confidence, and SHA-256 where applicable.
- Deduplicate and cache reusable assets.
- Persist assets using the repository's existing storage conventions.
- Produce a visual preview/contact sheet for the Director.
- Reject unrelated, misidentified, misleading, or unverified assets.

For example, if a narration passage mentions Cheoncheon or YG Entertainment, research the intended place or entity and obtain imagery that actually shows the intended location. Do not simply select a random BABYMONSTER or BLACKPINK music video and label it contextual footage.

Ensure the image agent does not take over the primary-subject footage workflow.

## 4. Implement a permanent Documentary Director Agent

The missing component is a Director that makes editorial decisions before footage assembly.

Create a persistent specialist in the existing agent architecture. Define its role, tools, instructions, inputs, outputs, failure handling, and acceptance tests in Git.

The Director must be invoked after the narration audio and its timing data are finalized, but before final video assembly.

It must plan every scene and select every shot based on the story, not the order in which videos were downloaded.

Responsibilities include:

- Read and interpret the finalized script, its beats, the fact ledger, and the intended narrative arc.
- Assign each passage an editorial purpose and intended viewer takeaway.
- Decide what the audience should see at every point in the narration.
- Route each visual requirement to subject footage, contextual image retrieval, archival footage, maps, motion cards, explanatory graphics, or another appropriate visual type.
- Examine the actual available assets and their contents.
- Pick specific source clips and source in/out timecodes.
- Choose shot size, crop, framing, display duration, and motion treatment.
- Plan cuts, transitions, inserts, establishing shots, reaction shots, and visual continuity.
- Vary pacing according to narrative importance.
- Avoid repetitive shots, arbitrary zooms, unrelated footage, and decorative transitions that do not improve the scene.
- Replan whenever an appropriate shot cannot be found.
- Ensure every scene is factually and visually appropriate for its narration.

The Director decides. The Editor executes. A separate QA role checks the result.

Do not implement a Director that merely emits descriptions while leaving the current random clip-selection algorithm untouched.

## 5. Replace random clip assignment with shot-level editorial selection

Audit `pipeline/assemble.py`, especially `pool_for()`, `stage_plan()`, and `stage_segments()`.

The current implementation shuffles candidate pools, falls back to broader tag matches and primary-subject footage, then divides the allotted segment duration across a list of clips and concatenates them.

That behavior needs to be replaced by actual shot selection.

Create or improve the footage-indexing stage:

- Detect shot boundaries using the existing tools or evaluate PySceneDetect.
- Create shot-level metadata and contact sheets.
- Record each candidate shot's source asset, start time, end time, duration, subjects, location, actions, context, and provenance.
- Use semantic matching against the narration beat's visual intent.
- Use vision or embeddings only where the existing environment supports them economically and reliably.
- Preserve all provenance and subject-synchronization checks.

Do not assume that a video tagged `ygent` adequately illustrates a narration about the actual YG Entertainment building. Tags identify broad relevance; the Director must identify the content needed for the specific scene.

Implement an explicit edit decision list with source in/out points and destination timeline positions.

Each shot must be selected intentionally. Do not play arbitrary first seconds from a list of candidate clips. Do not reuse an entire music video as though it were one editorial shot.

Keep the existing subject tags and per-second synchronization assertions, but make sure that tag agreement is a minimum safety condition—not proof of semantic relevance.

Retain determinism and resumability. The same inputs should reproduce the same edit decisions unless the Director deliberately revises the plan.

## 6. Make synchronization narration-first

Preserve Edge TTS, its word-boundary JSON data, the existing captions workflow, and the currently working music-generation system.

Investigate the actual synchronization faults in the current pipeline.

Specific requirements:

- The finalized narration audio is the authoritative timing source.
- Preserve its word timestamps and actual spoken duration.
- Measure each narration beat's real duration.
- Avoid distributing a film-duration correction equally across every beat when doing so alters narration spacing.
- Derive shot positions from the actual beat timing and explicit director decisions.
- Support multiple shots within a single sentence and multiple sentences within a continuous shot.
- Place visual changes at meaningful narrative beats, pauses, actions, reveals, and emphasis points.
- Synchronize captions against actual spoken audio.
- Coordinate the score's act/beat cues, fades, transitions, and ducking with the finalized edit.
- Preserve music beneath speech at appropriate levels. Do not blindly snap every visual cut to a musical beat.
- Check for narration overlaps, clipped words, visual gaps, accidental freezes, and scene transitions that contradict the spoken content.

Inspect the existing `voice_at`, timeline-duration normalization, and clip-trimming behavior before changing code.

Do not replace the successful existing score with generic background music. Preserve the current soundtrack unless the synchronized edit reveals a specific, verified need to revise a cue.

## 7. Produce an inspectable Director-to-Editor contract

Introduce a scene plan in a structured format compatible with the existing codebase.

Each shot should have:

- Scene and shot identifiers.
- Narrative beat reference and editorial purpose.
- Narration start/end times and exact spoken text.
- Intended visual meaning.
- Asset type and selection reason.
- Asset ID, source URL/path, rights status, and provenance.
- Source in/out timecodes for video footage.
- Image display interval and motion treatment for still imagery.
- Destination timeline start/end positions.
- Subject tags and contextual entity tags.
- Framing, crop, and shot-size instructions.
- Transition and continuity instructions.
- Captions, text, map, or graphics requirements.
- Music and sound-effect cues.
- Fallback decisions.
- Validation status.

The plan must support multiple shots per narration beat, overlapping music tracks, intentional visual holds, and context imagery that overlaps or follows primary-subject footage.

Persist the machine-readable plan in Git and produce an inspectable storyboard/contact sheet. Follow existing project naming conventions instead of creating duplicate incompatible files.

Generate this plan before assembly and make the rendering stage consume it directly.

## 8. Research existing repositories before choosing new dependencies

Inspect these reference projects and their actual current source code, agent instructions, skills, examples, licenses, and requirements:

- OpenFilm: https://github.com/openfilm/openfilm
- HyperFrames: https://github.com/heygen-com/hyperframes
- Geneva: https://github.com/geneva-render/geneva
- Motion Canvas: https://github.com/motion-canvas/motion-canvas
- PySceneDetect: https://github.com/Breakthrough/PySceneDetect
- WhisperX: https://github.com/m-bain/whisperX
- brag: https://github.com/latent-spaces/brag
- Bilal140202/imgagent
- Bilal140202/ytagent

Prioritize:

1. Shot-level footage selection and semantic matching.
2. An actual editorial decision list rather than random concatenation.
3. A deterministic timeline representation.
4. Persistent Director instructions and agent skills.
5. Synchronization using the existing word-boundary data.
6. Contextual image search and provenance.
7. Independent output QA.

Evaluate Geneva as a potentially useful JSON-edit execution component, OpenFilm as a reference for agent-directed editable timelines, and PySceneDetect as a shot-indexing component.

Do not install or replace components simply because they are interesting. Benchmark integration cost, performance, license, dependency footprint, and compatibility with the existing runner.

Use WhisperX only if it adds meaningful capability beyond the current Edge TTS timing data.

## 9. Persistent agent instructions and skills

Inspect the existing agent runtime and its actual skill formats. Study HyperFrames' `AGENTS.md` and reusable skills, plus the applicable creative-direction patterns in brag.

Create or update the appropriate equivalents of:

- `AGENTS.md`
- `HARDENED_RULES.md`
- `docs/agents/DOCUMENTARY_DIRECTOR.md`
- `docs/agents/IMAGE_RETRIEVAL_AGENT.md`
- `docs/agents/EDITOR_AGENT.md`
- `docs/agents/AUDIO_SYNC_AGENT.md`
- `docs/agents/VIDEO_QA_AGENT.md`
- `skills/documentary-director/SKILL.md`
- `skills/contextual-image-retrieval/SKILL.md`
- `skills/editorial-assembly/SKILL.md`
- `skills/narration-synchronization/SKILL.md`
- `skills/documentary-quality-control/SKILL.md`
- `docs/research/VIDEO_SYSTEM_AUDIT.md`
- `docs/research/INTEGRATION_DECISIONS.md`

These are proposed logical paths, not permission to create duplicate or conflicting instructions.

If the existing runtime uses `.mx` skills or another native format, inspect its actual specification and follow it. Do not invent undocumented syntax.

Skills must describe trigger conditions, inputs, tools, procedures, outputs, validation, failure handling, and handoff to the next stage.

Make the Director and image-retrieval specialist available to subsequent documentary projects, not just this Ahyeon rerender.

## 10. Regression tests and actual video validation

Create a small representative test covering primary-subject footage, a place-specific contextual image, a mixed scene, and multiple shots supporting one narration passage.

Verify:

1. The scene plan is generated before assembly.
2. The Director selects actual source in/out timecodes.
3. Context images depict the places mentioned in narration.
4. Images are used only when the scene's visual purpose justifies them.
5. Subject footage remains relevant and correctly tagged.
6. The source clips are trimmed to meaningful shots, not arbitrary first seconds.
7. The narration does not drift because of timeline normalization.
8. Captions match the spoken words.
9. Background music remains synchronized and appropriately subordinate to speech.
10. No unrelated footage is silently inserted because an asset is missing.
11. All technical output specifications and existing release checks still pass.

Generate a storyboard and a short test render first. Inspect representative frames and audio at scene boundaries. Fix the defects before starting the full rerender.

Then regenerate the original Ahyeon documentary from the recovered source assets and finalized narration. Preserve the established duration and output specification unless the recovered project configuration explicitly says otherwise.

## 11. Git discipline and final reporting

Work in the existing repository and branch conventions.

- Preserve the current release and working code as recoverable states.
- Keep changes small, testable, and documented.
- Follow the repository's commit/push discipline and confirm actual push results when authorized.
- Never commit tokens or secrets.
- Store assets and generated artifacts using the current manifest/storage rules.
- Release a completed project independently; do not wait for unrelated projects.
- Do not mark a stage completed until it has been verified.

Report the concrete files changed, actual algorithmic changes, reference-repository findings, test results, render inspection results, any remaining blocker, and the resulting release location.

## Definition of success

The regenerated Ahyeon documentary must show Ahyeon when the narration is about Ahyeon, show the actual relevant place when the narration describes that place, and select meaningful shot sequences rather than randomly concatenating source clips.

The narration, captions, picture, music, and transitions must tell the same story at the same time.

The final product must be a deliberately edited documentary—not a playlist with a voice-over.

Begin by recovering the actual project state and inspecting the existing assembly implementation. Then execute the changes and rerender.





Inspect these five repositories and determine which capabilities can best improve my existing AI documentary video-production system. Implement the highest-value compatible improvements without breaking, replacing, or degrading the existing setup.

Repositories to audit

1. Geneva — https://github.com/geneva-render/geneva
2. OpenFilm — https://github.com/openfilm/openfilm
3. HyperFrames — https://github.com/heygen-com/hyperframes
4. Revideo — https://github.com/redotvideo/revideo
5. Motion Canvas — https://github.com/motion-canvas/motion-canvas

https://github.com/superz1402/promos.
edenfunf/reelmimic
https://github.com/edenfunf/reelmimic
ChatCut-Inc/agent-plugin
https://github.com/ChatCut-Inc/agent-plugin

https://github.com/Bilal140202/ttagent
https://github.com/Bilal140202/igagent
https://github.com/Bilal140202/xthread-agent
https://github.com/Bilal140202/ytagent
https://github.com/ansaribilal14/personal-social-agen

I expect better videos from you take your time ,mainly used the whole of the prompt I am give as a to do task devide it into multiple task and use git issues as your task todo setup one by one do everything,mainly keep this full as task-main.md same as word to word then start documentinh it into multiple task with detailed setup using git issues whichever I ls solved and implemented add it is issues resolved on git too.

Take your time and do your best 

And yeah you are allowed to delete the last release as per rules ,and work on the same topic a perfect narration maker director agent ,and a perfect director room.
